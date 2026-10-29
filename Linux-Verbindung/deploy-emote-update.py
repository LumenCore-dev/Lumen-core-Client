"""Verify all staged assets, preserve live policy, and roll back a failed start."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,time,os,sqlite3,fcntl
root=Path('/opt/halo4');candidate=root/'emote-update-20261019'
deployment_lock=(root/'.emote-deploy.lock').open('a')
try:fcntl.flock(deployment_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
 print('HALO4_MAINTENANCE:'+json.dumps({'ok':False,'error':'An emote deployment is already running'}));raise SystemExit(1)
unit='halo4-dedicated.service';exe=root/'Halo4DedicatedServer.exe';assets=root/'assets/emotes'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while data:=f.read(4*1024*1024):h.update(data)
 return h.hexdigest()
def run(*args):return subprocess.run(args,check=True,capture_output=True,text=True)
manifest=json.loads((candidate/'manifest.json').read_text())
verified={}
for item in manifest['files']:
 print('EMOTE_VERIFY '+item['path'],flush=True)
 relative=Path(item['path']);assert not relative.is_absolute() and '..' not in relative.parts
 p=candidate/relative
 assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'Staged checksum differs: '+str(relative)
 verified[item['path']]=item
catalog=json.loads((candidate/'assets/emotes/catalog.json').read_text());assert len(catalog['maps'])==26
assert len({m['map'] for m in catalog['maps']})==26
elite_models=any(bool(m.get('elite')) for m in catalog['maps'])
if elite_models:
 assert manifest.get('elitePlayerModels') is True,'Missing paired Elite manifest'
 assert manifest.get('catalogSha256')==verified['assets/emotes/catalog.json']['sha256']
 assert manifest.get('serverSha256')==verified['Halo4DedicatedServer.exe']['sha256']
 assert re.fullmatch(r'[a-f0-9]{64}',manifest.get('clientSha256','')),'Missing paired client hash'
 version=manifest.get('compatibilityVersion','')
 assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+-]{0,63}',version) and version!='0.2.5','Elite caches require a new paired compatibility version'
for m in catalog['maps']:
 assert m['path']=='assets/emotes/maps/'+m['map']+'.map'
 assert verified[m['path']]['sha256']==m['sha256'] and verified[m['path']]['bytes']==m['bytes'] and m['nodes']==120 and len(m['ids'])==6
 assert m['checksum']==343466014 and m['frames']==[40,55,90,90,90,90]
 if elite_models:
  e=m.get('elite') or {}
  assert e.get('nodes')==116 and e.get('checksum')==175174267 and len(e.get('ids',[]))==6,'Missing paired Elite rig: '+m['map']
  assert e.get('frames')==[40,55,90,90,90,90]
  assert 0<e.get('unit',0)<0xffffffff and 0<e.get('graph',0)<0xffffffff
  assert all(isinstance(i,int) and 0<=i<0xffffffff for i in e['ids'])
cfg=root/'server.cfg';original_cfg=cfg.read_bytes();text=original_cfg.decode()
selected=re.search(r'^map\s*=\s*(\S+)',text,re.M).group(1)
expected_map=next(m for m in catalog['maps'] if m['map']==selected)
max_players=int(re.search(r'^max_players\s*=\s*(\d+)',text,re.M).group(1))
bind=re.search(r'^rcon_bind\s*=\s*(\S+)',text,re.M)
host,port=(bind.group(1) if bind else '127.0.0.1:49182').rsplit(':',1)
if host=='0.0.0.0':host='127.0.0.1'
sys.path.insert(0,str(root));from rcon_client import Client
def status():
 with Client(host,int(port),(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as c:return c.run('status').strip()
before=status();backup=root/('rollback-emotes-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
shutil.copy2(exe,backup/exe.name);shutil.copy2(cfg,backup/cfg.name)
had_assets=assets.exists();installed=False
try:
 run('systemctl','stop',unit)
 database_match=re.search(r'^database\s*=\s*(\S+)',text,re.M)
 if database_match:
  database=root/database_match.group(1)
  if database.is_file():
   with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as source,sqlite3.connect(backup/'server.sqlite3') as target:source.backup(target)
 if had_assets:os.replace(assets,backup/'emotes')
 assets.parent.mkdir(exist_ok=True);os.replace(candidate/'assets/emotes',assets);installed=True
 shutil.copy2(candidate/exe.name,exe)
 run('chown','-R','halo4-dedicated:halo4-dedicated',str(assets));run('chown','halo4-dedicated:halo4-dedicated',str(exe))
 started=time.time();run('systemctl','reset-failed',unit);run('systemctl','start',unit)
 deadline=time.monotonic()+85;state={}
 while time.monotonic()<deadline:
  try:
   p=root/'data/engine/native-server.json';state=json.loads(p.read_text())
   if p.stat().st_mtime>=started and state.get('status')=='DEDICATED_LOBBY_READY':
    assert state.get('session_bank_wide') is True,'Wide session disabled'
    assert state.get('native_player_membership',{}).get('capacity')==128
    assert state.get('emote_cache_verified') is True,'Map emote cache not loaded'
    assert state.get('emote_cache_sha256')==expected_map['sha256']
    live=status();assert 'max_players='+str(max_players)+' ' in live
    assert cfg.read_bytes()==original_cfg,'Server configuration changed'
    break
  except (OSError,ValueError):pass
  time.sleep(1)
 else:raise RuntimeError('Fresh lobby did not become ready: '+str(state.get('error')))
 assert run('systemctl','is-active',unit).stdout.strip()=='active'
 report={'ok':True,'status':'LINUX_EMOTES_READY','server':live,'before':before,'maps':26,
  'configurationPreserved':True,'emoteMap':selected,'emoteCacheSha256':expected_map['sha256'],
  'serverSha256':sha(exe),'backup':str(backup)}
 if elite_models:report.update(elitePlayerModels=True,compatibilityVersion=manifest['compatibilityVersion'],pairedClientSha256=manifest['clientSha256'],catalogSha256=manifest['catalogSha256'])
except Exception as error:
 subprocess.run(['systemctl','stop',unit],capture_output=True)
 shutil.copy2(backup/exe.name,exe)
 if installed:os.replace(assets,candidate/'assets/emotes')
 if had_assets and (backup/'emotes').exists():os.replace(backup/'emotes',assets)
 subprocess.run(['systemctl','reset-failed',unit],capture_output=True)
 restored=subprocess.run(['systemctl','start',unit],capture_output=True).returncode==0
 report={'ok':False,'error':str(error),'rollbackStarted':restored,'backup':str(backup)}
(root/'emote-deployment.json').write_text(json.dumps(report,indent=2))
print('HALO4_MAINTENANCE:'+json.dumps(report))
