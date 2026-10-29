from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,time
root=Path('/opt/halo4');cfg=root/'server.cfg'
candidate=root/'Halo4DedicatedServer.exe.join-leave-v9';exe=root/'Halo4DedicatedServer.exe'
expected='315fe35d8964f0f458abbbc19c20506af6a26df18b332ac2d8acabcc6f788225'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==expected,'Candidate checksum differs'
unit='halo4-dedicated.service'
drop=Path('/etc/systemd/system/halo4-dedicated.service.d/70-wide-session.conf')
backup=root/('rollback-join-leave-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
for p in (cfg,exe):shutil.copy2(p,backup/p.name)
if drop.exists():shutil.copy2(drop,backup/drop.name)
old_drop=drop.read_bytes() if drop.exists() else None
original=cfg.read_text();updated=original
changes={'name':'Halo 4 - Team Deathmatch','game_variant':'slayer','max_players':'16','mode':'multiplayer'}
maps=None
for line in original.splitlines():
    if re.match(r'^map_pool\s*=',line):maps=line.split('=',1)[1].strip().split(',')
assert maps,'Map pool missing'
changes['map_variants']=','.join(m.strip()+':slayer' for m in maps)
for key,value in changes.items():
    updated,count=re.subn(r'^'+key+r'\s*=.*$',key+' = '+value,updated,flags=re.M)
    if count==0:updated+='\n'+key+' = '+value+'\n'
    assert count<=1,'Duplicate configuration key '+key
updated='\n'.join(line for line in updated.splitlines() if not (line.startswith('#') and any(x in line for x in ('Gun Game','125 Spieler','Dieser native Build'))))+'\n'
updated+='# 128 Session slots; physical gameplay backend remains 16. Three clients verified locally.\n'
sys.path.insert(0,str(root));from rcon_client import Client
rcon_match=re.search(r'^rcon_bind\s*=\s*([^\s]+)',original,re.M)
rcon_host,rcon_port=(rcon_match.group(1) if rcon_match else '127.0.0.1:49182').rsplit(':',1)
if rcon_host=='0.0.0.0':rcon_host='127.0.0.1'
def command(value):
    with Client(rcon_host,int(rcon_port),(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as c:return c.run(value).strip()
try:before=command('status')
except OSError:before='Previous service unavailable during deployment recovery'
def run(*args):subprocess.run(args,check=True,capture_output=True,text=True)
try:
    run('systemctl','stop',unit)
    shutil.copy2(candidate,exe);run('chown','halo4-dedicated:halo4-dedicated',str(exe))
    cfg.write_text(updated)
    drop.parent.mkdir(exist_ok=True)
    drop.write_text('[Service]\nEnvironment=HALO4_CAPACITY_LAB_PLAYERS=128 HALO4_WIDE_SESSION_BANK=1 HALO4_HEADLESS_DYNAMIC_ARENA=1\n')
    run('systemctl','daemon-reload');run('systemctl','reset-failed',unit);started=time.time();run('systemctl','start',unit)
    deadline=time.monotonic()+85;state={};status=''
    while time.monotonic()<deadline:
        try:
            p=root/'data/engine/native-server.json';state=json.loads(p.read_text())
            if p.stat().st_mtime>=started and state.get('status')=='DEDICATED_LOBBY_READY':
                assert state.get('session_bank_wide') is True,'Wide Session not enabled'
                assert state.get('native_peer_membership',{}).get('capacity')==129,'Peer capacity differs'
                assert state.get('native_player_membership',{}).get('capacity')==128,'Player capacity differs'
                status=command('status')
                assert 'variant=0 ' in status and 'max_players=16 ' in status,'Live configuration differs'
                break
        except (OSError,ValueError):pass
        time.sleep(1)
    else:raise RuntimeError('Fresh wide-session lobby did not become ready: '+str(state.get('error')))
    active=subprocess.check_output(['systemctl','is-active',unit],text=True).strip();assert active=='active'
    processes=subprocess.check_output(['ps','-u','halo4-dedicated','-o','comm='],text=True).splitlines()
    count=sum(p.strip().startswith('Halo4Dedicated') for p in processes);assert count==1,'Expected one dedicated process, got '+str(count)
    report={'ok':True,'status':'LINUX_TDM_WIDE_SESSION_READY','server':status,'native_status':state['status'],
      'dedicated_processes':count,'requested_players':128,'admitted_player_limit':16,'session_player_capacity':128,'physical_backend_capacity':16,'128_gameplay_verified':False,
      'server_sha256':expected,'backup':str(backup),'before':before,'maps':maps}
    (root/'join-leave-tdm-deployment.json').write_text(json.dumps(report,indent=2))
except Exception as error:
    subprocess.run(['systemctl','stop',unit],capture_output=True)
    for p in (cfg,exe):shutil.copy2(backup/p.name,p)
    if old_drop is None:drop.unlink(missing_ok=True)
    else:drop.write_bytes(old_drop)
    subprocess.run(['systemctl','daemon-reload'],capture_output=True)
    subprocess.run(['systemctl','reset-failed',unit],capture_output=True)
    restored=subprocess.run(['systemctl','start',unit],capture_output=True).returncode==0
    report={'ok':False,'error':str(error),'rollback_started':restored,'backup':str(backup)}
print('HALO4_MAINTENANCE:'+json.dumps(report))
