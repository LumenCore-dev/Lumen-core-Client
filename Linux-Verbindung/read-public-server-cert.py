from pathlib import Path
import base64,json,hashlib
certificate=Path('/opt/halo4/data/server.tls/server.der').read_bytes()
print('HALO4_MAINTENANCE:'+json.dumps({'certificate_base64':base64.b64encode(certificate).decode(),'sha256':hashlib.sha256(certificate).hexdigest()}))
