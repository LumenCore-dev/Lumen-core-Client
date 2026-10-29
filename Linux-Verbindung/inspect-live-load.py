import json,subprocess,hashlib
from pathlib import Path
root=Path('/opt/halo4')
p=root/'data/engine/native-server.json'
state=json.loads(p.read_text()) if p.exists() else {}
keys=['status','error','map','map_loaded','session_bank_wide','native_peer_membership','native_player_membership','lan_frames_received','lan_frames_rejected','native_game_engine_kind']
result={k:state.get(k) for k in keys}
result['service']=subprocess.check_output(['systemctl','is-active','halo4-dedicated'],text=True).strip()
result['server_sha256']=hashlib.sha256((root/'Halo4DedicatedServer.exe').read_bytes()).hexdigest()
result['master_sha256']=hashlib.sha256((root/'Halo4LobbyServer.exe').read_bytes()).hexdigest()
print('HALO4_MAINTENANCE:'+json.dumps(result))
