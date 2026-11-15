"""Check and install official releases using Gluon's existing per-user agent."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from . import package_install, runtime, steam, steamplay


REPOSITORY = "dotjxl/gluon"
LATEST = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
DOWNLOAD_HOSTS = {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}
CHECK_INTERVAL = 6 * 60 * 60
RETRY_INTERVAL = 60 * 60
MAX_PACKAGE = 2 << 30
VERSION = re.compile(r"(0|[1-9][0-9]{0,4})\.(0|[1-9][0-9]{0,4})(?:\.(0|[1-9][0-9]{0,4}))?(-[0-9A-Za-z.-]{1,64})?")


class UpdateError(RuntimeError):
    pass


def _version(value):
    match = VERSION.fullmatch(value) if isinstance(value, str) else None
    if not match:
        raise UpdateError("Unrecognized Gluon version")
    major, minor, patch, prerelease = match.groups()
    return int(major), int(minor), int(patch or 0), prerelease is None


@dataclass(frozen=True)
class Release:
    version: str
    size: int
    digest: str

    @property
    def url(self):
        return f"https://github.com/{REPOSITORY}/releases/download/v{self.version}/Gluon-{self.version}.pkg"

    def validate(self):
        if not _version(self.version)[-1] or type(self.size) is not int or not 0 < self.size <= MAX_PACKAGE:
            raise UpdateError("Invalid Gluon release package")
        if not isinstance(self.digest, str) or not re.fullmatch(r"[0-9a-f]{64}", self.digest):
            raise UpdateError("Missing GitHub SHA-256 for the Gluon release package")
        return self


class _DownloadRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urlsplit(newurl)
        if url.scheme != "https" or url.netloc not in DOWNLOAD_HOSTS:
            raise UpdateError("Unexpected GitHub release download server")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _latest(installed):
    request = Request(LATEST, headers={"Accept": "application/vnd.github+json", "User-Agent": "Gluon"})
    try:
        with build_opener(_DownloadRedirect()).open(request, timeout=20) as response:
            data = json.loads(response.read(1024 * 1024))
    except HTTPError as error:
        if error.code == 404:  # GitHub returns this until the first stable release.
            error.close()
            return None
        raise
    if not isinstance(data, dict) or data.get("draft") is not False or data.get("prerelease") is not False:
        return None
    tag = data.get("tag_name")
    if not isinstance(tag, str) or not tag.startswith("v"):
        raise UpdateError("Unexpected Gluon release tag")
    version = tag[1:]
    if _version(version) <= _version(installed) or not _version(version)[-1]:
        return None
    assets = data.get("assets", [])
    if not isinstance(assets, list):
        raise UpdateError("Invalid GitHub release assets")
    matches = [asset for asset in assets if isinstance(asset, dict)
               and asset.get("name") == f"Gluon-{version}.pkg" and asset.get("state") == "uploaded"]
    if len(matches) != 1:
        raise UpdateError(f"Gluon {version} has no unique installer")
    asset = matches[0]
    digest = asset.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise UpdateError(f"Gluon {version} has no GitHub SHA-256")
    release = Release(version, asset.get("size"), digest.removeprefix("sha256:")).validate()
    if asset.get("browser_download_url") != release.url:
        raise UpdateError("Unexpected location for the Gluon release package")
    return release


def _enabled(home):
    try:
        fd = os.open(home / "steamplay/automatic-updates", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as file:
            info = os.fstat(file.fileno())
            return stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and file.read(3) == b"1\n"
    except OSError:
        return False


def _download(home, release, path):
    if shutil.disk_usage(path.parent).free < release.size * 5:
        raise UpdateError("Not enough free space to stage the Gluon update")
    request = Request(release.url, headers={"User-Agent": "Gluon"})
    digest, received = hashlib.sha256(), 0
    deadline = time.monotonic() + 15 * 60
    with tempfile.TemporaryDirectory(prefix=".download-", dir=path.parent) as temporary:
        part = Path(temporary) / "update.pkg"
        with build_opener(_DownloadRedirect()).open(request, timeout=25) as response, part.open("xb") as output:
            while block := response.read(1024 * 1024):
                received += len(block)
                if received > release.size or time.monotonic() > deadline or not _enabled(home):
                    raise UpdateError("Gluon update download stopped")
                output.write(block)
                digest.update(block)
        if received != release.size or digest.hexdigest() != release.digest:
            raise UpdateError("Gluon update did not match the published SHA-256 and size")
        os.replace(part, path)


def _install(home, package, release, installation):
    if package.stat().st_size != release.size or steamplay._digest(package) != release.digest:
        package.unlink()
        raise UpdateError("Staged Gluon update did not match the published SHA-256 and size")
    with tempfile.TemporaryDirectory(prefix=".unpack-", dir=package.parent) as temporary:
        expanded = Path(temporary) / "expanded"
        # Extract files only. A background update never runs package scripts or sudo.
        steamplay._run("/usr/sbin/pkgutil", "--expand-full", package, expanded)
        source = expanded / "gluon-component.pkg/Payload/Library/Application Support/Gluon"
        if not _enabled(home):
            return False
        installation.idle()
        package_install.deploy(source, update_version=release.version)
        return True


def poll():
    """Do one update check from launchd. Return log messages, never interrupt Steam."""
    home = Path(steam.GLUON_HOME).resolve()
    if os.getuid() == 0 or not _enabled(home):
        return []
    installation = steamplay.Installation(home)
    with installation.lock("updates.lock"):
        if not _enabled(home):
            return []
        installed = runtime._request(home / "runtime/pending.json")
        if not installed:
            return []
        folder = home / "updates"
        folder.mkdir(mode=0o700, exist_ok=True)
        info = folder.stat()
        if folder.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise UpdateError("The Gluon update folder is not private to this account")
        cache, package = folder / "state.json", folder / "latest.pkg"
        state = steamplay._json(cache) if cache.exists() else {}
        now = int(time.time())
        messages = []
        if now >= state.get("check_after", 0):
            state["check_after"] = now + RETRY_INTERVAL
            steamplay._write_json(cache, state)
            try:
                release = _latest(installed["version"])
                previous = state.get("release")
                if release is not None and (previous != asdict(release) or not package.is_file()):
                    _download(home, release, package)
                    messages.append(f"Downloaded Gluon {release.version}. It will install after Steam and Wine quit.")
                elif release is None:
                    package.unlink(missing_ok=True)
                state["release"] = asdict(release) if release is not None else None
                state["check_after"] = now + CHECK_INTERVAL
                steamplay._write_json(cache, state)
            except (UpdateError, OSError, ValueError, URLError) as error:
                return [f"Could not check for a Gluon update: {error}"]
        if not state.get("release") or now < state.get("install_after", 0) or not package.is_file():
            return messages
        release = Release(**state["release"]).validate()
        if _version(release.version) <= _version(installed["version"]):
            package.unlink(missing_ok=True)
            return messages
        try:
            installation.idle()
        except (steamplay.SteamPlayError, steam.SteamError, runtime.RuntimeSelectionError):
            return messages
        if not _enabled(home):
            return messages
        try:
            if _install(home, package, release, installation):
                package.unlink()
                messages.append(f"Updated Gluon to {release.version}.")
        except (UpdateError, steamplay.SteamPlayError, runtime.RuntimeSelectionError, steam.SteamError,
                OSError, ValueError, subprocess.SubprocessError) as error:
            state["install_after"] = now + RETRY_INTERVAL
            steamplay._write_json(cache, state)
            messages.append(f"Could not install Gluon {release.version}: {error}")
        return messages
