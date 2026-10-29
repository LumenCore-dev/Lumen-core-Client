from pathlib import Path
import subprocess,tempfile
source=Path(__file__).resolve().parents[1]/'Source/bin/session-leave-v1/Halo4DedicatedServer.exe'
script='option batch abort\noption confirm off\nopen "root@bitymedia.ch"\nput -transfer=binary "'+str(source)+'" /opt/halo4/Halo4DedicatedServer.exe.session-leave-v1\nexit\n'
with tempfile.TemporaryDirectory(prefix='halo4-counter-upload-') as folder:
 p=Path(folder)/'upload.txt';p.write_text(script,encoding='utf-8-sig')
 r=subprocess.run([r'C:\Program Files (x86)\WinSCP\WinSCP.com','/nointeractiveinput','/script='+str(p)],capture_output=True,timeout=180)
 if r.returncode:raise SystemExit('Upload failed: '+str(r.returncode))
print('Visitor counter candidate uploaded')
