"""Warm the packaged Wine runtime ahead of Play in an isolated directory."""
from __future__ import annotations

import fcntl
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile

from . import steam


def _advise(path, limit):
    """Ask Darwin to read ahead without copying the file into Python."""
    if sys.platform != "darwin":
        return
    try:
        with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as file:
            info = os.fstat(file.fileno())
            if stat.S_ISREG(info.st_mode) and info.st_size:
                # macOS sys/fcntl.h: F_RDADVISE, struct radvisory { off_t, int }.
                fcntl.fcntl(file.fileno(), 44, struct.pack("@qi4x", 0, min(info.st_size, limit)))
    except OSError:
        pass


def _recent_game(home):
    try:
        latest = max((home / "logs").glob("launch-*.log"), key=lambda item: item.stat().st_mtime)
        with os.fdopen(os.open(latest, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as log:
            info = os.fstat(log.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
                return None
            log.seek(max(0, info.st_size - 16384))
            lines = log.read(16384).decode(errors="replace").splitlines()
        for line in reversed(lines):
            _, found, name = line.partition("   program   = ")
            if not found:
                continue
            candidate = Path(name)
            if not candidate.is_absolute() or candidate.suffix.lower() != ".exe":
                return None
            candidate = candidate.resolve(strict=True)
            for root in {steam.STEAM_ROOT, *steam.library_dirs()}:
                common = (Path(root) / "steamapps/common").resolve()
                if candidate.is_relative_to(common):
                    return candidate
            return None
    except (OSError, ValueError):
        return None


def enabled(home: Path) -> bool:
    try:
        path = home / "steamplay/preload-wine"
        with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as file:
            info = os.fstat(file.fileno())
            return stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and file.read(3) == b"1\n"
    except OSError:
        return False


def warm(home: Path) -> None:
    if not enabled(home):
        return
    try:
        os.nice(10)
        runtime = (home / "runtime/current").resolve(strict=True)
        if runtime.parent != (home / "runtime").resolve() or not runtime.name.startswith("gluon-runtime-"):
            return
        wine, server = runtime / "bin/wine", runtime / "bin/wineserver"
        if not all(os.access(path, os.X_OK) for path in (wine, server)):
            return
        # An opt-in request and a Steam startup can coincide. Never run two
        # warmups, and never take a lock needed by a game or the installer.
        lock = home / "steamplay/preload.lock"
        fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            recent = _recent_game(home)
            if recent and enabled(home):
                _advise(recent, 64 * 1024 * 1024)
            for relative in ("bin/wine", "bin/wineserver", "lib/wine/x86_64-unix/wine",
                             "lib/wine/x86_64-unix/ntdll.so", "lib/wine/x86_64-windows/ntdll.dll",
                             "lib/wine/i386-windows/ntdll.dll"):
                if not enabled(home):
                    return
                _advise(runtime / relative, 4 * 1024 * 1024)
            if not enabled(home):
                return
            with tempfile.TemporaryDirectory(prefix="gluon-warm-", dir=home / "steamplay") as prefix:
                # Execute both startup binaries so Rosetta can translate them.
                # Version queries exit without booting or keeping any prefix alive.
                loader = runtime / "lib/wine/x86_64-unix/wine"
                for executable in (loader if os.access(loader, os.X_OK) else wine, server):
                    if not enabled(home):
                        return
                    subprocess.run([str(executable), "--version"], timeout=4, check=False,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,
                                   env={"HOME": str(Path.home()), "PATH": "/usr/bin:/bin",
                                        "WINEDLLPATH": str(runtime / "lib/wine"),
                                        "WINEPREFIX": prefix, "ROSETTA_ADVERTISE_AVX": "1"})
        finally:
            os.close(fd)
    except (OSError, subprocess.SubprocessError):
        # Optional acceleration must never require repair or block launch.
        pass
