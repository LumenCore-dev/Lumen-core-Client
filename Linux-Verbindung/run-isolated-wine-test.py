"""Upload one candidate to a unique staging directory and test it without deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--server-exe', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
binary = args.server_exe.resolve(strict=True)
folder = args.output.resolve()
folder.mkdir(parents=True, exist_ok=False)
spec = {'directory': '/var/tmp/halo4-maintainability-'+secrets.token_hex(8),
        'sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
(folder/'test-spec.json').write_text(json.dumps(spec, indent=2)+'\n')
script = ('option batch abort\noption confirm off\nopen "root@bitymedia.ch"\n'
          f'call install -d -m 700 -o halo4-dedicated -g halo4-dedicated {spec["directory"]}\n'
          f'put -transfer=binary "{binary}" {spec["directory"]}/Halo4DedicatedServer.exe\nexit\n')
upload = folder/'upload.txt'
upload.write_text(script, encoding='utf-8-sig')
process = subprocess.run([r'C:\Program Files (x86)\WinSCP\WinSCP.com', '/nointeractiveinput',
                          '/script='+str(upload)], capture_output=True, timeout=300)
if process.returncode:
    raise SystemExit('Isolated test upload failed: '+str(process.returncode))
root = Path(__file__).resolve().parent
test = folder/'remote-test.py'
test.write_text('TEST_SPEC = '+repr(spec)+'\n'+(root/'verify-isolated-wine.py').read_text(), encoding='utf-8')
process = subprocess.run([sys.executable, str(root/'run-maintenance.py'), str(test), '180', '--service-user'],
                         capture_output=True, text=True, timeout=200)
(folder/'remote-result.log').write_text(process.stdout+'\n'+process.stderr, encoding='utf-8')
if process.returncode:
    raise SystemExit('Isolated Wine check failed; see '+str(folder/'remote-result.log'))
result = json.loads(process.stdout)
(folder/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
raise SystemExit(0 if result.get('status') == 'WINE_LOBBY_RCON_VERIFIED' else 1)
