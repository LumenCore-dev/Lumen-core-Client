"""One slow request per live endpoint, with normal RCON after expiration."""
from concurrent.futures import ThreadPoolExecutor
import json, select, socket, ssl, struct, time
from pathlib import Path
from rcon_client import Client

root=Path('/opt/halo4')
certificate=root/'data/server.tls/server.der'
host='5.199.139.145'
def tls_request(port,protocol,message):
    incoming,outgoing=ssl.MemoryBIO(),ssl.MemoryBIO()
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version=context.maximum_version=ssl.TLSVersion.TLSv1_3
    context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(certificate.read_bytes()))
    context.set_alpn_protocols([protocol])
    tls=context.wrap_bio(incoming,outgoing,server_hostname='halo4.local')
    sock=socket.create_connection((host,port),3)
    while True:
        try:
            tls.do_handshake();sock.sendall(outgoing.read());break
        except ssl.SSLWantReadError:
            sock.sendall(outgoing.read());incoming.write(sock.recv(16384))
    assert tls.getpeercert(binary_form=True)==certificate.read_bytes()
    assert tls.selected_alpn_protocol()==protocol
    tls.write(message)
    return sock,outgoing.read()
def slow(sock,chunks,limit):
    start=time.monotonic();next_send=start;pending=iter(chunks)
    with sock:
        while time.monotonic()-start<limit:
            if time.monotonic()>=next_send:
                try:sock.sendall(next(pending))
                except (BrokenPipeError,ConnectionResetError,StopIteration):return time.monotonic()-start
                next_send=time.monotonic()+.2
            ready,_,_=select.select([sock],[],[],.05)
            if ready:
                try:
                    if not sock.recv(16384):return time.monotonic()-start
                except ConnectionResetError:return time.monotonic()-start
    raise AssertionError('Live endpoint did not enforce deadline')
def lobby():
    sock,record=tls_request(49180,'halo4-lobby/1',b'X'*4096)
    return slow(sock,[record[:5],*[bytes([b]) for b in record[5:]]],18)
def rcon():
    sock,record=tls_request(49182,'halo4-rcon/1',struct.pack('<iii',4096,1,3)+b'X'*4088)
    return slow(sock,[record[:5],*[bytes([b]) for b in record[5:]]],8)
def directory():return slow(socket.create_connection(('127.0.0.1',49175),3),[b'H']*100,5)
with ThreadPoolExecutor(max_workers=3) as pool:
    futures={name:pool.submit(test) for name,test in [('lobby',lobby),('rcon',rcon),('master',directory)]}
    measured={name:round(future.result(),2) for name,future in futures.items()}
assert 13<=measured['lobby']<=18
assert 4<=measured['rcon']<=8
assert 1.5<=measured['master']<=5
with Client(host,49182,(root/'data/rcon-password.txt').read_text().strip(),certificate=certificate) as client:
    status=client.run('status').strip()
    assert status.startswith('SERVER ')
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'live_deadline_seconds':measured,'normal_rcon_afterwards':True,'status':status}))
