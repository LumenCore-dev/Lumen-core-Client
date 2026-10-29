"""Bound Halo log retention without restarting either game service."""
import json, subprocess
from pathlib import Path

def run(*args):
    return subprocess.run(args,check=True,capture_output=True,text=True,timeout=20).stdout

rotation='''/opt/halo4/data/engine/*.log /opt/halo4/data/engine/debug/*/events.jsonl /opt/halo4/data/engine/debug/*/errors.jsonl {
    size 20M
    rotate 4
    missingok
    notifempty
    copytruncate
    compress
    su halo4-dedicated halo4-dedicated
}
'''
# Separate configuration/state avoids racing the distribution's daily job.
Path('/etc/halo4-logrotate.conf').write_text(rotation)
helper=r'''#!/usr/bin/python3
import os, re, time, subprocess
from pathlib import Path
root=Path('/opt/halo4/data/engine')
open_inodes=set()
for proc in Path('/proc').glob('[0-9]*'):
    try:
        for fd in (proc/'fd').iterdir():
            try:
                st=fd.stat();open_inodes.add((st.st_dev,st.st_ino))
            except OSError: pass
    except OSError: pass
# Restrict deletion to known log filenames, never game assets or directories.
pattern=re.compile(r'^(server-core\.log|server-console\.log|events\.jsonl|errors\.jsonl|crash\.dmp)(\.\d+(\.gz)?)?$')
files=[]
for directory,dirs,names in os.walk(root,followlinks=False):
    dirs[:]=[d for d in dirs if not Path(directory,d).is_symlink()]
    for name in names:
        p=Path(directory,name)
        if not pattern.fullmatch(name) or p.is_symlink(): continue
        st=p.stat()
        if not p.is_file(): continue
        files.append((st.st_mtime,st.st_size,p,(st.st_dev,st.st_ino) in open_inodes))
total=sum(f[1] for f in files);removed=0
for modified,size,path,opened in sorted(files):
    if opened: continue
    if total>512*1024*1024 or modified<time.time()-14*86400:
        path.unlink();total-=size;removed+=1
print(f'Halo log retention: {total} bytes, {removed} expired files removed')
'''
Path('/usr/local/sbin/halo4-log-retention').write_text(helper)
Path('/usr/local/sbin/halo4-log-retention').chmod(0o755)
Path('/etc/systemd/system/halo4-log-retention.service').write_text('''[Unit]
Description=Rotate and bound Halo diagnostic logs
[Service]
Type=oneshot
User=halo4-dedicated
Group=halo4-dedicated
StateDirectory=halo4-logrotate
StateDirectoryMode=0700
UMask=0077
NoNewPrivileges=true
ExecStart=/usr/sbin/logrotate --state /var/lib/halo4-logrotate/status /etc/halo4-logrotate.conf
ExecStart=/usr/bin/python3 -I /usr/local/sbin/halo4-log-retention
Nice=10
IOSchedulingClass=idle
''')
Path('/etc/systemd/system/halo4-log-retention.timer').write_text('''[Unit]
Description=Check Halo log sizes every minute
[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
AccuracySec=5s
[Install]
WantedBy=timers.target
''')
validation=run('/usr/sbin/logrotate','--debug','/etc/halo4-logrotate.conf')
compile(helper,'halo4-log-retention','exec')
before=run('systemctl','show','halo4-dedicated.service','-p','MainPID','--value').strip()
run('systemctl','daemon-reload')
run('systemctl','enable','--now','halo4-log-retention.timer')
run('systemctl','start','halo4-log-retention.service')
after=run('systemctl','show','halo4-dedicated.service','-p','MainPID','--value').strip()
assert before==after and after!='0'
assert run('systemctl','is-active','halo4-log-retention.timer').strip()=='active'
report={'ok':True,'rotation_megabytes':20,'archives_per_file':4,'retention_days':14,'aggregate_target_megabytes':512,'check_interval_seconds':60,'server_restarted':False,'notes':'Periodic target, not a filesystem hard quota. Open files are preserved. System-wide journal and non-log diagnostic assets are outside this policy.','last_run':run('journalctl','-u','halo4-log-retention.service','-n','5','--no-pager')}
print('HALO4_MAINTENANCE:'+json.dumps(report))
