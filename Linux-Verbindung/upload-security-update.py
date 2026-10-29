"""Stage reviewed server binaries in a root-only directory on the owned VPS."""
from pathlib import Path
import subprocess, sys, tempfile

dedicated, master = (Path(value).resolve(strict=True) for value in sys.argv[1:])
script = ('option batch abort\noption confirm off\nopen "root@bitymedia.ch"\n'
    'call install -d -m 700 -o root -g root /root/halo4-security-update\n'
    'put -transfer=binary "'+str(dedicated)+'" /root/halo4-security-update/Halo4DedicatedServer.exe\n'
    'put -transfer=binary "'+str(master)+'" /root/halo4-security-update/Halo4LobbyServer.exe\nexit\n')
with tempfile.TemporaryDirectory(prefix='halo4-security-upload-') as directory:
    path=Path(directory)/'upload.txt';path.write_text(script,encoding='utf-8-sig')
    result=subprocess.run([r'C:\Program Files (x86)\WinSCP\WinSCP.com','/nointeractiveinput','/script='+str(path)],capture_output=True,timeout=180)
    if result.returncode:raise SystemExit('Security binary upload failed (exit '+str(result.returncode)+')')
print('Security binaries staged in root-only server directory')
