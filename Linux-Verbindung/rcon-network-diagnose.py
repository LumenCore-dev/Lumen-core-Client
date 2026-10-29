import json,subprocess
from pathlib import Path
def run(*args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=15);return {'code':p.returncode,'out':p.stdout[-13000:],'error':p.stderr[-1000:]}
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'network_unit':run('systemctl','cat','halo4-network.service'),'firewall':run('iptables','-S','INPUT'),'listener':run('ss','-lntp'),'service':run('systemctl','is-active','halo4-dedicated.service')}))
