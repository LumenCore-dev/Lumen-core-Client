"""Exercise the same RemotePanel calls used by the Windows app."""
import json
from pathlib import Path
import sys
import time

workspace=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(workspace/'Source'))
from desktop.remote import RemotePanel
from webpanel.app import Conflict, revision

cache=workspace/'Server/Remote/vps-5-199-139-145'
panel=RemotePanel(cache,'root@bitymedia.ch','5.199.139.145')
result={'ok':False,'checks':{}}
text=panel.transport.call('config',config='server.cfg')['content']
result['checks']['before_online']=panel.status()['online']
if not result['checks']['before_online']:
    raise RuntimeError('Server must be online before lifecycle test')
players=panel.run('players')
if players.strip()!='PLAYERS 0':
    raise RuntimeError('Players connected; refusing disruptive lifecycle test')
try:
    panel.stop()
    result['checks']['clean_stop']=not panel.pids()
    try:
        panel.save(panel.config,text,'0'*64)
        raise RuntimeError('Stale config revision was accepted')
    except Conflict:
        result['checks']['stale_write_rejected']=True
    result['checks']['save_config']=panel.save(panel.config,text,revision(text))['revision']==revision(text)
    result['checks']['read_back_matches']=panel.transport.call('config',config='server.cfg')['content']==text
finally:
    panel.start()
status=panel.status()
result['checks']['restart_online']=status['online']
result['service']=status['service']
result['server_name']=status['name']
result['rcon_status']=panel.run('status').strip()
result['checks']['players']=panel.run('players').strip()
result['checks']['logs']=len(panel.logs('process'))>0
result['ok']=all(value is True for key,value in result['checks'].items() if key!='players')
report=workspace/'Source/desktop/build/vps-rcon-check.json'
report.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
if not result['ok']:raise SystemExit(1)
