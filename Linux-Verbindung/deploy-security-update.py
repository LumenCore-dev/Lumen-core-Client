"""Deploy only deadline fixes with an empty lobby and automatic binary rollback."""
from pathlib import Path
import hashlib, json, os, pwd, shutil, subprocess, sys, time

root=Path('/opt/halo4')
candidates=Path('/root/halo4-security-update')
expected={
    'Halo4DedicatedServer.exe':'d80cb03d7820307cc72266a9c1520b876c80b28fab9561d54ce09ec428dfd631',
    'Halo4LobbyServer.exe':'99ea137c729436d081a4ce8b2d513bb3df16a4f8500804db2356d38f32b0285e'}
original={
    'Halo4DedicatedServer.exe':'e5cea56bc4a9fbc054ccc9fcb62e1580256daed6a64eacc90112e0f1b03ee843',
    'Halo4LobbyServer.exe':'505977ba80da892e8da656d2661934340042cee32a231b7bcfaa9549661173c7'}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for name,value in expected.items():assert digest(candidates/name)==value,'Unexpected candidate'
for name,value in original.items():assert digest(root/name)==value,'Live binary changed since review'
config_before={name:digest(root/name) for name in ('server.cfg','server-policy.cfg')}
account=pwd.getpwnam('halo4-dedicated')
trusted_client=sys.modules['rcon_client'].__maintenance_source__
health_source=trusted_client+'''
import json
root=Path('/opt/halo4');values={}
for line in (root/'server.cfg').read_text().splitlines():
    if '=' in line and not line.strip().startswith(('#',';')):
        key,value=line.split('=',1);values[key.strip()]=value.strip()
host,port=values['rcon_bind'].rsplit(':',1)
with Client(host,int(port),(root/values['rcon_password_file']).read_text().strip(),certificate=root/'data/server.tls/server.der') as client:
    print(json.dumps({'status':client.run('status').strip(),'players':client.run('players').strip()}))
'''
# Suppress the CLI main guard when executing the reviewed module as a script.
health_source="__name__='halo4_maintenance_health'\n"+health_source
def health():
    return json.loads(subprocess.check_output(['runuser','-u',account.pw_name,'--','/usr/bin/python3','-I','-c',health_source],text=True,stderr=subprocess.PIPE,timeout=15))
def systemctl(*args):
    return subprocess.check_output(['systemctl',*args],text=True,stderr=subprocess.PIPE,timeout=45).strip()
assert health()['players']=='PLAYERS 0','Players connected; deployment deferred'
backup=Path('/root')/('halo4-before-security-update-'+str(time.time_ns()))
backup.mkdir(mode=0o700)
for name in original:shutil.copy2(root/name,backup/name)
def install(source,destination):
    # Never follow a symlink in the game-writable directory during root writes.
    directory=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    staging='.security-install-'+os.urandom(16).hex()
    try:
        fd=os.open(staging,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
        with os.fdopen(fd,'wb') as output:
            output.write(source.read_bytes());output.flush();os.fsync(output.fileno())
            os.fchown(output.fileno(),account.pw_uid,account.pw_gid)
        os.replace(staging,destination.name,src_dir_fd=directory,dst_dir_fd=directory)
    finally:
        try:os.unlink(staging,dir_fd=directory)
        except FileNotFoundError:pass
        os.close(directory)
database_names=('server.sqlite3','server.sqlite3-wal','master.sqlite3','master.sqlite3-wal')
databases_saved=False
try:
    systemctl('stop','halo4-dedicated','halo4-master')
    # Services are stopped, so SQLite and its WAL can be backed up consistently.
    for name in database_names:
        source=root/'data'/name
        if source.exists():shutil.copy2(source,backup/name)
    databases_saved=True
    for name in expected:install(candidates/name,root/name)
    started=time.time()
    systemctl('start','halo4-master','halo4-dedicated')
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        try:
            response=health()
            state_path=root/'data/engine/native-server.json'
            state=json.loads(state_path.read_text())
            if response['status'].startswith('SERVER ') and state.get('status') in ('DEDICATED_LOBBY_READY','DEDICATED_WORLD_READY') and state_path.stat().st_mtime>=started:
                break
        except (OSError,ValueError,subprocess.SubprocessError):pass
        time.sleep(1)
    else:raise RuntimeError('Fresh native server did not become ready')
    assert all(digest(root/name)==value for name,value in expected.items())
    assert all(digest(root/name)==value for name,value in config_before.items()),'Configuration changed'
    assert all(systemctl('is-active',name)=='active' for name in ('halo4-master','halo4-dedicated'))
except Exception:
    systemctl('stop','halo4-dedicated','halo4-master')
    for name in original:install(backup/name,root/name)
    if databases_saved:
        for name in database_names:
            if (backup/name).exists():install(backup/name,root/'data'/name)
        directory=os.open(root/'data',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            for name in (*[name for name in database_names if not (backup/name).exists()], 'server.sqlite3-shm','master.sqlite3-shm'):
                try:os.unlink(name,dir_fd=directory)
                except FileNotFoundError:pass
        finally:os.close(directory)
    systemctl('start','halo4-master','halo4-dedicated')
    raise
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'security_binaries':expected,'configuration_preserved':True,
    'fresh_native_status':state['status'],'status':response['status'],'backup':str(backup)}))
