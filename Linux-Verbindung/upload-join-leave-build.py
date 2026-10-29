from pathlib import Path
import subprocess,tempfile,sys
pair=sys.argv[1] if len(sys.argv)>1 else 'join-leave-fix-v9'
if pair not in ('join-leave-fix-v9','coordinator128-v1'):raise SystemExit('Unknown paired candidate')
source=Path(__file__).resolve().parents[1]/'Source/bin'/pair/'Halo4DedicatedServer.exe'
destination='join-leave-v9' if pair=='join-leave-fix-v9' else 'coordinator128-v1'
script='option batch abort\noption confirm off\nopen "root@bitymedia.ch"\nput -transfer=binary "'+str(source)+'" /opt/halo4/Halo4DedicatedServer.exe.'+destination+'\nexit\n'
with tempfile.TemporaryDirectory(prefix='halo4-upload-') as folder:
    p=Path(folder)/'upload.txt';p.write_text(script,encoding='utf-8-sig')
    r=subprocess.run([r'C:\Program Files (x86)\WinSCP\WinSCP.com','/nointeractiveinput','/script='+str(p)],capture_output=True,timeout=180)
    if r.returncode:raise SystemExit('Candidate upload failed, exit '+str(r.returncode))
print('Candidate uploaded; active executable unchanged until deployment.')
