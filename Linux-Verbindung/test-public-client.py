from pathlib import Path
import importlib.util
import json
import socket
import subprocess
import time

root=Path(r'D:\Halo4-Server')
folder=root/'reports/public-vps-test-20261016'
folder.mkdir(exist_ok=False)
engine='7c53e7d5bc9848545a1b70e2768242479336fba1b7630d7ab955f7fd0c34fa84'
with socket.create_connection(('5.199.139.145',49175),timeout=4) as stream:
    stream.sendall(f'H4LIST 1 {engine}\n'.encode())
    listing=stream.recv(16384).decode().strip()
    if '5.199.139.145:49180' not in listing:raise SystemExit('Public directory entry is missing: '+listing)
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as stream:
    stream.settimeout(4)
    stream.sendto(f'H4DISCOVER 1 1234567890abcdef {engine}'.encode(),('5.199.139.145',49180))
    discovery=stream.recv(4096).decode()
    if not discovery.startswith('H4SERVER 1 1234567890abcdef '):raise SystemExit('Invalid public discovery response.')
print('Public master listing and UDP discovery verified.',flush=True)
spec=importlib.util.spec_from_file_location('acceptance',root/'Source/server/tests/dedicated_server.py')
acceptance=importlib.util.module_from_spec(spec);spec.loader.exec_module(acceptance)
report=folder/'native-client.json'
args=[str(root/'Client/Halo4NativeClient.exe'),'--self-test-direct-connect','5.199.139.145:49180','--self-test-signed-identity','--map','ca_blood_crash','--master-address','5.199.139.145:49175','--game-dir',r'E:\SteamLibrary\steamapps\common\Halo The Master Chief Collection','--output',str(report)]
process=subprocess.Popen(args,cwd=root/'Client')
print('Owned test client PID: '+str(process.pid),flush=True)
deadline=time.monotonic()+150
last=''
try:
    while time.monotonic()<deadline:
        state=acceptance.read_json(report)
        status=state.get('status','pending')
        if status!=last:
            print('Client: '+status+' '+state.get('error',''),flush=True);last=status
        if process.poll() is not None:break
        time.sleep(1)
    else:raise RuntimeError('Public client test timed out.')
    state=acceptance.read_json(report)
    controls=acceptance.control_evidence(folder/'network-control.jsonl')
    result={'status':'PUBLIC_CLIENT_CONTROL_VERIFIED' if state.get('map_loaded') and state.get('world_state_verified') and state.get('native_join_requested') and controls.get('verified') and process.returncode==0 else 'PUBLIC_CLIENT_TEST_FAILED','exit_code':process.returncode,'master_listing':listing,'discovery':discovery,'client_status':state.get('status'),'client_error':state.get('error'),'map_loaded':state.get('map_loaded'),'world_state_verified':state.get('world_state_verified'),'native_join_requested':state.get('native_join_requested'),'controls':controls}
    (folder/'validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2),flush=True)
finally:
    if process.poll() is None:
        process.terminate();process.wait(timeout=15)
