from pathlib import Path
import json,re,subprocess,time,hashlib
root=Path('/opt/halo4');cfg=root/'server.cfg'
expected='315fe35d8964f0f458abbbc19c20506af6a26df18b332ac2d8acabcc6f788225'
assert hashlib.sha256((root/'Halo4DedicatedServer.exe').read_bytes()).hexdigest()==expected
text=cfg.read_text();text,n=re.subn(r'^max_players\s*=.*$','max_players = 16',text,flags=re.M);assert n==1
subprocess.run(['systemctl','stop','halo4-dedicated'],check=True,capture_output=True)
cfg.write_text(text)
subprocess.run(['systemctl','reset-failed','halo4-dedicated'],check=True,capture_output=True)
subprocess.run(['systemctl','start','halo4-dedicated'],check=True,capture_output=True)
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'status':'START_REQUESTED','requested_players':128,'admitted_player_limit':16,'session_capacity':128,'started':time.time()}))
