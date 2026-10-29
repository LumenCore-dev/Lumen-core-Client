import json,os,pwd,subprocess,tempfile,time
from pathlib import Path
account=pwd.getpwnam('halo4-dedicated')
assert os.geteuid()==account.pw_uid, 'Run with run-maintenance.py --service-user'
with tempfile.TemporaryDirectory(prefix='halo-log-test-') as temp:
    root=Path(temp);log=root/'server-core.log'
    log.write_bytes(b'x'*(21*1024*1024))
    config=root/'rotate.conf'
    config.write_text(f'{log} {{\n size 20M\n rotate 4\n copytruncate\n compress\n}}\n')
    with log.open('ab') as writer:
        subprocess.run(['logrotate','-s',str(root/'state'),str(config)],check=True,capture_output=True)
        assert log.stat().st_size==0 and Path(str(log)+'.1.gz').exists()
        writer.write(b'after rotation\n');writer.flush()
        assert log.read_bytes()==b'after rotation\n'
    expired=root/'errors.jsonl';expired.write_text('expired')
    asset=root/'keep.bin';asset.write_text('keep')
    old=time.time()-15*86400
    os.utime(expired,(old,old));os.utime(asset,(old,old));os.utime(log,(old,old))
    helper=Path('/usr/local/sbin/halo4-log-retention').read_text().replace("root=Path('/opt/halo4/data/engine')",'root=Path('+repr(str(root))+')')
    with log.open('ab'):
        subprocess.run(['python3','-I','-c',helper],check=True,capture_output=True)
        assert log.exists() and asset.exists() and not expired.exists()
    subprocess.run(['python3','-I','-c',helper],check=True,capture_output=True)
    assert not log.exists() and asset.exists()
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'rotation_and_compression':True,'writer_continues_after_rotation':True,'expired_logs_removed':True,'open_logs_preserved':True,'non_log_files_preserved':True}))
