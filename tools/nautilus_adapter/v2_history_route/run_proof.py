"""Offline N2-04 staged safety proof. Native clones have no production authority."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from decimal import Decimal

BINARY = Path('/tmp/cpw-target/debug/cpw-n2-history-route')
ROOT = Path('/evidence/physical-final')


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
    if checkpoint.exists():
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
        # Trusted digest belongs to the original producer, never to a mutated clone receipt.
        digest = sha(checkpoint.read_bytes()) if checkpoint.exists() else '0' * 64
        with subprocess.Popen([str(BINARY), mode, str(target)],
                env=dict(os.environ, CPW_ROUTE_REDIS_PORT='6398', CPW_EXPECTED_CHECKPOINT_SHA256=digest),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            try:
                stdout, stderr = process.communicate(timeout=60)
            except BaseException:
                process.kill()
                process.communicate()
                raise
        (target / 'child.log').write_bytes(stdout + stderr)
        # Native process closes its backing writer before exit; no sleep-based drain claim.
        after = native_records(6398)
        content_after = contents(6398)
        def read(name):
            path = target / name
            return json.loads(path.read_bytes()) if path.exists() else None
        row = {'mode': mode, 'exit': process.returncode, 'pid': process.pid,
            'admission': read('admission.json'), 'process': read('restore-process.json'),
            'native_receipt': read('restore-receipt.json'), 'collision_receipt': read('collision-receipt.json'),
            'mutation': mutation, 'native_clone_exact': before == records,
            'native_clone_content_equal': clone_contents == source_contents,
            'contents_before': content_before, 'contents_after': content_after,
            'content_changed_keys': [key for key in sorted(set(content_before) | set(content_after))
                                     if content_before.get(key) != content_after.get(key)],
            'records_before': hashes(fault_before), 'records_after': hashes(after),
            'changed_keys': [key for key in sorted(set(fault_before) | set(after)) if fault_before.get(key) != after.get(key)],
            'source_files_before': source_before, 'source_files_after': files(target / 'event_store'),
            'checkpoint_after': sha((target / 'checkpoint.json').read_bytes()) if (target / 'checkpoint.json').exists() else None}
        for label, values in [('before', fault_before), ('after', after)]:
            directory = target / ('native-record-' + label)
            directory.mkdir()
            save(directory / 'keys.json', {str(i): key for i, key in enumerate(values)})
            for i, value in enumerate(values.values()):
                (directory / f'{i}.dump').write_bytes(value)
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


def require_result(row, admitted=False, reason=None, duplicate=False):
    """Fail the matrix on any mutation, mismatched PID, or weakened disposition."""
    assert not row['changed_keys'], row
    assert not row['content_changed_keys'], row
    assert row['source_files_before'] == row['source_files_after'], row
    assert row['process']['pid'] == row['pid'], row
    decision = row['admission']
    assert decision['pid'] == row['pid'], row
    assert decision['decision'] == ('RECOVERY_ADMITTED_SEALED' if admitted else 'RECONCILIATION_REQUIRED'), row
    assert (row['exit'] == 0) is admitted, row
    if reason:
        assert reason in decision['error'], row
    if admitted:
        native = row['native_receipt']
        assert native['equal'] is True and native['tail_replay_invoked'] is False, row
        assert native['bus_publishes'] == native['bus_sends'] == [], row
        assert native['bus_responses'] == 0 and native['registered_endpoints'] == [], row
        if duplicate:
            probe = native['duplicate']
            assert probe['position_id'] and probe['unchanged'], row
            assert len(probe['attempts']) == 3, row
            assert all(a['unchanged'] and a['native_error'] for a in probe['attempts']), row
    return True


def produce_case(label, scenario='reversal', boundary=None):
    root = ROOT / label
    root.mkdir()
    authority = start_redis(root / 'authoritative-redis', 6397)
    try:
        with (root / 'producer.log').open('wb') as log:
            env = dict(os.environ, CPW_ROUTE_REDIS_PORT='6397')
            if boundary:
                env['CPW_CRASH_BOUNDARY'] = boundary
            producer = subprocess.Popen([str(BINARY), 'produce', str(root), scenario],
                                        stdout=log, stderr=subprocess.STDOUT, env=env)
            try:
                deadline = time.monotonic() + 90
                while producer.poll() is None:
                    marker = root / 'boundary.json'
                    try:
                        reached = json.loads(marker.read_bytes())
                    except (FileNotFoundError, json.JSONDecodeError):
                        reached = None
                    if boundary and reached and reached['boundary'] == boundary:
                        assert reached['pid'] == producer.pid
                        assert reached['binary_sha256'] == sha(BINARY.read_bytes())
                        producer.kill()  # Only the separate Popen-owned PID at its proven boundary.
                        break
                    assert time.monotonic() < deadline, (root / 'producer.log').read_text()
                    time.sleep(.03)
                producer.wait(timeout=10)
                assert producer.returncode == (-9 if boundary else 0), (root / 'producer.log').read_text()
            finally:
                if producer.poll() is None:
                    producer.kill()
                    producer.wait(timeout=10)
        records, semantic = native_records(6397), contents(6397)
        directory = root / 'native-record-bytes'
        directory.mkdir()
        save(directory / 'keys.json', {str(i): key for i, key in enumerate(records)})
        for i, value in enumerate(records.values()):
            (directory / f'{i}.dump').write_bytes(value)
        cp = root / 'checkpoint.json'
        checkpoint = json.loads(cp.read_bytes()) if cp.exists() else None
        state = json.loads((root / 'producer-state.json').read_bytes())
        assert state['pid'] == producer.pid
        if checkpoint:
            assert checkpoint['pid'] == producer.pid
        receipt = {'pid': producer.pid, 'exit': producer.returncode, 'boundary': boundary,
                   'checkpoint_sha256': sha(cp.read_bytes()) if cp.exists() else None,
                   'checkpoint': checkpoint, 'state': state, 'records': hashes(records),
                   'contents': semantic, 'source_files': files(root / 'event_store')}
        save(root / 'producer-receipt.json', receipt)
        return root, records, semantic, receipt
    finally:
        stop_redis(authority, 6397)


def main():
    assert not ROOT.exists(), 'fresh physical evidence required'
    assert len(Path('/proc/net/route').read_text().splitlines()) == 1, 'external network present'
    ROOT.mkdir()
    started = time.monotonic()
    matrix = {'controller_pid': os.getpid(), 'binary_sha256': sha(BINARY.read_bytes()),
              'producers': [], 'cases': [], 'stage_b_passed': False, 'outcome': 'N2_04_FAILED'}

    def retain(row, **requirements):
        matrix['cases'].append(row)
        save(ROOT / 'results.json', matrix)
        require_result(row, **requirements)

    try:
        # B: one sealed reversal, one torn pairing, one associated duplicate probe.
        root, records, semantic, producer = produce_case('quick_reversal')
        matrix['producers'].append(producer)
        checkpoint, store = root / 'checkpoint.json', root / 'event_store'
        retain(child(root, 'restore', 'sealed-restore', checkpoint, store, records, semantic), admitted=True)

        def torn(target):
            key = next(k for k in records if ':accounts:' in k)
            redis(6398, 'DEL', key)
            return {'deleted_native_key': key}
        retain(child(root, 'restore', 'torn-pair', checkpoint, store, records, semantic, torn),
               reason='REDIS_PRODUCER_PAIR_MISMATCH')
        row = child(root, 'duplicate', 'associated-duplicates', checkpoint, store, records, semantic)
        matrix['cases'].append(row)
        save(ROOT / 'results.json', matrix)
        if row['admission'] and 'NATIVE_ASSOCIATION_BLOCKED' in (row['admission']['error'] or ''):
            matrix['outcome'] = 'NATIVE_ASSOCIATION_BLOCKED'
            raise RuntimeError('NATIVE_ASSOCIATION_BLOCKED')
        require_result(row, admitted=True, duplicate=True)
        matrix['stage_b_passed'] = True
        save(ROOT / 'results.json', matrix)

        # C: truthful windows, one multi-cycle, one authentic open position.
        acknowledged = None
        for boundary in ('before_seal', 'after_seal', 'after_drain', 'acknowledged'):
            case_root, case_records, case_semantic, cp = produce_case('crash_' + boundary, boundary=boundary)
            matrix['producers'].append(cp)
            row = child(case_root, 'restore', 'restart', case_root / 'checkpoint.json',
                        case_root / 'event_store', case_records, case_semantic)
            retain(row, admitted=boundary == 'acknowledged')
            if boundary == 'acknowledged':
                acknowledged = (case_root, case_records, case_semantic)
        other, other_records, other_semantic = acknowledged
        # Both producer stores are valid separately; pairing either with the other's receipt refuses.
        retain(child(root, 'restore', 'different-valid-redis', checkpoint, store, other_records, other_semantic),
               reason='REDIS_PRODUCER_PAIR_MISMATCH')
        retain(child(root, 'restore', 'different-valid-redb', checkpoint, other / 'event_store', records, semantic),
               reason='EVENT_STORE_PRODUCER_PAIR_MISMATCH')

        for label, fault in [('truncated_receipt', lambda t: (t / 'checkpoint.json').write_bytes(b'{')),
                             ('absent_receipt', lambda t: (t / 'checkpoint.json').unlink()),
                             ('wrong_run', mutate_identity('run_id')),
                             ('stale_watermark', mutate_identity('watermark')),
                             ('invalid_marker', mutate_identity('checkpoint'))]:
            retain(child(root, 'restore', label, checkpoint, store, records, semantic, fault))
        for scenario in ('multi_cycle', 'open'):
            case_root, case_records, case_semantic, cp = produce_case(scenario, scenario)
            matrix['producers'].append(cp)
            state = cp['checkpoint']['state']
            if scenario == 'multi_cycle':
                assert len(state['snapshots']) >= 2, state
                assert {frame['index'] for frame in state['snapshots']} == {0, 1}, state
                reason = 'ARCHIVE_CONTINUITY_BLOCKED'
            else:
                assert any(not p['closed'] for p in state['positions']), state
                assert state['portfolio_unrealized_pnl'] is not None, state
                assert state['portfolio_net_exposure'] is not None, state
                reason = 'OPEN_EXPOSURE_REQUIRES_RECONCILIATION'
            retain(child(case_root, 'restore', 'restart', case_root / 'checkpoint.json',
                         case_root / 'event_store', case_records, case_semantic), reason=reason)
        matrix['outcome'] = 'N2_04_SAFETY_GATE_PASSED'
    except BaseException as error:
        matrix['hard_stop'] = repr(error)
        raise
    finally:
        matrix['physical_seconds'] = time.monotonic() - started
        matrix['binary_unchanged'] = sha(BINARY.read_bytes()) == matrix['binary_sha256']
        assert matrix['binary_unchanged']
        save(ROOT / 'results.json', matrix)
        print(json.dumps({k: matrix[k] for k in ('outcome', 'stage_b_passed', 'physical_seconds')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
