from pathlib import Path
import subprocess,json
root=Path('/opt/halo4')
out={}
for name in ('data/engine/server-console.log','data/engine/server-core.log'):
    p=root/name
    if p.exists():out[name]=p.read_text(errors='replace')[-6000:]
out['journal']=subprocess.run(['journalctl','-u','halo4-dedicated','-n','35','--no-pager','-o','cat'],capture_output=True,text=True).stdout
print('HALO4_MAINTENANCE:'+json.dumps(out))
