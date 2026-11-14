"""Record the files that make up the signed Steam Play payload."""
import hashlib
import json
from pathlib import Path
import sys

source, payload, repository = map(Path, sys.argv[1:])
run = (payload / 'run').read_bytes()
if (not run.startswith(b'#!/bin/sh\n# gluon Steam Play compatibility tool shim\n')
        or run not in (payload / 'gluon-steamplay.dylib').read_bytes()):
    sys.exit('Steam Play dylib must embed the packaged Gluon compatibility launcher')
profiles = sorted((payload / 'signatures/macos.arm64').glob('*.json'))
if not profiles:
    sys.exit('Steam Play requires at least one bundled signature profile')
manifest = {
    'schema': 1,
    'compatibility': 'runtime-signatures-v1',
    'notproton': '8562a6320279224125a80cd66bf8d1af9b04bb2d',
    'dobby': '5dfc8546954ce3b3198132ab13fddb89ee92cdd7',
    'profiles': [path.relative_to(payload).as_posix() for path in profiles],
    'files': {},
    'patches': {},
}
for path in sorted((repository / 'steamplay/patches').glob('*.patch')):
    manifest['patches'][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
for path in sorted(payload.rglob('*')):
    if path.is_file() and path.name not in ('payload.json', 'dependencies.txt'):
        manifest['files'][str(path.relative_to(payload))] = hashlib.sha256(path.read_bytes()).hexdigest()
(payload / 'payload.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
