"""Copy the system package's staged payload into the logged-in user's Gluon home.

The privileged package script drops privileges before invoking this module.
No user-owned path or script is processed as root. Runtime versions are immutable;
installation requires Steam/Wine idle, and existing prefixes are never copied.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import time
import uuid

from . import runtime, steam, steamplay


STEAM_PROCESSES = "steam_osx|steamwebhelper|Steam Helper"
WINE_PROCESS = "wineserver"


def _running(pattern, *, own_user=False):
    command = ["/usr/bin/pgrep", "-x"]
    if own_user:
        command.extend(["-u", str(os.getuid())])
    result = subprocess.run([*command, pattern], capture_output=True, timeout=3)
    if result.returncode not in (0, 1):
        raise steamplay.SteamPlayError("Could not check whether Steam or Wine is running.")
    return result.returncode == 0


def _request_wine_quit(home):
    """Send ordinary macOS Quit requests to Wine apps and Gluon's game launcher."""
    script = '''
ObjC.import("AppKit");
function run(argv) {
    var launcher = argv[0];
    var apps = $.NSWorkspace.sharedWorkspace.runningApplications;
    for (var i = 0; i < apps.count; ++i) {
        var app = apps.objectAtIndex(i);
        var identifier = ObjC.unwrap(app.bundleIdentifier) || "";
        var url = app.executableURL;
        var executable = url.isNil() ? "" : ObjC.unwrap(url.path);
        if (identifier === "org.winehq.wine" || identifier === "com.codeweavers.CrossOver" ||
            identifier.indexOf("org.gluon.game.") === 0 || executable === launcher) {
            app.terminate;
        }
    }
}
'''
    subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", "-e", script,
                    str(home / "bin/gluon-launcher-host")], capture_output=True, timeout=4)


def _quit_running_apps(installation):
    steam_open = _running(STEAM_PROCESSES)
    wine_open = _running(WINE_PROCESS)
    if not (steam_open or wine_open):
        return

    if steam_open and _running("steam_osx", own_user=True):
        client = Path(steam.CLIENT_DIR) / "steam_osx"
        if client.is_file():
            try:
                subprocess.run([str(client), "-shutdown"], capture_output=True, timeout=4)
            except (OSError, subprocess.TimeoutExpired):
                pass  # Report what is still running after the wait.

    if wine_open and _running(WINE_PROCESS, own_user=True):
        try:
            _request_wine_quit(installation.home)
        except (OSError, subprocess.TimeoutExpired):
            pass

    deadline = time.monotonic() + 15
    while True:
        steam_open = _running(STEAM_PROCESSES)
        wine_open = _running(WINE_PROCESS)
        if not (steam_open or wine_open):
            return
        if time.monotonic() >= deadline:
            break
        time.sleep(0.5)

    if steam_open and wine_open:
        reason = "Steam and Wine are still running. Quit Steam and close any Windows games, then retry the installer."
    elif steam_open:
        reason = "Steam is still running. Choose Steam > Quit Steam, then retry the installer."
    else:
        reason = "Wine is still running. Close any Windows games or Wine apps, then retry the installer."
    raise steamplay.SteamPlayError(reason)


def deploy(source, *, quit_apps=False, update_version=None):
    if os.geteuid() == 0:
        raise steamplay.SteamPlayError('Gluon user setup must not run as root')
    with steamplay.Installation().lock('package.lock'):
        return _deploy(source, quit_apps=quit_apps, update_version=update_version)


def _stage(source, home, directories):
    home.mkdir(parents=True, exist_ok=True)
    for relative in directories:
        src, dst = source / relative, home / relative
        if not src.is_dir() or src.is_symlink():
            raise steamplay.SteamPlayError('missing staged package directory: ' + relative)
        if dst.exists():
            if steamplay._tree(src) != steamplay._tree(dst):
                raise steamplay.SteamPlayError('existing version differs from package; use a newer package: ' + str(dst))
            continue
        temporary = dst.with_name('.staging-' + dst.name)
        if temporary.exists():
            shutil.rmtree(temporary)
        temporary.parent.mkdir(parents=True, exist_ok=True)
        try:
            steamplay.System().copy(src, temporary)
            if steamplay._tree(src) != steamplay._tree(temporary):
                raise steamplay.SteamPlayError('staged copy failed verification: ' + relative)
            os.rename(temporary, dst)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)


