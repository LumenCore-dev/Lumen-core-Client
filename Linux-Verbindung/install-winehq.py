"""Add the official WineHQ runtime source, scoped by its own signing key."""
import os
from pathlib import Path
import subprocess
import urllib.request

os.umask(0o022)
base = 'https://dl.winehq.org/wine-builds/'
key_dir = Path('/etc/apt/keyrings')
key_dir.mkdir(mode=0o755, exist_ok=True)
source_path = Path('/etc/apt/sources.list.d/halo4-winehq.sources')
key_path = key_dir / 'halo4-winehq.asc'
if source_path.exists() or key_path.exists():
    raise SystemExit('WineHQ-Konfiguration bereits vorhanden; kein Ueberschreiben.')
key = urllib.request.urlopen(base+'winehq.key', timeout=30).read()
if b'BEGIN PGP PUBLIC KEY BLOCK' not in key:
    raise SystemExit('Unerwartetes Format des WineHQ-Signaturschluessels.')
key_path.write_bytes(key)
key_path.chmod(0o644)
source_path.write_text(f'Types: deb\nURIs: {base}debian\nSuites: trixie\nComponents: main\nArchitectures: amd64\nSigned-By: {key_path}\n')
source_path.chmod(0o644)
subprocess.run(['apt-get','update'],check=True)
subprocess.run(['apt-cache','depends','wine-stable-amd64'],check=True)
subprocess.run(['apt-cache','policy','wine-stable-amd64'],check=True)
