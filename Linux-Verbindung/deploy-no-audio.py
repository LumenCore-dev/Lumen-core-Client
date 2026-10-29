"""Switch this owned service to the dedicated binary with no output backend."""
from pathlib import Path
import shutil
import subprocess

root=Path('/opt/halo4')
unit=Path('/etc/systemd/system/halo4-dedicated.service')
candidate=root/'Halo4DedicatedServer.no-audio-candidate.exe'
if not candidate.is_file() or 'Description=Halo 4 Dedicated Server under Wine' not in unit.read_text():
    raise SystemExit('Candidate or expected owned service is missing.')
subprocess.run(['systemctl','stop','halo4-dedicated.service'],check=True)
backup=root/'Halo4DedicatedServer.exe.before-no-audio'
if not backup.exists():
    shutil.copy2(root/'Halo4DedicatedServer.exe',backup)
backup_unit=Path('/root/halo4-service-before-no-audio.service')
if not backup_unit.exists():
    shutil.copy2(unit,backup_unit)
text=unit.read_text().replace('Requires=halo4-audio.service\n','').replace(' halo4-audio.service','')
text='\n'.join(line for line in text.splitlines() if not line.startswith('Environment=PULSE_SERVER='))+'\n'
unit.write_text(text)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','stop','halo4-audio.service'],check=True)
shutil.copy2(candidate,root/'Halo4DedicatedServer.exe')
subprocess.run(['chown','halo4-dedicated:halo4-dedicated',str(root/'Halo4DedicatedServer.exe')],check=True)
subprocess.run(['systemctl','start','halo4-dedicated.service'],check=True)
print('Started the candidate with the audio helper stopped and no audio dependency.')
