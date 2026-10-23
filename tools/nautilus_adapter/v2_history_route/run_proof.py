"""Offline BOOTSTRAP-REPLAY-02 controller. Redis native clones are test fixtures only."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from decimal import Decimal

BINARY = Path('/tmp/cpw-target/debug/cpw-n2-history-route')
ROOT = Path('/evidence/physical')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def redis(port, *args, data=None):
    command = ['redis-cli', '-p', str(port), '--raw']
    if data is not None:
        command.append('-x')
    result = subprocess.run(command + list(args), input=data, capture_output=True, timeout=10)
    assert result.returncode == 0 and not result.stdout.startswith(b'ERR '), result.stderr + result.stdout
    return result.stdout.removesuffix(b'\n')


def native_records(port):
    return {key.decode(): redis(port, 'DUMP', key.decode())
            for key in sorted(redis(port, '--scan').splitlines())}


def contents(port):
    """Native record contents; normalize unordered index sets, never economic data."""
    result = {}
    for key in native_records(port):
        kind = redis(port, 'TYPE', key).decode()
        command = {'string': ['GET', key], 'list': ['LRANGE', key, '0', '-1'],
                   'set': ['SMEMBERS', key], 'hash': ['HGETALL', key]}[kind]
        raw = subprocess.check_output(['redis-cli', '-p', str(port), '--json'] + command)
        value = json.loads(raw)
        if kind == 'set':
            value.sort()
        result[key] = {'type': kind, 'value': value}
    return result


def hashes(records):
    return {key: sha(value) for key, value in records.items()}


def files(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def start_redis(directory, port, records=None, expected_contents=None):
    directory.mkdir()
    with (directory / 'redis.log').open('wb') as log:
        process = subprocess.Popen(['redis-server', '--bind', '127.0.0.1', '--port', str(port),
            '--appendonly', 'yes', '--appendfsync', 'always', '--save', '', '--dir', str(directory)],
            stdout=log, stderr=subprocess.STDOUT)
    deadline = time.monotonic() + 10
    while True:
        assert process.poll() is None, (directory / 'redis.log').read_text()
        check = subprocess.run(['redis-cli', '-p', str(port), 'PING'], capture_output=True)
        if check.returncode == 0:
            break
        assert time.monotonic() < deadline
        time.sleep(.05)
    assert redis(port, 'DBSIZE') == b'0'
    if records:
        for key, value in records.items():
            assert redis(port, 'RESTORE', key, '0', data=value) == b'OK'
        # Native RESTORE can re-encode unordered sets. Preserve input DUMPs and
        # record raw differences; require native type/content equality separately.
        assert contents(port) == expected_contents, 'native clone contents differ'
    return process


def stop_redis(process, port):
    redis(port, 'SHUTDOWN')
    process.wait(timeout=10)
    assert process.returncode == 0


def child(root, mode, label, checkpoint, source, records, source_contents, fault=None):
    target = root / label
    target.mkdir()
    shutil.copyfile(checkpoint, target / 'checkpoint.json')
    shutil.copytree(source, target / 'event_store')
    clone = start_redis(target / 'redis', 6398, records, source_contents)
    before = native_records(6398)
    clone_contents = contents(6398)
    try:
        mutation = fault(target) if fault else None
        fault_before = native_records(6398)
        content_before = contents(6398)
        source_before = files(target / 'event_store')
        result = subprocess.run([str(BINARY), mode, str(target)],
            env=dict(os.environ, CPW_ROUTE_REDIS_PORT='6398'), capture_output=True, timeout=60)
        (target / 'child.log').write_bytes(result.stdout + result.stderr)
        time.sleep(.1)  # Drain queued native writes before observing the disposable clone.
        after = native_records(6398)
        content_after = contents(6398)
        def read(name):
            path = target / name
            return json.loads(path.read_bytes()) if path.exists() else None
        row = {'mode': mode, 'exit': result.returncode, 'process': read('restore-process.json'),
            'native_receipt': read('restore-receipt.json'), 'collision_receipt': read('collision-receipt.json'),
            'mutation': mutation, 'native_clone_exact': before == records,
            'native_clone_content_equal': clone_contents == source_contents,
            'contents_before': content_before, 'contents_after': content_after,
            'content_changed_keys': [key for key in sorted(set(content_before) | set(content_after))
                                     if content_before.get(key) != content_after.get(key)],
            'records_before': hashes(fault_before), 'records_after': hashes(after),
            'changed_keys': [key for key in sorted(set(fault_before) | set(after)) if fault_before.get(key) != after.get(key)],
            'source_files_before': source_before, 'source_files_after': files(target / 'event_store'),
            'checkpoint_after': sha((target / 'checkpoint.json').read_bytes())}
        save(target / 'controller-receipt.json', row)
        return row
    finally:
        stop_redis(clone, 6398)


def mutate_identity(field):
    def mutate(target):
        path = target / 'checkpoint.json'
        data = json.loads(path.read_bytes())
        data[field] = ('00000000-0000-4000-8000-000000000001' if field == 'instance_id' else 'wrong-' + field)
        save(path, data)
        return {'checkpoint_field': field}
    return mutate


def mutate_snapshot(kind):
    def mutate(target):
        keys = [key for key in native_records(6398) if 'position-snapshots' in key]
        assert len(keys) == 1, keys
        key = keys[0]
        value = redis(6398, 'GET', key)
        if kind == 'missing':
            redis(6398, 'DEL', key)
        else:
            redis(6398, 'SET', key, data=(b'corrupt' if kind == 'corrupt' else value[:len(value)//2]))
        return {'snapshot': kind, 'key': key}
    return mutate


def mutate_anchor(kind):
    def mutate(target):
        path = next((target / 'event_store').rglob('*.redb'))
        if kind == 'missing':
            path.unlink()
        else:
            path.write_bytes(b'corrupt' if kind == 'corrupt' else path.read_bytes()[:32])
        return {'native_anchor_source': kind}
    return mutate


def main():
    assert not ROOT.exists(), 'fresh physical evidence required'
    assert len(Path('/proc/net/route').read_text().splitlines()) == 1, 'external network present'
    ROOT.mkdir()
    started = time.monotonic()
    matrix = {'controller_pid': os.getpid(), 'binary_sha256': sha(BINARY.read_bytes()), 'cases': []}
    for scenario in ('round_trip', 'reversal'):
        for termination in ('healthy', 'crash'):
            root = ROOT / f'{scenario}_{termination}'
            root.mkdir()
            authority = start_redis(root / 'authoritative-redis', 6397)
            try:
                with (root / 'producer.log').open('wb') as output:
                    producer = subprocess.Popen([str(BINARY), 'hold' if termination == 'crash' else 'produce',
                        str(root), scenario], stdout=output, stderr=subprocess.STDOUT,
                        env=dict(os.environ, CPW_ROUTE_REDIS_PORT='6397'))
                    try:
                        deadline = time.monotonic() + 90
                        checkpoint = root / 'checkpoint.json'
                        while not checkpoint.exists():
                            assert producer.poll() is None, (root / 'producer.log').read_text()
                            assert time.monotonic() < deadline
                            time.sleep(.05)
                        if termination == 'crash':
                            producer.kill()
                        producer.wait(timeout=10)
                    finally:
                        if producer.poll() is None:
                            producer.kill()
                            producer.wait(timeout=10)
                checkpoint_bytes = checkpoint.read_bytes()
                cp = json.loads(checkpoint_bytes)
                assert cp['pid'] == producer.pid
                records = native_records(6397)
                source_contents = contents(6397)
                source_files = files(root / 'event_store')
                native_dir = root / 'native-record-bytes'
                native_dir.mkdir()
                save(native_dir / 'keys.json', {str(i): key for i, key in enumerate(records)})
                for i, value in enumerate(records.values()):
                    (native_dir / f'{i}.dump').write_bytes(value)
                restores = [child(root, 'restore', f'restore-{i}', checkpoint, root / 'event_store', records, source_contents) for i in range(2)]
                controls = {}
                if termination == 'healthy':
                    controls['duplicate_fill'] = child(root, 'duplicate', 'duplicate-fill', checkpoint, root / 'event_store', records, source_contents)
                    controls['duplicate_sequence'] = child(root, 'collision', 'duplicate-sequence', checkpoint, root / 'event_store', records, source_contents)
                if scenario == 'reversal' and termination == 'healthy':
                    faults = {field: mutate_identity(field) for field in ('source', 'binary_sha256', 'cargo_lock_sha256', 'instance_id', 'run_id')}
                    faults.update({f'{kind}_snapshot': mutate_snapshot(kind) for kind in ('missing', 'corrupt', 'truncated')})
                    faults.update({f'{kind}_anchor_source': mutate_anchor(kind) for kind in ('missing', 'corrupt', 'truncated')})
                    for label, fault in faults.items():
                        controls[label] = child(root, 'restore', 'negative-' + label, checkpoint, root / 'event_store', records, source_contents, fault)
                    controls['no_resume'] = child(root, 'resume', 'negative-resume', checkpoint, root / 'event_store', records, source_contents)
                expected = Decimal('29.836' if scenario == 'reversal' else '9.916')
                qualified = all(r['exit'] == 0 and r['native_receipt'] and r['native_receipt']['equal'] for r in restores)
                row = {'scenario': scenario, 'termination': termination, 'producer_pid': producer.pid,
                    'producer_exit': producer.returncode, 'checkpoint': cp, 'checkpoint_sha256': sha(checkpoint_bytes),
                    'producer_pnl_match': Decimal(cp['state']['portfolio_realized_pnl']) == expected,
                    'producer_equity_match': Decimal(cp['state']['accounts'][0]['equity']) == 10000 + expected,
                    'restores': restores, 'controls': controls, 'qualified_recovery': qualified,
                    'authority_records_before': hashes(records), 'authority_records_after': hashes(native_records(6397)),
                    'authority_files_before': source_files, 'authority_files_after': files(root / 'event_store'),
                    'authoritative_checkpoint_unchanged': checkpoint.read_bytes() == checkpoint_bytes}
                assert row['authority_records_before'] == row['authority_records_after']
                assert row['authority_files_before'] == row['authority_files_after']
                assert row['authoritative_checkpoint_unchanged']
                matrix['cases'].append(row)
                save(ROOT / 'results.json', matrix)
            finally:
                stop_redis(authority, 6397)
            assert time.monotonic() - started < 3600, 'physical WP limit'
    matrix['physical_seconds'] = time.monotonic() - started
    matrix['outcome'] = ('REQUIRES_SAFETY_REVIEW' if all(row['qualified_recovery'] for row in matrix['cases'])
                         else 'NATIVE_V2_BOOTSTRAP_ROUTE_FAILED')
    save(ROOT / 'results.json', matrix)
    print(json.dumps({'outcome': matrix['outcome'], 'physical_seconds': matrix['physical_seconds'],
                      'qualified': [r['qualified_recovery'] for r in matrix['cases']]}))
    return 0 if matrix['outcome'] == 'REQUIRES_SAFETY_REVIEW' else 2


if __name__ == '__main__':
    raise SystemExit(main())
