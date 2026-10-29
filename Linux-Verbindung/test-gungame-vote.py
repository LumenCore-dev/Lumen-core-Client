from pathlib import Path
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time

r=Path(r'D:\Halo4-Server')
sys.path.insert(0,str(r/'Source/server/tests'))
from dedicated_server import read_json,lobby_ready,world_ready,stop_owned
spec=importlib.util.spec_from_file_location('rcon',r/'Source/tools/rcon_client.py')
rcon=importlib.util.module_from_spec(spec);spec.loader.exec_module(rcon)
f=r/'reports/gungame-vote-fix-20261016-v4';f.mkdir(exist_ok=False)
s=f/'server';s.mkdir();b=f/'client-bin';b.mkdir()
shutil.copy2(r/'reports/linux-vps-20261016/Halo4DedicatedServer.exe',s/'Halo4DedicatedServer.exe')
shutil.copy2(r/'Source/build/deadlock/Halo4NativeClient.exe',b/'Halo4NativeClient.exe')
shutil.copytree(r/'Client/assets/customize',b/'assets/customize',copy_function=os.link)
cfg=(r/'Linux-Upload/server.cfg').read_text()
for key,value in {'game_directory':str(r/'Server/Packages/Halo4-Windows-Dedicated/game'),'bind':'127.0.0.1:49480','rcon_bind':'127.0.0.1:49482','network':'lan','max_players':'1','vote_seconds':'12','round_seconds':'600','map':'ca_blood_crash'}.items():
    cfg=re.sub(r'^'+key+r'\s*=.*$',lambda match:key+' = '+value,cfg,flags=re.M)
cfg=re.sub(r'^master_address\s*=.*\n?','',cfg,flags=re.M)
(s/'server.cfg').write_text(cfg)
env=os.environ.copy();env['HALO4_HEADLESS_CPU_GRAPHICS_PROBE']='1';env['HALO4_HEADLESS_NO_D3D_PROBE']='1'
host=client=None;result={'status':'STARTING'}
def wait_for(predicate,seconds):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if predicate():return
        if host is not None and host.poll() is not None:raise RuntimeError('Server exited: '+str(host.returncode))
        if client is not None and client.poll() is not None:raise RuntimeError('Client exited: '+str(client.returncode)+': '+str(read_json(f/'client/native-client.json').get('error')))
        time.sleep(.5)
    raise TimeoutError('Timed out waiting for the next test stage')
try:
    host=subprocess.Popen([str(s/'Halo4DedicatedServer.exe')],cwd=s,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    wait_for(lambda:lobby_ready(read_json(s/'data/engine/native-server.json')),40)
    print('Gun Game loadout-disabled native server ready.',flush=True)
    (b/'server-trust').mkdir();shutil.copy2(s/'data/server.tls/server.der',b/'server-trust/127.0.0.1_49480.der')
    client=subprocess.Popen([str(b/'Halo4NativeClient.exe'),'--self-test-map-cycle','127.0.0.1:49480','--self-test-signed-identity','--cycle-vote','19','--game-dir',r'E:\SteamLibrary\steamapps\common\Halo The Master Chief Collection','--output',str(f/'client/native-client.json')],cwd=r/'Source')
    wait_for(lambda:world_ready(read_json(s/'data/engine/native-server.json')) and read_json(f/'client/native-client.json').get('player_snapshot',{}).get('valid'),50)
    print('First Gun Game world loaded with real client.',flush=True)
    time.sleep(5)
    with rcon.Client('127.0.0.1',49482,(s/'data/rcon-password.txt').read_text().strip(),certificate=s/'data/server.tls/server.der') as control:
        result['next_reply']=control.run('next')
    wait_for(lambda:read_json(f/'client/native-client.json').get('status')=='IN_PROCESS_MAP_CYCLE_VERIFIED',110)
    state=read_json(f/'client/native-client.json')
    result['same_pid']=state.get('pid')==client.pid
    result['map']=state.get('map');result['map_loaded']=state.get('map_loaded')
    result['in_process_map_changes']=state.get('in_process_map_changes')
    events='\n'.join(p.read_text(encoding='utf-8') for p in (f/'client').rglob('events.jsonl'))
    result['stock_loadouts_disabled']=events.count('GUNGAME_STOCK_LOADOUTS_DISABLED')>=2
    result['shared_vote_cards_rendered']='ROUND_VOTE_SHARED_CARDS' in events
    result['vote_capture_exists']=(f/'client/round-vote-cards.png').is_file()
    assert result['same_pid'] and result['map']=='ca_gore_valley' and result['in_process_map_changes']==1 and result['stock_loadouts_disabled'] and result['shared_vote_cards_rendered'] and result['vote_capture_exists']
    result['status']='GUNGAME_VOTE_AND_NEXT_WORLD_VERIFIED'
except Exception as error:
    result['status']='FAILED';result['error']=str(error)
finally:
    stop_owned(client);stop_owned(host)
    (f/'validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2),flush=True)
