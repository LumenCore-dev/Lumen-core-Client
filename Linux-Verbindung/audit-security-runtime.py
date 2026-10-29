"""Read-only Halo 4 deployment security inventory. Never print secrets."""
import json, os, stat, subprocess
from pathlib import Path

def run(*args):
    p = subprocess.run(args, text=True, capture_output=True, timeout=25)
    return {'exit': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()[:500]}

root = Path('/opt/halo4')
result = {'ok': True}
result['sockets'] = [line for line in run('ss', '-lntup')['stdout'].splitlines() if any(p in line for p in (':49175', ':49180', ':49181', ':49182', 'Xvfb'))]
result['services'] = {}
for name in ('halo4-dedicated', 'halo4-master', 'halo4-network'):
    result['services'][name] = run('systemctl', 'show', name,
        '-p', 'User', '-p', 'Group', '-p', 'ActiveState', '-p', 'MainPID',
        '-p', 'NoNewPrivileges', '-p', 'PrivateTmp', '-p', 'ProtectSystem',
        '-p', 'ProtectHome', '-p', 'CapabilityBoundingSet', '-p', 'UMask',
        '-p', 'ReadWritePaths', '-p', 'RestrictSUIDSGID')
result['firewall'] = [line.strip() for line in run('iptables-save')['stdout'].splitlines() if any(word in line for word in ('halo4','49175','49180','49181','49182'))]
result['privileged_units'] = {}
for p in Path('/etc/systemd/system').glob('halo4*'):
    if p.is_file() and not p.is_symlink():
        result['privileged_units'][str(p)] = p.read_text()
result['root_helpers'] = []
for p in root.glob('*.py'):
    s = p.stat()
    result['root_helpers'].append({'path':str(p),'uid':s.st_uid,'mode':oct(stat.S_IMODE(s.st_mode))})
result['config'] = {}
allowed = {'bind','port','rcon_bind','rcon_password_file','database','network',
    'require_identity','require_signed_identity','allow_unsigned_clients','masters',
    'policy','native_bind','native_port','log_file','allow_remote_rcon'}
for name in ('server.cfg', 'server-policy.cfg'):
    p = root / name
    if p.exists():
        result['config'][name] = [line for line in p.read_text().splitlines()
            if '=' in line and line.split('=',1)[0].strip() in allowed]
result['permissions'] = []
for relative in ('', 'server.cfg','server-policy.cfg','data','data/rcon-password.txt',
    'data/server.tls','data/server.tls/server.key','data/server.tls/server.der',
    'data/master.sqlite3','rcon_client.py'):
    p = root / relative
    if p.exists():
        s = p.stat()
        result['permissions'].append({'path': str(p), 'mode': oct(stat.S_IMODE(s.st_mode)),
            'uid': s.st_uid, 'gid': s.st_gid, 'symlink': p.is_symlink()})
result['sensitive_file_permissions'] = []
for base in (root / 'data', root):
    for p in (base.iterdir() if base.exists() else []):
        if p.is_file() and any(word in p.name.lower() for word in ('password','token','.key','.pem','sqlite')):
            s = p.stat()
            result['sensitive_file_permissions'].append({'path':str(p),'mode':oct(stat.S_IMODE(s.st_mode)),'uid':s.st_uid})
state = root / 'data/engine/native-server.json'
if state.exists():
    data = json.loads(state.read_text())
    result['engine'] = {k:data.get(k) for k in ('status','phase','error','map_loaded')}
result['halo_processes'] = [line for line in run('ps','-eo','user:24,pid,ppid,comm')['stdout'].splitlines()
    if line.split()[0] == 'halo4-dedicated']
print('HALO4_MAINTENANCE:' + json.dumps(result))
