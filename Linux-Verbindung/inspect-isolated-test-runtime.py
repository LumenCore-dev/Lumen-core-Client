"""Read prerequisites for an isolated Wine test; do not touch running services."""
import json
import os
from pathlib import Path
import shutil
import subprocess

root = Path('/opt/halo4')
state_path = root/'data/engine/native-server.json'
state = json.loads(state_path.read_text()) if state_path.exists() else {}
result = {
    'uid': os.getuid(),
    'wine': shutil.which('wine'),
    'xvfb': shutil.which('xvfb-run'),
    'wineStable': Path('/opt/wine-stable/lib/wine/x86_64-unix/wine').is_file(),
    'gameDirectory': (root/'game/halo4/halo4.dll').is_file(),
    'nativeCppRuntime': (root/'vcruntime140.dll').is_file(),
    'gameState': {k: state.get(k) for k in ('status', 'map', 'map_loaded', 'native_peer_membership')},
    'services': {name: subprocess.run(['systemctl', 'is-active', name], capture_output=True, text=True).stdout.strip()
                 for name in ('halo4-master', 'halo4-dedicated')},
    'memory': [line for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemTotal:', 'MemAvailable:'))],
}
print('HALO4_MAINTENANCE:'+json.dumps(result))
