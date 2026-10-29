import json,subprocess
from pathlib import Path
r=Path('/opt/halo4/data/engine/debug')
files=[{'path':str(p),'bytes':p.stat().st_size} for p in r.rglob('*') if p.is_file()]
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'count':len(files),'largest':sorted(files,key=lambda x:x['bytes'],reverse=True)[:20],'journal':subprocess.run(['journalctl','--disk-usage'],capture_output=True,text=True).stdout}))
