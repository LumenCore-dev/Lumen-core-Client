"""Stage the paired server and all verified map assets without touching live files."""
from pathlib import Path
import json,hashlib,subprocess,tempfile,re,importlib.util
root=Path(__file__).resolve().parents[1];source=root/'Source'
catalog=json.loads((source/'assets/emotes/catalog.json').read_text())
assert len(catalog['maps'])==26,'All maps must be ready before upload'
elite_models=any(bool(m.get('elite')) for m in catalog['maps'])
assert len({m['map'] for m in catalog['maps']})==26,'Duplicate cache names'
for m in catalog['maps']:
 assert m['path']=='assets/emotes/maps/'+m['map']+'.map'
 assert m['nodes']==120 and m['checksum']==343466014 and len(m['ids'])==6
 assert m['frames']==[40,55,90,90,90,90]
 if elite_models:
  e=m.get('elite') or {}
  assert e.get('nodes')==116 and e.get('checksum')==175174267 and len(e.get('ids',[]))==6,'Missing paired Elite rig: '+m['map']
  assert e.get('frames')==[40,55,90,90,90,90]
  assert 0<e.get('unit',0)<0xffffffff and 0<e.get('graph',0)<0xffffffff
  assert all(isinstance(i,int) and 0<=i<0xffffffff for i in e['ids'])
proof=json.loads((source/'build/emote-wide/validation.json').read_text())
assert proof['status']=='BUILT' and proof['inputsUnchanged']
assert hashlib.sha256((source/'assets/emotes/catalog.json').read_bytes()).hexdigest()==proof['catalogSha256']
assert hashlib.sha256((source/'bin/emote-wide/Halo4DedicatedServer.exe').read_bytes()).hexdigest()==proof['sha256']['Halo4DedicatedServer.exe']
compatibility=json.loads((source/'release-version.inc').read_text().strip())
client_hash=hashlib.sha256((source/'bin/emote-wide/Halo4NativeClient.exe').read_bytes()).hexdigest()
assert client_hash==proof['sha256']['Halo4NativeClient.exe'],'Paired client build differs'
if elite_models:
 assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+-]{0,63}',compatibility)
 assert compatibility!='0.2.5','New Elite caches require a new client/server compatibility version'
 assert proof.get('compatibilityVersion')==compatibility,'Build proof compatibility version differs'
 assert proof.get('inputSha256'),'Elite release requires hashed native/Rust build inputs'
for relative,expected in proof.get('inputSha256',{}).items():
 assert hashlib.sha256((source/relative).read_bytes()).hexdigest()==expected,'Build inputs changed since paired compile: '+relative
files=[(source/'bin/emote-wide/Halo4DedicatedServer.exe','Halo4DedicatedServer.exe'),
       (source/'assets/emotes/catalog.json','assets/emotes/catalog.json')]
files += [(source/m['path'],m['path']) for m in catalog['maps']]
manifest=[]
for path,relative in files:
 h=hashlib.sha256()
 with path.open('rb') as f:
  while data:=f.read(4*1024*1024):h.update(data)
 manifest.append({'path':relative,'bytes':path.stat().st_size,'sha256':h.hexdigest()})
verified={m['path']:m for m in manifest}
for m in catalog['maps']:
 assert verified[m['path']]['sha256']==m['sha256'] and verified[m['path']]['bytes']==m['bytes'],'Cache bytes differ from paired catalog: '+m['map']
remote='/opt/halo4/emote-update-20261019'
spec=importlib.util.spec_from_file_location('halo4_incremental_staging',source/'tools/avatar-runtime/stage_maps_linux.py')
staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging)
# Content-read the remote candidates immediately before deciding to skip them.
# Incremental watcher journals and file timestamps are deliberately insufficient.
remote_files=staging.remote_hashes([relative for _,relative in files])
transfer=[];reused=[]
for path,relative in files:
 expected=verified[relative]
 if remote_files.get(relative)=={'sha256':expected['sha256'],'bytes':expected['bytes']}:
  reused.append(relative)
 else:transfer.append((path,relative))
print('EMOTE_REMOTE_SHA_REUSED',len(reused),'TRANSFER',len(transfer),flush=True)
# Candidate maps can share an inode with the active unchanged cache set.
# Replace through a fresh verified temporary file whenever bytes do differ.
for path,relative in transfer:
 if relative.startswith('assets/emotes/maps/') and relative.endswith('.map'):
  expected=verified[relative]
  staging.upload_map(path,relative,expected['sha256'],expected['bytes'])
with tempfile.TemporaryDirectory(prefix='halo4-emote-upload-') as folder:
 folder=Path(folder);p=folder/'manifest.json';p.write_text(json.dumps({'files':manifest,'elitePlayerModels':elite_models,'compatibilityVersion':compatibility,'clientSha256':client_hash,'catalogSha256':proof['catalogSha256'],'serverSha256':proof['sha256']['Halo4DedicatedServer.exe']},indent=2))
 commands=['option batch abort','option confirm off','open "root@bitymedia.ch"',
           'call mkdir -p '+remote+'/assets/emotes/maps']
 for path,relative in transfer:
  if relative.startswith('assets/emotes/maps/') and relative.endswith('.map'):continue
  commands.append('put -transfer=binary -resumesupport=on "'+str(path)+'" '+remote+'/'+relative)
 commands += ['put -transfer=binary "'+str(p)+'" '+remote+'/manifest.json','exit']
 script=folder/'upload.txt';script.write_text('\n'.join(commands)+'\n',encoding='utf-8-sig')
 with (source/'build/emote-upload.log').open('wb') as log:
  result=subprocess.run([r'C:\Program Files (x86)\WinSCP\WinSCP.com','/nointeractiveinput','/script='+str(script)],stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise SystemExit('Staging upload failed, exit '+str(result.returncode))
(source/'build/emote-upload-manifest.json').write_text(json.dumps({'remote':remote,'files':manifest,'freshRemoteShaReused':reused,'transferred':[relative for _,relative in transfer]},indent=2))
print('EMOTE_UPDATE_STAGED: active service unchanged')
