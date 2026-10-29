"""Remove game-user to root paths without restarting the game services."""
import hashlib, json, os, pwd, shutil, stat, subprocess, time
from pathlib import Path

def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE, timeout=35).strip()

def trusted_directory(path):
    if path.is_symlink():
        raise RuntimeError('Symlink in privileged path: ' + str(path))
    if not path.exists():
        path.mkdir(mode=0o755)
    for item in (path, *path.parents):
        s = item.lstat()
        if not stat.S_ISDIR(s.st_mode) or s.st_uid != 0 or s.st_mode & 0o022:
            raise RuntimeError('Unsafe privileged directory: ' + str(item))

root = Path('/opt/halo4')
account = pwd.getpwnam('halo4-dedicated')
units = Path('/etc/systemd/system')
names = ('halo4-network.service', 'halo4-rcon-network.service', 'halo4-log-retention.service')
before_units = {name:(units/name).read_text() for name in names}
before_pids = {name:run('systemctl','show',name,'-p','MainPID','--value') for name in ('halo4-master','halo4-dedicated')}
before_rules = [line for line in run('/usr/sbin/iptables-save').splitlines() if 'halo4-' in line]
helper = Path('/usr/local/sbin/halo4-log-retention')
s = helper.lstat()
if not stat.S_ISREG(s.st_mode) or s.st_uid != 0 or s.st_mode & 0o022:
    raise RuntimeError('Unexpected log retention helper permissions')
for parent in helper.parents:
    trusted_directory(parent)
target = Path('/usr/local/libexec')
trusted_directory(target)
target = target/'halo4'
trusted_directory(target)
backup = Path('/root') / ('halo4-security-backup-' + str(time.time_ns()))
backup.mkdir(mode=0o700)
for name, text in before_units.items():
    (backup/name).write_text(text)

sources = {
    'halo4-firewall.py': '''import subprocess,sys
rules=[['-d','5.199.139.145','-p','tcp','--dport','49175','-m','comment','--comment','halo4-public-test','-j','ACCEPT'],['-d','5.199.139.145','-p','tcp','--dport','49180','-m','comment','--comment','halo4-public-test','-j','ACCEPT'],['-d','5.199.139.145','-p','udp','--dport','49180:49181','-m','comment','--comment','halo4-public-test','-j','ACCEPT']]
if sys.argv[1:] not in (['start'],['stop']):raise SystemExit('Expected start or stop')
for rule in rules:
    exists=subprocess.run(['/usr/sbin/iptables','-w','-C','INPUT',*rule],capture_output=True).returncode==0
    if sys.argv[1]=='start' and not exists:subprocess.run(['/usr/sbin/iptables','-w','-A','INPUT',*rule],check=True)
    if sys.argv[1]=='stop' and exists:subprocess.run(['/usr/sbin/iptables','-w','-D','INPUT',*rule],check=True)
''',
    'halo4-rcon-firewall.py': '''import subprocess,sys
rule=['-d','5.199.139.145','-p','tcp','--dport','49182','-m','comment','--comment','halo4-rcon-direct','-j','ACCEPT']
if sys.argv[1:] not in (['start'],['stop']):raise SystemExit('Expected start or stop')
exists=subprocess.run(['/usr/sbin/iptables','-w','-C','INPUT',*rule],capture_output=True).returncode==0
if sys.argv[1]=='start' and not exists:subprocess.run(['/usr/sbin/iptables','-w','-A','INPUT',*rule],check=True)
elif sys.argv[1]=='stop' and exists:subprocess.run(['/usr/sbin/iptables','-w','-D','INPUT',*rule],check=True)
'''}
for name, text in sources.items():
    compile(text, name, 'exec')
    path=target/name
    if path.is_symlink():raise RuntimeError('Unexpected helper symlink')
    staging=target/(name+'.new-'+str(os.getpid()))
    with staging.open('x') as f:f.write(text)
    staging.chmod(0o644)
    os.chown(staging,0,0)
    os.replace(staging,path)

timer_active = subprocess.run(['systemctl','is-active','--quiet','halo4-log-retention.timer']).returncode == 0
run('systemctl','stop','halo4-log-retention.timer','halo4-log-retention.service')
try:
    for service, filename in (('halo4-network.service','halo4-firewall.py'),('halo4-rcon-network.service','halo4-rcon-firewall.py')):
        old = '/usr/bin/python3 /opt/halo4/' + filename
        new = '/usr/bin/python3 -I ' + str(target/filename)
        text = before_units[service]
        if text.count(old) != 2 and text.count(new) != 2:
            raise RuntimeError('Unexpected unit commands: ' + service)
        (units/service).write_text(text.replace(old,new))
    text=before_units['halo4-log-retention.service']
    if 'User=' not in text:
        text=text.replace('[Service]\n','[Service]\nUser=halo4-dedicated\nGroup=halo4-dedicated\nStateDirectory=halo4-logrotate\nStateDirectoryMode=0700\nUMask=0077\nNoNewPrivileges=true\n',1)
    text=text.replace('/var/lib/halo4-logrotate.status','/var/lib/halo4-logrotate/status')
    text=text.replace('ExecStart=/usr/local/sbin/halo4-log-retention','ExecStart=/usr/bin/python3 -I /usr/local/sbin/halo4-log-retention')
    state=Path('/var/lib/halo4-logrotate')
    if state.is_symlink():raise RuntimeError('Unexpected state symlink')
    if not state.exists():state.mkdir(mode=0o700)
    os.chown(state,account.pw_uid,account.pw_gid)
    state.chmod(0o700)
    # The service creates its own new state. Root must never open a path inside
    # this now service-writable directory, including an apparent missing file.
    (units/'halo4-log-retention.service').write_text(text)
    run('systemctl','daemon-reload')
    # Exercise the real start operation; existing rules must remain unchanged.
    for filename in sources:
        run('/usr/bin/python3','-I',str(target/filename),'start')
    run('systemctl','start','halo4-log-retention.service')
    assert run('systemctl','show','halo4-log-retention.service','-p','Result','--value') == 'success'
    assert run('systemctl','show','halo4-log-retention.service','-p','User','--value') == account.pw_name
    for path in (target,*[target/name for name in sources]):
        assert subprocess.run(['runuser','-u',account.pw_name,'--','test','-w',str(path)]).returncode == 1
    # -I excludes both the game directory and injected PYTHONPATH from imports.
    env=dict(os.environ,PYTHONPATH=str(root))
    imports=subprocess.check_output(['/usr/bin/python3','-I','-c',
        'import subprocess,sys;assert "/opt/halo4" not in sys.path;print(subprocess.__file__)'],
        cwd=root,env=env,text=True).strip()
    assert not imports.startswith(str(root))
    after_rules=[line for line in run('/usr/sbin/iptables-save').splitlines() if 'halo4-' in line]
    assert before_rules == after_rules, 'Firewall rules changed'
    after_pids={name:run('systemctl','show',name,'-p','MainPID','--value') for name in before_pids}
    assert before_pids == after_pids and all(pid!='0' for pid in after_pids.values())
except Exception:
    for name,text in before_units.items():(units/name).write_text(text)
    run('systemctl','daemon-reload')
    if timer_active:run('systemctl','start','halo4-log-retention.timer')
    raise
if timer_active:run('systemctl','start','halo4-log-retention.timer')
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'protected_helper_directory':str(target),
    'game_pids_unchanged':True,'firewall_rules_unchanged':True,'python_import_isolated':True,
    'log_retention_user':account.pw_name,'log_retention_result':'success',
    'backup':str(backup),'timer_active':timer_active}))
