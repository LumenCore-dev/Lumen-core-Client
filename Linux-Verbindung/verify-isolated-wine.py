"""Wine/RCON startup check in a unique directory and prefix as the service user.

TEST_SPEC is supplied by run-isolated-wine-test.py. Production services and
their binaries, database, certificates and Wine prefix are never modified.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import time
from rcon_client import Client

if 'TEST_SPEC' not in globals():
    raise RuntimeError('Use run-isolated-wine-test.py to supply the immutable test spec')
stage = Path(TEST_SPEC['directory'])
if stage.parent != Path('/var/tmp') or not stage.name.startswith('halo4-maintainability-'):
    raise RuntimeError('Invalid isolated test directory')
if os.getuid() == 0:
    raise RuntimeError('Run this test with --service-user')
binary = stage/'Halo4DedicatedServer.exe'
if hashlib.sha256(binary.read_bytes()).hexdigest() != TEST_SPEC['sha256']:
    raise RuntimeError('Uploaded binary differs from the reviewed test spec')
work = stage/'test'
work.mkdir(mode=0o700)
game = work/'game'
(game/'halo4').mkdir(parents=True)
(game/'MCC/Binaries/Win64').mkdir(parents=True)
for item in Path('/opt/halo4/game/halo4').iterdir():
    target = game/'halo4'/item.name
    if item.suffix.lower() == '.dll':
        shutil.copy2(item, target)
    else:
        target.symlink_to(item, target_is_directory=item.is_dir())
shutil.copy2('/opt/halo4/game/MCC/Binaries/Win64/bink2w64.dll', game/'MCC/Binaries/Win64/bink2w64.dll')
# Bind zero to choose unused local ports without reusing production endpoints.
reservations = []
for _ in range(2):
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    reservations.append(sock)
lobby_port, rcon_port = [sock.getsockname()[1] for sock in reservations]
(work/'server.cfg').write_text(f'''game_directory = game
bind = 127.0.0.1:{lobby_port}
name = Isolated maintenance validation
network = lan
database = data/server.sqlite3
mode = multiplayer
map = wraparound
map_pool = wraparound
max_players = 128
min_players = 1
headless = true
console = false
rcon_bind = 127.0.0.1:{rcon_port}
rcon_password_file = data/rcon-password.txt
''')
env = os.environ.copy()
env.update(WINEPREFIX=str(work/'.wine'), WINEARCH='win64', WINEDEBUG='-all',
           WINEDLLOVERRIDES='mscoree,mshtml=', HALO4_WIDE_SESSION_BANK='1',
           HALO4_CAPACITY_LAB_PLAYERS='128', HALO4_HEADLESS_CPU_GRAPHICS_PROBE='1',
           HALO4_HEADLESS_NO_D3D_PROBE='1', HALO4_HEADLESS_DYNAMIC_ARENA='1')
wine = '/opt/wine-stable/lib/wine/x86_64-unix/wine'
result = {'status': 'FAILED', 'uid': os.getuid(), 'serverSha256': TEST_SPEC['sha256'],
          'directory': str(work), 'productionDeploymentPerformed': False, 'gameplayVerified': False}
process = None
try:
    for sock in reservations:
        sock.close()
    with (work/'wine.log').open('wb') as log:
        process = subprocess.Popen(['xvfb-run', '-a', '--server-args=-screen 0 1280x720x24 -nolisten tcp',
                                    wine, str(binary), '--config', 'server.cfg'], cwd=work, env=env,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic()+100
        state = {}
        while time.monotonic() < deadline:
            report = work/'data/engine/native-server.json'
            if report.exists():
                try:
                    state = json.loads(report.read_text())
                except ValueError:
                    pass
            if process.poll() is not None:
                raise RuntimeError('Owned Wine host exited: '+str(state.get('error')))
            if state.get('status') == 'DEDICATED_LOBBY_READY' and (work/'data/rcon-password.txt').exists():
                secret = (work/'data/rcon-password.txt').read_text().strip()
                try:
                    with Client('127.0.0.1', rcon_port, secret, certificate=work/'data/server.tls/server.der') as client:
                        status = client.run('status')
                        if 'players=0' not in status:
                            raise RuntimeError('Unexpected isolated lobby membership')
                        result['rconStatus'] = status
                        result['rconStop'] = client.run('stop')
                    result['status'] = 'WINE_LOBBY_RCON_VERIFIED'
                    result['lobbyStatus'] = state['status']
                    result['sessionBankWide'] = state.get('session_bank_wide')
                    break
                except (OSError, TimeoutError):
                    pass
            time.sleep(.25)
        else:
            raise TimeoutError('Isolated Wine lobby/RCON not ready')
except Exception as error:
    result['error'] = str(error)
finally:
    for sock in reservations:
        sock.close()
    if process is not None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
    # Scope the Wine server shutdown to this test's unique prefix.
    wineserver = Path('/opt/wine-stable/bin/wineserver')
    if wineserver.exists():
        subprocess.run([str(wineserver), '-k'], env=env, capture_output=True, timeout=15)
    result['ownedLauncherStopped'] = process is None or process.poll() is not None
    result['servicesAfter'] = {name: subprocess.run(['systemctl', 'is-active', name], capture_output=True,
                              text=True).stdout.strip() for name in ('halo4-master', 'halo4-dedicated')}
    (work/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print('HALO4_MAINTENANCE:'+json.dumps(result))
