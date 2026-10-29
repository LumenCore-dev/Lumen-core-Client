"""Run a reviewed Python maintenance file through the existing WinSCP session."""
import base64
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
# Root maintenance must not import code from the game user's writable tree.
# Supply the reviewed workstation copy before older maintenance files import it.
trusted_rcon = (Path(__file__).resolve().parents[1] / 'Source/tools/rcon_client.py').read_text(encoding='utf-8-sig')
source = ('import sys, types\n'
          '_maintenance_rcon = types.ModuleType("rcon_client")\n'
          '_maintenance_rcon.__maintenance_source__ = ' + repr(trusted_rcon) + '\n'
          'exec(_maintenance_rcon.__maintenance_source__, _maintenance_rcon.__dict__)\n'
          'sys.modules["rcon_client"] = _maintenance_rcon\n' + source)
timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 180
if sys.argv[3:] not in ([], ['--service-user']):
    raise SystemExit('Optional execution mode: --service-user')
remote_python = 'runuser -u halo4-dedicated -- python3' if sys.argv[3:] else 'python3'
if not 30 <= timeout <= 1800:
    raise SystemExit('Maintenance timeout must be 30..1800 seconds')
encoded = base64.b64encode(source.encode()).decode("ascii")
command = "import base64;exec(base64.b64decode(" + repr(encoded) + "))"
script = 'option batch abort\noption confirm off\nopen "root@bitymedia.ch" -timeout=' + str(timeout) + '\ncall ' + remote_python + ' -I -c ' + shlex.quote(command) + '\nexit\n'
with tempfile.TemporaryDirectory(prefix="halo4-maintenance-") as directory:
    path = Path(directory) / "script.txt"
    path.write_text(script, encoding="utf-8-sig")
    result = subprocess.run([r"C:\Program Files (x86)\WinSCP\WinSCP.com", "/nointeractiveinput", "/script=" + str(path)], capture_output=True, timeout=timeout)
output = result.stdout.decode("utf-8", errors="replace")
marker = "HALO4_MAINTENANCE:"
rows = [line[len(marker):] for line in output.splitlines() if line.startswith(marker)]
if not rows:
    # Show Python diagnostics only; never echo the stored SSH session or command.
    trace = output.find('Traceback (most recent call last):')
    if trace >= 0:
        print('\n'.join(line for line in output[trace:].splitlines() if len(line)<400 and 'base64' not in line and not set(line.strip())<=set('~^'))[-2500:])
    else:
        import re
        diagnostics = output + '\n' + result.stderr.decode('utf-8', errors='replace')
        for line in diagnostics.splitlines():
            if len(line)<350 and re.search(r'error|failed|cannot|fehler|exception|exit|return code|command.*long',line,re.I) and not re.search(r'base64|password|passwort|root@|session|authenticat',line,re.I):
                print(line)
    raise SystemExit("SSH maintenance failed; no structured result returned (exit " + str(result.returncode) + ").")
report = json.loads(rows[-1])
print(json.dumps(report, ensure_ascii=True, indent=2))
if not report.get("ok", True) or result.returncode:
    raise SystemExit(1)
