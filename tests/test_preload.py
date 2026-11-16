from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gluon import preload


class PreloadTests(unittest.TestCase):
    def test_opt_in_uses_only_the_packaged_wine_and_a_disposable_prefix(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary).resolve()
            settings = home / "steamplay"
            settings.mkdir()
            runtime = home / "runtime/gluon-runtime-fixture"
            (runtime / "bin").mkdir(parents=True)
            (runtime.parent / "current").symlink_to(runtime)
            for name in ("wine", "wineserver"):
                executable = runtime / "bin" / name
                executable.touch()
                executable.chmod(0o700)
            game_prefix = home / "compatdata/123/pfx-wine"
            game_prefix.mkdir(parents=True)

            runs = []

            def check(args, **kwargs):
                prefix = Path(kwargs["env"]["WINEPREFIX"])
                self.assertTrue(prefix.is_dir())
                self.assertEqual(prefix.parent, settings)
                self.assertFalse(any(key.startswith(("DYLD_", "STEAM_")) for key in kwargs["env"]))
                self.assertEqual(args, [str(runtime / "bin" / ("wine" if not runs else "wineserver")), "--version"])
                self.assertLessEqual(kwargs["timeout"], 4)
                runs.append(prefix)

            with patch("gluon.preload.os.nice"), patch("gluon.preload.subprocess.run", side_effect=check):
                preload.warm(home)
                self.assertEqual(runs, [])
                (settings / "preload-wine").write_text("1\n")
                preload.warm(home)
                self.assertEqual(len(runs), 2)
                self.assertFalse(runs[0].exists())
                self.assertEqual(list(game_prefix.iterdir()), [])