def _deploy(source, *, quit_apps=False, update_version=None):
    source = Path(source).resolve(strict=True)
    home = Path(steam.GLUON_HOME)
    installation = steamplay.Installation()
    request = runtime._request(source / 'runtime/pending.json')
    pending = steamplay._json(source / 'steamplay/pending.json')
    name = pending.get('name')
    if (request is None or not isinstance(name, str) or name in ('', '.', '..')
            or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for c in name)):
        raise steamplay.SteamPlayError('invalid staged package request')
    directories = ('runtime/' + request['name'], 'steamplay/payloads/' + name)
    if update_version is not None:
        if request["version"] != update_version:
            raise steamplay.SteamPlayError("The update package version does not match its release tag.")
        return _apply_update(source, installation, directories, request)
    if quit_apps:
        _quit_running_apps(installation)
    installation.idle()
    subprocess.run(['/bin/launchctl', 'bootout', 'gui/%d/com.gluon.agent' % os.getuid()], capture_output=True)
    _stage(source, home, directories)
    # Scripts and Python modules are small; copy while all native sessions are idle.
    for directory in ('bin', 'lib'):
        steamplay.System().copy(source / directory, home / directory)
    for retired in ('enable.py', 'metadata.py'):
        (home / 'lib/gluon' / retired).unlink(missing_ok=True)
    for relative in ('runtime/pending.json', 'steamplay/pending.json'):
        steamplay._atomic(home / relative, (source / relative).read_bytes())
    # Use the just-installed code. The environment is set by the privileged wrapper
    # to this account's HOME; no privileged interpreter imports from the home folder.
    result = subprocess.run(['/usr/bin/arch', '-arm64', '/usr/bin/python3', '-m', 'gluon', 'install'],
                            env=dict(os.environ, PYTHONPATH=str(home / 'lib')), capture_output=True, text=True)
    logs = home / 'logs'
    logs.mkdir(mode=0o700, exist_ok=True)
    if not logs.is_symlink() and logs.stat().st_uid == os.getuid():
        logs.chmod(0o700)
    (logs / 'install.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise steamplay.SteamPlayError('Steam Play setup failed: ' + result.stderr.strip() + '\nSee ' + str(logs / 'install.log'))
    print(result.stdout, end='')
    agents = Path.home() / 'Library/LaunchAgents'
    agents.mkdir(parents=True, exist_ok=True)
    plist = agents / 'com.gluon.agent.plist'
    steamplay._atomic(plist, plistlib.dumps({'Label': 'com.gluon.agent',
        'ProgramArguments': [str(home / 'bin/gluon-agent')], 'RunAtLoad': True,
        'StartInterval': 60, 'ProcessType': 'Background', 'StandardErrorPath': str(logs / 'agent-stderr.log')}))
    subprocess.run(['/bin/launchctl', 'bootstrap', 'gui/%d' % os.getuid(), str(plist)], check=True)


def _apply_update(source, installation, directories, request):
    from .updates import _enabled, _version

    home = installation.home
    installed = runtime._request(home / "runtime/pending.json")
    if not installed or _version(request["version"]) <= _version(installed["version"]):
        raise steamplay.SteamPlayError("Gluon has already installed this version or a newer one.")
    apps = installation.receipt()["apps"]
    if len(apps) != 1:
        raise steamplay.SteamPlayError("Automatic updates require an existing Gluon Steam installation.")
    installation.idle()
    _stage(source, home, directories)
    candidate = steamplay.Installation(home)
    candidate.payload = home / directories[1]
    candidate.payload_check()

    selections = ("runtime/pending.json", "steamplay/pending.json")
    previous = {name: (home / name).read_bytes() for name in selections}
    current = home / "runtime/current"
    old_runtime = runtime._current(current)
    save = home / "backups" / ("update-" + uuid.uuid4().hex)
    save.mkdir(mode=0o700, parents=True)
    moved = []
    try:
        for directory in ("bin", "lib"):
            if not (home / directory).is_dir() or (home / directory).is_symlink() or (source / directory).is_symlink():
                raise steamplay.SteamPlayError("Invalid Gluon " + directory + " directory.")
            shutil.copytree(home / directory, save / (directory + "-new"), symlinks=True)
            steamplay.System().copy(source / directory, save / (directory + "-new"))
        if not _enabled(home):
            raise steamplay.SteamPlayError("Automatic updates were turned off.")
        installation.idle()
        for directory in ("bin", "lib"):
            os.rename(home / directory, save / directory)
            moved.append(directory)
            os.rename(save / (directory + "-new"), home / directory)
        for name in selections:
            steamplay._atomic(home / name, (source / name).read_bytes())
        runtime.activate_pending(home=str(home))
        if runtime._current(current) != request["name"]:
            raise steamplay.SteamPlayError("Steam or Wine reopened before the update could finish.")
        candidate.install(next(iter(apps)))
    except Exception:
        for directory in reversed(moved):
            if (home / directory).exists():
                os.rename(home / directory, save / (directory + "-failed"))
            os.rename(save / directory, home / directory)
        if moved:
            for name, contents in previous.items():
                steamplay._atomic(home / name, contents)
            if runtime._current(current) == request["name"]:
                if old_runtime is None:
                    current.unlink()
                elif old_runtime != request["name"]:
                    temporary = current.with_name(".rollback-" + save.name)
                    temporary.symlink_to(old_runtime)
                    os.replace(temporary, current)
        shutil.rmtree(save, ignore_errors=True)
        raise
    else:
        shutil.rmtree(save, ignore_errors=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--quit-apps', action='store_true')
    args = parser.parse_args()
    try:
        deploy(args.source, quit_apps=args.quit_apps)
    except (steamplay.SteamPlayError, runtime.RuntimeSelectionError, steam.SteamError,
            OSError, ValueError, subprocess.SubprocessError) as error:
        print('gluon: ' + str(error), file=sys.stderr)
        sys.exit(1)
