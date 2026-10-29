"""Remove only this task's redundant null audio service after validation."""
from pathlib import Path
import json
import os
import subprocess

root=Path('/opt/halo4')
state=json.loads((root/'data/engine/native-server.json').read_text())
if state.get('status')!='DEDICATED_LOBBY_READY' or state.get('dedicated_audio_disabled') is not True or state.get('dedicated_audio_backend_initialized') is not False:
    raise SystemExit('No verified native no-audio lobby; helper preserved.')
if subprocess.run(['systemctl','is-active','--quiet','halo4-audio.service']).returncode==0:
    raise SystemExit('Audio helper is unexpectedly still running.')
unit=Path('/etc/systemd/system/halo4-audio.service')
if unit.exists():
    if 'Description=Halo 4 private silent audio endpoint' not in unit.read_text():
        raise SystemExit('Unexpected audio service; no removal.')
    unit.unlink()
(root/'pulse-null.pa').unlink(missing_ok=True)
subprocess.run(['systemctl','daemon-reload'],check=True)
simulation=subprocess.run(['apt-get','--simulate','remove','pulseaudio','pulseaudio-utils'],capture_output=True,text=True,check=True)
removed=[line.split()[1] for line in simulation.stdout.splitlines() if line.startswith('Remv ')]
if any(name not in ('pulseaudio','pulseaudio-utils') for name in removed):
    raise SystemExit('Unexpected additional package removals; packages preserved: '+str(removed))
subprocess.run(['apt-get','remove','-y','pulseaudio','pulseaudio-utils'],check=True,env={**os.environ,'DEBIAN_FRONTEND':'noninteractive'})
print('Owned audio helper and its two packages removed; server remains active.')
