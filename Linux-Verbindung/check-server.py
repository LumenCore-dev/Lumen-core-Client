from pathlib import Path
import json
import sys

root = Path('/opt/halo4')
sys.path.insert(0, str(root))
from rcon_client import Client

state = json.loads((root/'data/engine/native-server.json').read_text())
print(json.dumps({name: state.get(name) for name in ('status','phase','error','session_role','session_phase','native_membership_verified','runtime_asset_root_linked','headless_render_mode','map_loaded')}, indent=2))
with Client('127.0.0.1', 49182, (root/'data/rcon-password.txt').read_text().strip(), certificate=root/'data/server.tls/server.der') as client:
    print('RCON:', client.run('status'))
