"""Deploy the owned public IPv4 test services, retaining rollback copies."""
from pathlib import Path
import hashlib
import json
import shutil
import stat
import subprocess
import time

root=Path('/opt/halo4')
units=Path('/etc/systemd/system')
server=units/'halo4-dedicated.service'
master=units/'halo4-master.service'
if 'Description=Halo 4 Dedicated Server under Wine' not in server.read_text() or 'Description=Halo 4 Master Directory under Wine' not in master.read_text():
    raise SystemExit('Unexpected service definitions.')
for name in ('Halo4DedicatedServer.exe','Halo4LobbyServer.exe'):
    if not (root/(name+'.public-candidate')).is_file():
        raise SystemExit('Candidate missing: '+name)
backup=Path('/root/halo4-before-public-test')
backup.mkdir(exist_ok=True,mode=0o700)
for path in (server,master,root/'server.cfg',root/'Halo4DedicatedServer.exe',root/'Halo4LobbyServer.exe'):
    if not (backup/path.name).exists():shutil.copy2(path,backup/path.name)
subprocess.run(['systemctl','stop','halo4-dedicated','halo4-master'],check=True)
for name in ('Halo4DedicatedServer.exe','Halo4LobbyServer.exe'):
    shutil.copy2(root/(name+'.public-candidate'),root/name)
    subprocess.run(['chown','halo4-dedicated:halo4-dedicated',str(root/name)],check=True)
cfg=root/'server.cfg'
text=cfg.read_text().replace('bind = 127.0.0.1:49180','bind = 5.199.139.145:49180').replace('network = lan','network = online')
if 'master_address =' not in text:text+='\nmaster_address = 5.199.139.145:49175\n'
cfg.write_text(text)
master.write_text(master.read_text().replace('--master-bind 127.0.0.1:49175','--master-bind 0.0.0.0:49175'))
trusted=Path('/usr/local/libexec/halo4')
trusted.mkdir(parents=True,exist_ok=True,mode=0o755)
for directory in (trusted,*trusted.parents):
    metadata=directory.lstat()
    if directory.is_symlink() or metadata.st_uid!=0 or metadata.st_mode&0o022:
        raise RuntimeError('Unsafe privileged helper directory: '+str(directory))
firewall=trusted/'halo4-firewall.py'
if firewall.is_symlink():raise RuntimeError('Unexpected firewall helper symlink')
if firewall.exists():
    metadata=firewall.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid!=0 or metadata.st_mode&0o022:
        raise RuntimeError('Unsafe privileged helper file')
firewall.write_text('''from pathlib import Path
import subprocess
import sys
rules=[['-d','5.199.139.145','-p','tcp','--dport','49175','-m','comment','--comment','halo4-public-test','-j','ACCEPT'],['-d','5.199.139.145','-p','tcp','--dport','49180','-m','comment','--comment','halo4-public-test','-j','ACCEPT'],['-d','5.199.139.145','-p','udp','--dport','49180:49181','-m','comment','--comment','halo4-public-test','-j','ACCEPT']]
for rule in rules:
    exists=subprocess.run(['/usr/sbin/iptables','-w','-C','INPUT',*rule],capture_output=True).returncode==0
    if sys.argv[1]=='start' and not exists:subprocess.run(['/usr/sbin/iptables','-w','-A','INPUT',*rule],check=True)
    if sys.argv[1]=='stop' and exists:subprocess.run(['/usr/sbin/iptables','-w','-D','INPUT',*rule],check=True)
''')
firewall.chmod(0o644)
(units/'halo4-network.service').write_text('''[Unit]
Description=Halo 4 public test port rules
After=network-online.target
Before=halo4-master.service halo4-dedicated.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 -I /usr/local/libexec/halo4/halo4-firewall.py start
ExecStop=/usr/bin/python3 -I /usr/local/libexec/halo4/halo4-firewall.py stop
''')
for unit in (server,master):
    content=unit.read_text()
    if 'Requires=halo4-network.service' not in content:
        content=content.replace('[Unit]\n','[Unit]\nRequires=halo4-network.service\nAfter=halo4-network.service\n',1)
    unit.write_text(content)
subprocess.run(['systemctl','daemon-reload'],check=True)
started=time.time()
subprocess.run(['systemctl','start','halo4-master','halo4-dedicated'],check=True)
deadline=time.monotonic()+45
while time.monotonic()<deadline:
    try:
        report=root/'data/engine/native-server.json'
        state=json.loads(report.read_text())
        if report.stat().st_mtime>=started and state.get('status')=='DEDICATED_LOBBY_READY':break
    except (OSError,ValueError):pass
    time.sleep(1)
else:raise SystemExit('Fresh lobby did not become ready.')
print(json.dumps({'status':'PUBLIC_IPV4_DEPLOYED','native_status':state['status'],'audio_disabled':state.get('dedicated_audio_disabled'),'server_sha256':hashlib.sha256((root/'Halo4DedicatedServer.exe').read_bytes()).hexdigest(),'rollback_directory':str(backup)},indent=2),flush=True)
