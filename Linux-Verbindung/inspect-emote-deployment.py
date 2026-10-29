from pathlib import Path
import json,subprocess,hashlib
root=Path('/opt/halo4')
def read(path):
 try:return json.loads(path.read_text())
 except (OSError,ValueError):return {}
state=read(root/'data/engine/native-server.json')
report=read(root/'emote-deployment.json')
processes=subprocess.check_output(['ps','-C','python3','-o','pid=,etimes=,comm='],text=True).strip()
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'service':subprocess.run(['systemctl','is-active','halo4-dedicated.service'],capture_output=True,text=True).stdout.strip(),
 'deployment':report,'native':{k:state.get(k) for k in ['status','error','pid','map','emote_cache_verified','emote_cache_sha256','session_bank_wide']},
 'pythonProcesses':processes,'serverSha256':hashlib.sha256((root/'Halo4DedicatedServer.exe').read_bytes()).hexdigest(),
 'candidateAssets':(root/'emote-update-20261019/assets/emotes').exists(),'activeAssets':(root/'assets/emotes').exists()}))
