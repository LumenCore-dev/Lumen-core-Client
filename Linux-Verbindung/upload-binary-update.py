"""Upload a paired 0.2.8 server binary and integrity manifest; no Halo assets."""
from pathlib import Path
import hashlib,json,importlib.util,re
import sys
root=Path(__file__).resolve().parents[1];source=root/'Source'
sys.path.insert(0,str(source/'tools'))
from release_quality import run_checks,require_verified_build
run_checks()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while block:=f.read(8*1024*1024):h.update(block)
 return h.hexdigest()
proof=json.loads((source/'build/emote-wide/validation.json').read_text())
version=json.loads((source/'release-version.inc').read_text().strip())
assert version=='0.2.8','This rollout is for the original-map 0.2.8 release'
assert proof.get('status')=='BUILT' and proof.get('inputsUnchanged') is True
assert proof.get('compatibilityVersion')==version and proof.get('inputSha256')
assert proof.get('modifiedMapFeatures') is False,'Original-map release requires the central custom-cache feature gate disabled'
for relative,expected in proof['inputSha256'].items():
 if relative.replace('\\','/')=='assets/emotes/catalog.json':continue
 assert sha(source/relative)==expected,'Build input changed: '+relative
server=source/'bin/emote-wide/Halo4DedicatedServer.exe';client=source/'bin/emote-wide/Halo4NativeClient.exe'
require_verified_build(proof,{'Halo4DedicatedServer.exe':server,'Halo4NativeClient.exe':client},source)
server_hash=sha(server);client_hash=sha(client)
assert server_hash==proof['sha256']['Halo4DedicatedServer.exe'] and client_hash==proof['sha256']['Halo4NativeClient.exe']
manifest={'version':version,'assetMode':'installed-original-maps','files':[{'path':'Halo4DedicatedServer.exe','sha256':server_hash,'bytes':server.stat().st_size}],'serverSha256':server_hash,'pairedClientSha256':client_hash,'mapsUploaded':False,'engineUploaded':False,'testsExecuted':proof.get('testsExecuted')}
report=source/'reports/binary-only-release-20261019';report.mkdir(parents=True,exist_ok=True)
manifest_path=report/'binary-upload-manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('staging',source/'tools/avatar-runtime/stage_maps_linux.py');staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging)
remote='/opt/halo4/binary-update-0.2.8'
code="from pathlib import Path;import hashlib,json;r=Path("+repr(remote)+");m=json.loads((r/'manifest.json').read_text());p=r/'Halo4DedicatedServer.exe';assert p.stat().st_size==m['files'][0]['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==m['serverSha256'];print('HALO4_STAGE_RESULT:'+json.dumps({'ok':True,'status':'BINARY_ONLY_STAGED','serverSha256':m['serverSha256'],'mapsUploaded':False,'liveFilesTouched':False}))"
result=staging.winscp(['call mkdir -p '+remote,'put -transfer=binary "'+str(server)+'" '+remote+'/Halo4DedicatedServer.exe','put -transfer=binary "'+str(manifest_path)+'" '+remote+'/manifest.json',staging.remote_command(code)],'binary-only-upload')
(report/'binary-upload-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
