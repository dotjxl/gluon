import hashlib
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gluon import steam, steamplay, updates


class UpdateTests(unittest.TestCase):
    def test_latest_stable_release_requires_the_official_asset_and_digest(self):
        release = updates.Release("0.5", 4, "a" * 64)
        asset = {"name": "Gluon-0.5.pkg", "state": "uploaded", "size": release.size,
                 "digest": "sha256:" + release.digest, "browser_download_url": release.url}
        metadata = {"tag_name": "v0.5", "draft": False, "prerelease": False, "assets": [asset]}

        def fetch(installed):
            with patch.object(updates, "build_opener") as opener:
                opener.return_value.open.return_value = BytesIO(json.dumps(metadata).encode())
                return updates._latest(installed)

        self.assertEqual(fetch("0.5-rc.1"), release)
        self.assertIsNone(fetch("0.5.0"))
        self.assertIsNone(fetch("0.6"))
        metadata["prerelease"] = True
        self.assertIsNone(fetch("0.4.3"))
        metadata["prerelease"] = False
        asset["browser_download_url"] = "https://example.org/update.pkg"
        with self.assertRaisesRegex(updates.UpdateError, "Unexpected location"):
            fetch("0.4.3")

    def test_opt_in_queues_verified_download_until_steam_quits(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            for directory in ("steamplay", "runtime"):
                (home / directory).mkdir()
            steamplay._write_json(home / "runtime/pending.json", {
                "schema": 1, "name": "previous", "version": "0.5-rc.1",
            })
            preference = home / "steamplay/automatic-updates"
            payload = b"release"
            release = updates.Release("0.5", len(payload), hashlib.sha256(payload).hexdigest())
            with patch.object(steam, "GLUON_HOME", str(home)), patch.object(updates.os, "getuid", return_value=home.stat().st_uid or 501), \
                 patch.object(updates, "_latest", return_value=release) as latest, \
                 patch.object(updates, "build_opener") as opener, \
                 patch.object(steamplay.Installation, "idle") as idle, patch.object(updates, "_install", return_value=True) as install:
                self.assertEqual(updates.poll(), [])
                latest.assert_not_called()
                preference.write_bytes(b"1\n")
                # CI runs as a normal account. On a root test host, stub the preference itself.
                with patch.object(updates, "_enabled", side_effect=lambda _: preference.read_bytes() == b"1\n"):
                    opener.return_value.open.return_value = BytesIO(payload)
                    idle.side_effect = steamplay.SteamPlayError("busy")
                    self.assertIn("after Steam and Wine quit", updates.poll()[0])
                    install.assert_not_called()
                    preference.write_bytes(b"0\n")
                    idle.side_effect = None
                    self.assertEqual(updates.poll(), [])
                    install.assert_not_called()
                    preference.write_bytes(b"1\n")
                    self.assertEqual(updates.poll(), ["Updated Gluon to 0.5."])
                    install.assert_called_once()
                    latest.assert_called_once()

    def test_bad_digest_cannot_enter_the_install_queue(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            package = home / "latest.pkg"
            release = updates.Release("0.5", 3, "a" * 64)
            with patch.object(updates, "_enabled", return_value=True), patch.object(updates, "build_opener") as opener:
                opener.return_value.open.return_value = BytesIO(b"bad")
                with self.assertRaisesRegex(updates.UpdateError, "SHA-256"):
                    updates._download(home, release, package)
            self.assertFalse(package.exists())
