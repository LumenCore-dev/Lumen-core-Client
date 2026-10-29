from pathlib import Path
import json, subprocess, hashlib
root=Path('/opt/halo4')
def run(*args):
    return subprocess.run(args,text=True,capture_output=True).stdout.strip()
cfg={}
for line in (root/'server.cfg').read_text().splitlines():
    if '=' in line:
        k,v=map(str.strip,line.split('=',1))
        if k in ('name','mode','map','map_pool','game_variant','max_players','min_players','bind','network','game_directory','map_change'):cfg[k]=v
state=json.loads((root/'data/engine/native-server.json').read_text())
report={'ok':True,'config':cfg,'unit':run('systemctl','cat','halo4-dedicated.service'),
 'units':run('systemctl','list-units','--all','--no-pager','--plain','halo4*'),
 'processes':run('ps','-u','halo4-dedicated','-o','pid=,comm='),
 'state':{k:state.get(k) for k in ('status','error','session_bank_wide','native_peer_membership','native_player_membership')},
 'server_sha256':hashlib.sha256((root/'Halo4DedicatedServer.exe').read_bytes()).hexdigest()}
print('HALO4_MAINTENANCE:'+json.dumps(report))
