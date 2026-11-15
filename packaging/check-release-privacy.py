#!/usr/bin/env python3
"""Check expanded release payloads and source archives for private material."""
import argparse
import base64
import hashlib
import mmap
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tarfile


CREDENTIALS = {
    "GitHub token": ((b"ghp_", b"gho_", b"ghu_", b"ghs_", b"ghr_", b"github_pat_"),
                     rb"(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{70,255})"),
    "OpenAI key": ((b"sk-proj-", b"sk-svcacct-"), rb"sk-(?:proj-|svcacct-)[A-Za-z0-9_-]{32,255}"),
    "AWS key ID": ((b"AKIA", b"ASIA"), rb"(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])"),
    "Google API key": ((b"AIza",), rb"AIza[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])"),
    "Slack token": ((b"xox",), rb"xox[baprs]-[0-9]+-[0-9]+-[A-Za-z0-9-]{12,255}"),
    "Stripe live secret": ((b"sk_live_", b"rk_live_"), rb"(?:sk|rk)_live_[A-Za-z0-9]{24,255}"),
    "URL credentials": ((b"http",), rb"https?://[A-Za-z0-9_.%+-]{1,100}:[A-Za-z0-9_+%=.-]{6,200}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
}
PEM_KEY = re.compile(
    rb"-----BEGIN ([A-Z ]{0,16}PRIVATE KEY)-----\r?\n"
    rb"((?:[A-Za-z0-9+/=]{8,100}\r?\n){1,128})-----END \1-----"
)
# Public vectors from the pinned GnuTLS 3.8.13 release,
# lib/crypto-selftests-pk.c. Match decoded bytes and only in this dependency.
GNUTLS_SELF_TESTS = {
    "0294b4406902e33bb02f89eaf4c691328790d7a9cd01b873d68edac994f310a1",
    "09f1c1a4680df80b9e8e6e587d3a787de7402a919e366426ad807a1c0f8c98c1",
    "2859ff03b44c8f0e4f96604b8cced325ef4d01ca935422b2041d88d8809f8fa1",
    "323a1e2a6917c0615aa5e0144ba9ea0b18553c671284f2b75ca5dde1308c477b",
    "458022ddcb5598b39253bc027eb02c4f3dba00e2bdbaef239a35bc91c9bd4f3a",
    "803fc9d7eb40ea13dc82723b2d99780ac1e0335ba0b65d660e66994c613ed422",
    "87e288dc7dbc29a24241b596ec8c84f949d9f09f34fc0cf69242481fb2274770",
    "d245e52c341a76645e1b0e56c58dc964cd4f3ecaea64a9c6d6db9897d4948a8a",
}
PRIVATE_NAMES = {
    ".netrc", ".npmrc", ".pypirc", "id_rsa", "id_ed25519", "credentials.json",
    "loginusers.vdf", "localconfig.vdf", "config.vdf", "appinfo.vdf", "ssfn",
}
PRIVATE_DIRS = {".git", ".ssh", ".aws", "__pycache__"}


class Audit:
    def __init__(self, private_markers):
        self.patterns = {name: (needles, re.compile(pattern)) for name, (needles, pattern) in CREDENTIALS.items()}
        self.markers = [value.encode() for value in private_markers]
        self.files = 0
        self.findings = set()

    def names(self, name):
        parts = PurePosixPath(name).parts
        leaf = parts[-1].lower() if parts else ""
        if (PRIVATE_DIRS.intersection(parts) or leaf in PRIVATE_NAMES or
                leaf.startswith((".env", "ssfn")) or leaf.endswith((".p12", ".pfx"))):
            self.findings.add((name, "private filename"))

    def data(self, name, content):
        self.files += 1
        for label, (needles, pattern) in self.patterns.items():
            if any(content.find(needle) >= 0 for needle in needles) and pattern.search(content):
                self.findings.add((name, label))
        if content.find(b"-----BEGIN ") >= 0:
            for match in PEM_KEY.finditer(content):
                key = base64.b64decode(b"".join(match[2].split()))
                digest = hashlib.sha256(key).hexdigest()
                if not (name.endswith("/lib/libgnutls.30.dylib") and digest in GNUTLS_SELF_TESTS):
                    self.findings.add((name, "private key"))
        if any(content.find(marker) >= 0 for marker in self.markers):
            self.findings.add((name, "developer identifier"))

    def directory(self, root):
        for directory, dirs, files in os.walk(root, followlinks=False):
            for leaf in dirs + files:
                path = Path(directory) / leaf
                name = path.relative_to(root).as_posix()
                self.names(name)
                info = path.lstat()
                if path.is_symlink():
                    self.data(name, os.readlink(path).encode())
                elif stat.S_ISREG(info.st_mode) and info.st_size:
                    with path.open("rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
                        self.data(name, data)

    def archive(self, path):
        with tarfile.open(path, "r|*") as archive:
            for entry in archive:
                self.names(entry.name)
                if entry.issym() or entry.islnk():
                    self.data(entry.name, entry.linkname.encode())
                elif entry.isfile() and entry.size:
                    with archive.extractfile(entry) as file:
                        # Include binaries and preserve matches across chunk boundaries.
                        tail = b""
                        while True:
                            block = file.read(4 * 1024 * 1024)
                            if not block:
                                break
                            self.data(entry.name, tail + block)
                            tail = block[-16384:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="+")
    parser.add_argument("--private-marker", action="append", default=[])
    args = parser.parse_args()
    audit = Audit(filter(None, args.private_marker))
    for path in args.paths:
        if path.is_dir():
            audit.directory(path)
        else:
            audit.archive(path)
    for name, finding in sorted(audit.findings):
        print(f"{finding}: {name}", file=sys.stderr)
    print(f"Release privacy scan checked {audit.files} files or archive blocks.")
    return 1 if audit.findings or not audit.files else 0


if __name__ == "__main__":
    sys.exit(main())
