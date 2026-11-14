"""Run an installed legacy Mac app with the separately installed mac32 runner."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


def invoke(operation: str, target: str, runner: str | None = None) -> int:
    app = Path(target).expanduser().resolve(strict=True)
    if not app.is_file() and not (app.is_dir() and app.suffix.lower() == ".app"):
        raise ValueError("Choose a Mac application bundle or a Mach-O executable.")
    if runner:
        executable = Path(runner).expanduser().resolve(strict=True)
    else:
        command = shutil.which("mac32")
        candidates = [
            Path(command) if command else None,
            Path.home() / ".local/bin/mac32",
            Path("/Applications/Mac32.app/Contents/MacOS/mac32"),
        ]
        executable = next((path for path in candidates
                           if path and path.is_file() and os.access(path, os.X_OK)), None)
    if not executable or not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError("Install mac32, then pass its executable with --runner. See docs/STEAM-SETTINGS.md.")
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith(("DYLD_", "STEAM_DYLD_"))}
    return subprocess.run([str(executable), operation, str(app)], env=environment).returncode
