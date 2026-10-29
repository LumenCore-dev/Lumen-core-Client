"""Expose the native authenticated TLS-RCON endpoint, keeping the existing key."""
from pathlib import Path
import json,os,re,shutil,stat,subprocess,sys,time
root=Path('/opt/halo4');sys.path.insert(0,str(root))
from rcon_client import Client
cfg=root/'server.cfg';original=cfg.read_text()
values={}
for line in original.splitlines():
 if '=' in line and not line.strip().startswith(('#',';')):
  k,v=line.split('=',1);values[k.strip()]=v.strip()
password=(root/values['rcon_password_file']).read_text().strip()
cert=root/'data/server.tls/server.der'
host,port=values['rcon_bind'].rsplit(':',1)
with Client(host,int(port),password,certificate=cert) as c:
 if c.run('players').strip()!='PLAYERS 0':raise RuntimeError('Players connected; restart postponed')
 c.run('stop')
deadline=time.monotonic()+30
while subprocess.run(['systemctl','is-active','--quiet','halo4-dedicated.service']).returncode==0:
 if time.monotonic()>deadline:raise RuntimeError('Stop timed out')
 time.sleep(.3)
backup=root/'data/desktop-backups';backup.mkdir(parents=True,exist_ok=True)
shutil.copy2(cfg,backup/('before-direct-rcon-'+str(time.time_ns())+'.cfg'))
trusted=Path('/usr/local/libexec/halo4')
trusted.mkdir(parents=True,exist_ok=True,mode=0o755)
for directory in (trusted,*trusted.parents):
 metadata=directory.lstat()
 if directory.is_symlink() or metadata.st_uid!=0 or metadata.st_mode&0o022:raise RuntimeError('Unsafe privileged helper directory: '+str(directory))
firewall=trusted/'halo4-rcon-firewall.py'
if firewall.is_symlink():raise RuntimeError('Unexpected firewall helper symlink')
if firewall.exists():
 metadata=firewall.lstat()
 if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid!=0 or metadata.st_mode&0o022:raise RuntimeError('Unsafe privileged helper file')
firewall.write_text('''import subprocess,sys
rule=['-d','5.199.139.145','-p','tcp','--dport','49182','-m','comment','--comment','halo4-rcon-direct','-j','ACCEPT']
exists=subprocess.run(['/usr/sbin/iptables','-w','-C','INPUT',*rule],capture_output=True).returncode==0
if sys.argv[1]=='start' and not exists:subprocess.run(['/usr/sbin/iptables','-w','-A','INPUT',*rule],check=True)
elif sys.argv[1]=='stop' and exists:subprocess.run(['/usr/sbin/iptables','-w','-D','INPUT',*rule],check=True)
''')
firewall.chmod(0o644)
unit=Path('/etc/systemd/system/halo4-rcon-network.service')
unit.write_text('''[Unit]
Description=Halo 4 direct TLS RCON port
After=network-online.target
Before=halo4-dedicated.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 -I /usr/local/libexec/halo4/halo4-rcon-firewall.py start
ExecStop=/usr/bin/python3 -I /usr/local/libexec/halo4/halo4-rcon-firewall.py stop
[Install]
WantedBy=multi-user.target
''')
drop=Path('/etc/systemd/system/halo4-dedicated.service.d/60-rcon-network.conf')
drop.write_text('[Unit]\nRequires=halo4-rcon-network.service\nAfter=halo4-rcon-network.service\n')
changed=re.sub(r'^rcon_bind\s*=.*$','rcon_bind = 5.199.139.145:49182',original,flags=re.M)
if changed==original and values['rcon_bind']!='5.199.139.145:49182':raise RuntimeError('Missing RCON config key')
cfg.write_text(changed)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','enable','--now','halo4-rcon-network.service'],capture_output=True,check=True)
subprocess.run(['systemctl','start','halo4-dedicated.service'],check=True)
deadline=time.monotonic()+45
status=''
while time.monotonic()<deadline:
 try:
  with Client('5.199.139.145',49182,password,certificate=cert) as c:status=c.run('status')
  if status.startswith('SERVER '):break
 except (OSError,ValueError):pass
 time.sleep(.5)
else:
 cfg.write_text(original)
 subprocess.run(['systemctl','restart','halo4-dedicated.service'],check=True)
 raise RuntimeError('Direct listener did not start; original config restored')
# Revoke only the unused tunnel entry introduced during this setup attempt.
keys=Path('/root/.ssh/authorized_keys')
removed=0
if keys.exists():
 old=keys.read_text();rows=old.splitlines();kept=[line for line in rows if 'halo4-manager-rcon-' not in line];removed=len(rows)-len(kept)
 if removed:
  shutil.copy2(keys,backup/('before-tunnel-cleanup-'+str(time.time_ns())+'.keys'))
  keys.write_text('\n'.join(kept)+'\n');keys.chmod(0o600)
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'rcon_endpoint':'5.199.139.145:49182','password_changed':False,'tls_required':True,'unused_tunnel_keys_removed':removed,'status':status.strip()}))
