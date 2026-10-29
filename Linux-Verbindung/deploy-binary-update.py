"""Deploy only the paired server executable, retaining installed original maps."""
from pathlib import Path
import hashlib,json,re,subprocess,time,sys,fcntl,sqlite3,shutil,struct
root=Path('/opt/halo4');candidate=root/'binary-update-0.2.8';unit='halo4-dedicated.service';exe=root/'Halo4DedicatedServer.exe'
lock=(root/'.emote-deploy.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while block:=f.read(8*1024*1024):h.update(block)
 return h.hexdigest()
def run(*args):return subprocess.run(args,check=True,capture_output=True,text=True)
manifest=json.loads((candidate/'manifest.json').read_text())
assert manifest['version']=='0.2.8' and manifest['assetMode']=='installed-original-maps'
assert manifest['mapsUploaded'] is False and manifest['engineUploaded'] is False
assert re.fullmatch('[a-f0-9]{64}',manifest['pairedClientSha256'])
assert len(manifest['files'])==1 and manifest['files'][0]['path']=='Halo4DedicatedServer.exe'
assert sha(candidate/exe.name)==manifest['serverSha256']==manifest['files'][0]['sha256']
assert (candidate/exe.name).stat().st_size==manifest['files'][0]['bytes']
cfg=root/'server.cfg';original_cfg=cfg.read_bytes();text=original_cfg.decode();selected=re.search(r'^map\s*=\s*(\S+)',text,re.M).group(1)
pool=re.search(r'^map_pool\s*=\s*(\S+)',text,re.M);names=list(dict.fromkeys([selected]+(pool.group(1).split(',') if pool else [])))
original_maps={}
for name in names:
 assert re.fullmatch('[a-z0-9_]+',name)
 path=root/'game/halo4/maps'/(name+'.map');assert path.is_file() and not path.is_symlink()
 with path.open('rb') as f:header=f.read(512)
 assert header[:4]==b'daeh' and struct.unpack_from('<I',header,4)[0]==13
 original_maps[name]={'path':'game/halo4/maps/'+name+'.map','bytes':path.stat().st_size,'sha256':sha(path),'build':header[152:184].split(b'\0')[0].decode(errors='replace')}
 print('ORIGINAL_MAP_PRESENT '+name,flush=True)
max_players=int(re.search(r'^max_players\s*=\s*(\d+)',text,re.M).group(1));bind=re.search(r'^rcon_bind\s*=\s*(\S+)',text,re.M)
host,port=(bind.group(1) if bind else '127.0.0.1:49182').rsplit(':',1)
if host=='0.0.0.0':host='127.0.0.1'
sys.path.insert(0,str(root));from rcon_client import Client
def status():
 with Client(host,int(port),(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as client:return client.run('status').strip()
before=status();backup=root/('rollback-binary-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
shutil.copy2(exe,backup/exe.name);shutil.copy2(cfg,backup/cfg.name)
try:
 run('systemctl','stop',unit)
 database_match=re.search(r'^database\s*=\s*(\S+)',text,re.M)
 if database_match:
  database=root/database_match.group(1)
  if database.is_file():
   with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as source,sqlite3.connect(backup/'server.sqlite3') as target:source.backup(target)
 shutil.copy2(candidate/exe.name,exe);run('chown','halo4-dedicated:halo4-dedicated',str(exe))
 started=time.time();run('systemctl','reset-failed',unit);run('systemctl','start',unit)
 deadline=time.monotonic()+100;state={}
 while time.monotonic()<deadline:
  try:
   report_path=root/'data/engine/native-server.json';state=json.loads(report_path.read_text())
   if report_path.stat().st_mtime>=started and state.get('status')=='DEDICATED_LOBBY_READY':
    assert state.get('emote_cache_verified') is False,'Custom emote cache is still active'
    assert not state.get('emote_cache_sha256'),'Unexpected custom-cache fingerprint'
    assert state.get('session_bank_wide') is True and state.get('native_player_membership',{}).get('capacity')==128
    active_map=state.get('map');assert active_map in original_maps,'Native map is outside original configured pool'
    live=status();assert 'max_players='+str(max_players)+' ' in live
    assert cfg.read_bytes()==original_cfg,'Server configuration changed'
    break
  except (OSError,ValueError):pass
  time.sleep(1)
 else:raise RuntimeError('Original-map native lobby did not become ready: '+str(state.get('error')))
 assert run('systemctl','is-active',unit).stdout.strip()=='active'
 active_path=root/original_maps[active_map]['path'];assert sha(active_path)==original_maps[active_map]['sha256'],'Installed original map changed'
 assert sha(exe)==manifest['serverSha256']
 report={'ok':True,'status':'LINUX_ORIGINAL_MAPS_READY','compatibilityVersion':manifest['version'],'server':live,'before':before,'configurationPreserved':True,'serverSha256':manifest['serverSha256'],'pairedClientSha256':manifest['pairedClientSha256'],'emoteCacheVerified':False,'emoteCacheSha256':state.get('emote_cache_sha256'),'nativeMap':active_map,'installedOriginalMap':original_maps[active_map],'originalConfiguredPool':original_maps,'mapAssetsUploaded':False,'mapAssetsSwapped':False,'engineUploaded':False,'serviceActive':True,'freshNativeLobbyReady':True,'backup':str(backup),'testsExecuted':False}
except Exception as error:
 subprocess.run(['systemctl','stop',unit],capture_output=True);shutil.copy2(backup/exe.name,exe)
 subprocess.run(['systemctl','reset-failed',unit],capture_output=True);restored=subprocess.run(['systemctl','start',unit],capture_output=True).returncode==0
 report={'ok':False,'error':str(error),'rollbackStarted':restored,'backup':str(backup),'mapAssetsUploaded':False,'mapAssetsSwapped':False}
(root/'binary-deployment.json').write_text(json.dumps(report,indent=2)+'\n');print('HALO4_MAINTENANCE:'+json.dumps(report))
