from pathlib import Path
import json
import sys
import time
root=Path('/opt/halo4')
sys.path.insert(0,str(root))
from rcon_client import Client
deadline=time.monotonic()+40
while time.monotonic()<deadline:
    state=json.loads((root/'data/engine/native-server.json').read_text())
    if state.get('status')=='DEDICATED_WORLD_READY':break
    time.sleep(1)
else:raise SystemExit('World is not ready for a map transition test.')
with Client('127.0.0.1',49182,(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as client:
    print(client.run('status'),flush=True)
    print(client.run('next'),flush=True)
