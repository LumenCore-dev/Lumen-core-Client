"""Non-destructive live validation; run as the dedicated service account."""
import json, os, pwd, socket, ssl, subprocess
from pathlib import Path
from rcon_client import Client

root=Path('/opt/halo4')
assert os.geteuid()==pwd.getpwnam('halo4-dedicated').pw_uid
values={}
for line in (root/'server.cfg').read_text().splitlines():
    if '=' in line and not line.strip().startswith(('#',';')):
        key,value=line.split('=',1);values[key.strip()]=value.strip()
host,port=values['rcon_bind'].rsplit(':',1)
secret=(root/values['rcon_password_file']).read_text().strip()
certificate=root/'data/server.tls/server.der'
with Client(host,int(port),secret,certificate=certificate) as client:
    assert client.stream.version()=='TLSv1.3'
    status=client.run('status').strip()
    players=client.run('players').strip()
    assert status.startswith('SERVER ')
try:
    with Client(host,int(port),'invalid-test-password-0000000000',certificate=certificate):
        raise AssertionError('Invalid password accepted')
except PermissionError:
    pass
for name in ('halo4-master','halo4-dedicated'):
    state=subprocess.check_output(['systemctl','show',name,'-p','User','-p','ActiveState'],text=True)
    assert 'User=halo4-dedicated' in state and 'ActiveState=active' in state
for name in ('halo4-firewall.py','halo4-rcon-firewall.py'):
    path=Path('/usr/local/libexec/halo4')/name
    assert not os.access(path,os.W_OK) and not os.access(path.parent,os.W_OK)
for service in ('halo4-network','halo4-rcon-network'):
    commands=subprocess.check_output(['systemctl','show',service,'-p','ExecStart','-p','ExecStop'],text=True)
    assert '/opt/halo4/' not in commands and '-I /usr/local/libexec/halo4/' in commands
retention=subprocess.check_output(['systemctl','show','halo4-log-retention','-p','User','-p','Result'],text=True)
assert 'User=halo4-dedicated' in retention and 'Result=success' in retention
with socket.create_connection(('127.0.0.1',49175),3) as stream:
    stream.sendall(b'H4LIST 1 7c53e7d5bc9848545a1b70e2768242479336fba1b7630d7ab955f7fd0c34fa84\n')
    assert stream.recv(4096).startswith(b'H4SERVERS ')
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'tls':'TLSv1.3','wrong_rcon_password_rejected':True,
    'protected_helpers_not_writable':True,'firewall_imports_isolated':True,'log_retention_unprivileged':True,
    'directory_responds':True,'both_services_unprivileged_and_active':True,'status':status,'players':players}))
