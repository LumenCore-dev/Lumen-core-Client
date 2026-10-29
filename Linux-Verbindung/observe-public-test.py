from pathlib import Path
import json
import shutil
import time
root=Path('/opt/halo4')
folder=root/'public-test-evidence'
folder.mkdir(exist_ok=True)
last=''
for _ in range(55):
    try:
        state=json.loads((root/'data/engine/native-server.json').read_text())
        status=state.get('status','')
        if status!=last:
            print(json.dumps({key:state.get(key) for key in ('status','phase','error','map_loaded','world_state_verified','native_peer_membership','dedicated_audio_backend_initialized')}),flush=True)
            last=status
        if state.get('status')=='DEDICATED_WORLD_READY':
            (folder/'native-server.json').write_text(json.dumps(state,indent=2))
            for name in ('dedicated-units.jsonl','native-packet-samples.json'):
                path=root/'data/engine'/name
                if path.is_file():shutil.copy2(path,folder/name)
    except (OSError,ValueError):pass
    time.sleep(1)
