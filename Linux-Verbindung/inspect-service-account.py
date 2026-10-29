import json
import pwd
import grp
import subprocess
from pathlib import Path

def run(*args):
    return subprocess.check_output(args, text=True).strip()

result = {'services': {}}
for service in ('halo4-dedicated', 'halo4-master'):
    values = dict(line.split('=', 1) for line in run('systemctl', 'show', service,
        '-p', 'User', '-p', 'Group', '-p', 'MainPID', '-p', 'ActiveState',
        '-p', 'FragmentPath', '-p', 'DropInPaths').splitlines())
    pid = values['MainPID']
    if pid != '0':
        status = Path('/proc') / pid / 'status'
        values['process_uid'] = next(line.split()[1:] for line in status.read_text().splitlines() if line.startswith('Uid:'))
    result['services'][service] = values
try:
    account = pwd.getpwnam('halo4-dedicated')
    result['account'] = {'name': account.pw_name, 'uid': account.pw_uid,
        'gid': account.pw_gid, 'home': account.pw_dir, 'shell': account.pw_shell,
        'local': any(line.startswith(account.pw_name + ':') for line in Path('/etc/passwd').read_text().splitlines()),
        'groups': [g.gr_name for g in grp.getgrall() if account.pw_name in g.gr_mem or g.gr_gid == account.pw_gid]}
    result['password_status'] = run('passwd', '-S', account.pw_name).split()[:2]
except KeyError:
    result['account'] = None
result['processes'] = [line for line in run('ps', '-eo', 'user:24,pid,ppid,comm').splitlines()
    if line.split()[0] == 'halo4-dedicated']
print('HALO4_MAINTENANCE:' + json.dumps(result))
