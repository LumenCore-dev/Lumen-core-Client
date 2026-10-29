import json, subprocess
from pathlib import Path
def run(*args):
    p=subprocess.run(args,capture_output=True,text=True,timeout=15)
    return p.stdout[-12000:]
root=Path('/opt/halo4')
files=[]
for p in root.rglob('*'):
    if p.is_file() and (p.suffix in ('.log','.dmp') or p.name.endswith('.service')):
        s=p.stat();files.append({'path':str(p),'bytes':s.st_size})
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'units':run('systemctl','cat','halo4-dedicated.service','halo4-master.service'),'files':sorted(files,key=lambda x:x['bytes'],reverse=True)[:45],'rotation':run('sh','-c','command -v logrotate; ls /etc/logrotate.d; df -h /opt/halo4'),'timers':run('systemctl','list-timers','--all','--no-pager')}))
