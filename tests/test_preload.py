from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gluon import preload


class PreloadTests(unittest.TestCase):
    def test_on_play_read_ahead_is_bounded_and_can_be_disabled(self):
        with tempfile.TemporaryDirectory() as temporary:
            installation = Path(temporary)
            game = installation / "Game.exe"
            app_source = installation / "resources/app.asar"
            app_source.parent.mkdir()
            app_source.touch()
            with patch.object(preload.sys, "platform", "darwin"), \
                 patch.dict("os.environ", {"GLUON_LAUNCH_PREFETCH": "1"}), \
                 patch.object(preload, "_advise", side_effect=lambda path, limit: limit) as advise:
                preload.warm_for_launch(str(game))
                self.assertEqual(advise.call_args_list[0].args, (game, 64 << 20))
                self.assertEqual(advise.call_args_list[1].args, (app_source, 32 << 20))
                self.assertEqual(advise.call_count, 2)
                preload.warm_for_launch(r"C:\Games\Game.exe")
                with patch.dict("os.environ", {"GLUON_LAUNCH_PREFETCH": "0"}):
                    preload.warm_for_launch(str(game))
                self.assertEqual(advise.call_count, 2)

    def test_game_read_ahead_caps_chromium_files_and_skips_linked_resources(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            (home / "steamplay").mkdir()
            (home / "steamplay/preload-wine").write_text("1\n")
            game = home / "game"
            game.mkdir()
            exe = game / "game.exe"
            other = home / "other"
            other.mkdir()
            (other / "app.asar").touch()
            (game / "resources").symlink_to(other)
            (game / "chrome_100_percent.pak").touch()
            calls = []

            def read_ahead(path, limit):
                calls.append((path.relative_to(game).as_posix(), limit))
                return 32 * 1024 * 1024 if path.name == "icudtl.dat" else 0

            with patch("gluon.preload._advise", side_effect=read_ahead):
                preload._warm_game(home, exe)
            self.assertEqual(calls[:2], [("game.exe", 256 * 1024 * 1024),
                                         ("icudtl.dat", 48 * 1024 * 1024)])
            self.assertEqual(calls[2][1], 16 * 1024 * 1024)
            self.assertNotIn("resources/app.asar", dict(calls))

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
