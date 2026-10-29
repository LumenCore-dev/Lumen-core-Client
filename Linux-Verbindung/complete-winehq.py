from pathlib import Path
import os
import subprocess

path = Path('/etc/apt/sources.list.d/halo4-winehq.sources')
text = path.read_text()
if 'URIs: https://dl.winehq.org/wine-builds/debian' not in text:
    raise SystemExit('Unerwartete Paketquelle.')
path.write_text(text.replace('Architectures: amd64\n', 'Architectures: amd64 i386\n'))
subprocess.run(['dpkg','--add-architecture','i386'],check=True)
subprocess.run(['apt-get','update'],check=True)
subprocess.run(['apt-get','install','-y','--no-remove','--no-install-recommends','wine-stable=11.0.0.0~trixie-1'],check=True,env={**os.environ,'DEBIAN_FRONTEND':'noninteractive'})
