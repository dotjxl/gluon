"""Warm the packaged Wine runtime ahead of Play in an isolated directory."""
from __future__ import annotations

import fcntl
import os
from pathlib import Path
import stat
import subprocess
import tempfile


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
            for relative in ("bin/wine", "bin/wineserver", "lib/wine/x86_64-unix/wine",
                             "lib/wine/x86_64-unix/ntdll.so", "lib/wine/x86_64-windows/ntdll.dll",
                             "lib/wine/i386-windows/ntdll.dll"):
                if not enabled(home):
                    return
                try:
                    with (runtime / relative).open("rb", buffering=0) as file:
                        # Read the startup binaries only. Avoid walking the runtime
                        # or competing with Steam's catalogue and game downloads.
                        file.read(4 * 1024 * 1024)
                except OSError:
                    pass
            if not enabled(home):
                return
            with tempfile.TemporaryDirectory(prefix="gluon-warm-", dir=home / "steamplay") as prefix:
                subprocess.run([str(server), "-f", "-p2"], timeout=4, check=False,
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               env={"HOME": str(Path.home()), "PATH": "/usr/bin:/bin",
                                    "WINEPREFIX": prefix, "ROSETTA_ADVERTISE_AVX": "1"})
        finally:
            os.close(fd)
    except (OSError, subprocess.SubprocessError):
        # Optional acceleration must never require repair or block launch.
        pass
