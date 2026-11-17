#!/bin/bash
# Recover the ABI-identical Steam bridge from a published, pinned Gluon package.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
destination="${1:-$root/build/inputs}"
mkdir -p "$destination"
temporary="$(mktemp -d)"
trap 'rm -rf "$temporary"' EXIT
package="$root/build/downloads/Gluon-0.4.2.pkg"
digest=4097db39f711b21ab9bebb560f12b8b74eb681f451fa43a29ca68c3962ff65fd
mkdir -p "${package%/*}"
if ! printf '%s  %s\n' "$digest" "$package" | shasum -a 256 -c - >/dev/null 2>&1; then
    curl -fL --connect-timeout 15 --max-time 180 --retry 2 \
        https://github.com/dotjxl/gluon/releases/download/v0.4.2/Gluon-0.4.2.pkg \
        -o "$temporary/bridge-source.pkg"
    printf '%s  %s\n' "$digest" "$temporary/bridge-source.pkg" | shasum -a 256 -c -
    mv "$temporary/bridge-source.pkg" "$package"
fi
pkgutil --expand-full "$package" "$temporary/expanded"
python3 - "$temporary/expanded" "$destination" <<'PY'
import hashlib
from pathlib import Path
import sys
import tarfile

expanded, output = map(Path, sys.argv[1:])
runtimes = expanded / 'gluon-component.pkg/Payload/Library/Application Support/Gluon/runtime'
runtime, = runtimes.glob('gluon-runtime-*')
files = {
    'lib/wine/x86_64-unix/lsteamclient.so': 'ae6ae4dbf999d1dd2a7364fc389c4ffe403152e5f3152905c4ab7bd4a02c677f',
    'lib/wine/x86_64-windows/lsteamclient.dll': 'e7d4e1411e9fa92f968602ac2c89c1a83a02f7f618f92f41507c2031917ef874',
    'lib/wine/i386-windows/lsteamclient.dll': 'a754dd85e05246849f21245e1804fe86716d78cd0476b4ec66a377b9ebde6ad6',
}
for name, expected in files.items():
    if hashlib.sha256((runtime / name).read_bytes()).hexdigest() != expected:
        raise SystemExit('Published Steam bridge does not match its recorded ABI input')
archive = output / 'steam-bridge-0.4.2.tar.gz'
with tarfile.open(archive, 'w:gz') as bundle:
    for name in (*files, 'licenses/steam-bridge/LICENSE', 'licenses/steam-bridge/NOTICE',
                 'licenses/steam-bridge/ORIGIN.txt'):
        bundle.add(runtime / name, arcname=name, recursive=False)
archive.with_name(archive.name + '.sha256').write_text(
    hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n')
print('Recovered the verified 32-bit and 64-bit Steam bridge and its notices')
PY
