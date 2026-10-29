from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import time

root=Path('/opt/halo4')
cfg=root/'server.cfg'
original=cfg.read_text()
if 'bind = 5.199.139.145:49180' not in original:
    raise SystemExit('Unexpected server configuration.')
maps=('ca_blood_crash','ca_gore_valley','ca_spiderweb')
for name in maps:
    if not (root/'game/halo4/maps'/(name+'.map')).is_file():
        raise SystemExit('Required map missing: '+name)
backup=root/('server.cfg.before-gungame-'+time.strftime('%Y%m%d-%H%M%S'))
shutil.copy2(cfg,backup)
text=original
changes={'name':'Halo 4 - Gun Game','map':maps[0],'map_pool':','.join(maps),'map_variants':','.join(name+':gungame' for name in maps),'game_variant':'gungame','max_players':'16'}
for key,value in changes.items():
    text,count=re.subn(r'^'+key+r'\s*=.*$',key+' = '+value,text,flags=re.M)
    if count!=1:raise SystemExit('Expected exactly one setting: '+key)
text=re.sub(r'^# (?:Gemischt:|Exile:|Ragnarok:|Longbow:|Meltdown:|Outcast:|Perdition:|Shatter:|Vortex:|Wreckage:|Daybreak:).*\n','',text,flags=re.M)
text=text.replace('# 40/128 Spieler brauchen weiterhin groessere native Netzwerkstrukturen.','# Wunsch: 125 Spieler. Dieser native Build unterstuetzt maximal 16.\n# Gun Game: Exile, Longbow, Daybreak; Startkarte Exile.')
sys.path.insert(0,str(root))
from rcon_client import Client
def command(value):
    with Client('127.0.0.1',49182,(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as client:
        return client.run(value).strip()
print('Before: '+command('status'),flush=True)
cfg.write_text(text)
print(command('stop'),flush=True)
deadline=time.monotonic()+30
while subprocess.run(['systemctl','is-active','--quiet','halo4-dedicated']).returncode==0:
    if time.monotonic()>deadline:raise SystemExit('Graceful server stop timed out.')
    time.sleep(.5)
started=time.time()
subprocess.run(['systemctl','start','halo4-dedicated'],check=True)
deadline=time.monotonic()+40
while time.monotonic()<deadline:
    try:
        report=root/'data/engine/native-server.json'
        state=json.loads(report.read_text())
        if report.stat().st_mtime>=started and state.get('status') in ('DEDICATED_LOBBY_READY','DEDICATED_WORLD_READY'):
            status=command('status')
            if 'map=ca_blood_crash ' in status and 'variant=13 ' in status and 'max_players=16 ' in status:break
    except (OSError,ValueError):pass
    time.sleep(1)
else:raise SystemExit('Gun Game server did not become ready.')
result={'status':'GUNGAME_SERVER_READY','server':status,'maps':list(maps),'requested_max_players':125,'supported_max_players':16,'backup':str(backup),'native_status':state['status']}
(root/'gungame-config-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
