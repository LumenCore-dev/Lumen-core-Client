"""Provide an owned, local null audio endpoint for the headless game process."""
import os
from pathlib import Path
import subprocess
import time

root = Path('/opt/halo4')
unit = Path('/etc/systemd/system/halo4-dedicated.service')
text = unit.read_text()
if 'Description=Halo 4 Dedicated Server under Wine' not in text:
    raise SystemExit('Unexpected server service.')
audio_unit = Path('/etc/systemd/system/halo4-audio.service')
if audio_unit.exists() and 'Description=Halo 4 private silent audio endpoint' not in audio_unit.read_text():
    raise SystemExit('Audio service already used by another installation.')
subprocess.run(['systemctl','stop','halo4-dedicated.service'],check=True)
(root/'pulse-null.pa').write_text('''load-module module-native-protocol-unix socket=/run/halo4-audio/native
load-module module-null-sink sink_name=halo4 rate=48000 channels=2 sink_properties=device.description=Halo4Silent
set-default-sink halo4
set-default-source halo4.monitor
''')
(root/'pulse-null.pa').chmod(0o644)
audio_unit.write_text('''[Unit]
Description=Halo 4 private silent audio endpoint

[Service]
Type=notify
User=halo4-dedicated
Group=halo4-dedicated
RuntimeDirectory=halo4-audio
RuntimeDirectoryMode=0700
Environment=HOME=/opt/halo4 XDG_RUNTIME_DIR=/run/halo4-audio
ExecStart=/usr/bin/pulseaudio --daemonize=no --exit-idle-time=-1 --log-target=journal --disallow-exit=yes --disable-shm=yes -n --file=/opt/halo4/pulse-null.pa
Restart=on-failure
RestartSec=5
TimeoutStartSec=15
NoNewPrivileges=true
PrivateTmp=true
''')
audio_unit.chmod(0o644)
if 'Requires=halo4-audio.service' not in text:
    text = text.replace('After=network-online.target', 'Requires=halo4-audio.service\nAfter=network-online.target halo4-audio.service')
if 'PULSE_SERVER=' not in text:
    text = text.replace('ExecStart=', 'Environment=PULSE_SERVER=unix:/run/halo4-audio/native PULSE_SINK=halo4\nExecStart=')
unit.write_text(text)
unit.chmod(0o644)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','restart','halo4-audio.service'],check=True)
command = ['runuser','-u','halo4-dedicated','--','env','HOME=/opt/halo4','PULSE_SERVER=unix:/run/halo4-audio/native','pactl','info']
for attempt in range(20):
    result = subprocess.run(command,text=True,capture_output=True)
    if result.returncode == 0:
        print('\n'.join(line for line in result.stdout.splitlines() if not line.startswith('Cookie:')),flush=True)
        break
    time.sleep(0.5)
else:
    raise SystemExit('Silent audio endpoint did not become ready: '+result.stderr)
subprocess.run(['systemctl','start','halo4-dedicated.service'],check=True)
print('Headless server restarted with verified silent audio endpoint.',flush=True)
