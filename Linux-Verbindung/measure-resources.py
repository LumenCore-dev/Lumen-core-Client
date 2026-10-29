"""Read-only 10-second resource sample of the owned services and VPS."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time

names=('halo4-dedicated','halo4-master')
def services():
    result={}
    for name in names:
        raw=subprocess.check_output(['systemctl','show',name,'-p','ControlGroup','-p','ActiveState','-p','MainPID'],text=True)
        props=dict(line.split('=',1) for line in raw.splitlines() if '=' in line)
        group=Path('/sys/fs/cgroup')/props['ControlGroup'].lstrip('/')
        cpu=dict(line.split() for line in (group/'cpu.stat').read_text().splitlines())
        result[name]={'state':props['ActiveState'],'pid':int(props['MainPID']),'cpu_usec':int(cpu['usage_usec']),'memory_bytes':int((group/'memory.current').read_text()),'memory_peak_bytes':int((group/'memory.peak').read_text())}
    return result
def cpu():
    return list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
first=services();cpu_first=cpu();start=time.monotonic()
time.sleep(10)
elapsed=time.monotonic()-start;second=services();cpu_second=cpu()
cores=os.cpu_count()
for name,data in second.items():
    data['cpu_percent_one_core']=(data.pop('cpu_usec')-first[name]['cpu_usec'])/1e6/elapsed*100
    data['cpu_percent_total_vps']=data['cpu_percent_one_core']/cores
memory={line.split(':',1)[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()}
delta=[b-a for a,b in zip(cpu_first,cpu_second)];total=sum(delta)
result={'sample_seconds':elapsed,'vcpus':cores,'services':second,'vps_cpu_busy_percent':100*(total-delta[3]-delta[4])/total,'vps_cpu_iowait_percent':100*delta[4]/total,'vps_cpu_steal_percent':100*delta[7]/total,'vps_ram_total_bytes':memory['MemTotal'],'vps_ram_available_bytes':memory['MemAvailable'],'vps_ram_used_bytes':memory['MemTotal']-memory['MemAvailable'],'swap_total_bytes':memory['SwapTotal'],'load_average':os.getloadavg()}
state=json.loads(Path('/opt/halo4/data/engine/native-server.json').read_text())
result['game']={key:state.get(key) for key in ('status','map','map_loaded','native_player_membership')}
sys.path.insert(0,'/opt/halo4')
from rcon_client import Client
with Client('127.0.0.1',49182,Path('/opt/halo4/data/rcon-password.txt').read_text().strip(),certificate=Path('/opt/halo4/data/server.tls/server.der')) as client:
    result['game_status']=client.run('status').strip()
print(json.dumps(result,indent=2),flush=True)
