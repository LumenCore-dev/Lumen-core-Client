"""Read-only acceptance check against the production baseline of 2026-10-20.

The pinned live hashes are historical acceptance inputs, not a generic updater.
"""
import hashlib
import json
from pathlib import Path
import subprocess

expected = {
    'Halo4DedicatedServer.exe': 'd80cb03d7820307cc72266a9c1520b876c80b28fab9561d54ce09ec428dfd631',
    'Halo4LobbyServer.exe': '99ea137c729436d081a4ce8b2d513bb3df16a4f8500804db2356d38f32b0285e',
}
live = {name: hashlib.sha256((Path('/opt/halo4')/name).read_bytes()).hexdigest() for name in expected}
tests = []
for report in Path('/var/tmp').glob('halo4-maintainability-*/test/validation.json'):
    result = json.loads(report.read_text())
    prefix = ('WINEPREFIX='+str(report.parent/'.wine')).encode()
    running = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            environment = (entry/'environ').read_bytes().split(b'\0')
            if prefix in environment:
                running.append(int(entry.name))
        except (OSError, PermissionError):
            pass
    tests.append({'directory': str(report.parent), 'status': result.get('status'), 'remainingPrefixPids': running})
services = {name: subprocess.run(['systemctl', 'is-active', name], capture_output=True, text=True).stdout.strip()
            for name in ('halo4-master', 'halo4-dedicated')}
print('HALO4_MAINTENANCE:'+json.dumps({'liveHashes': live, 'productionBinariesUnchanged': live == expected,
    'services': services, 'isolatedTests': tests, 'allTestPrefixesStopped': all(not t['remainingPrefixPids'] for t in tests)}))
