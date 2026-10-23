"""OS-process controller for the private native Rust fixture; standard library only.

Run inside the owned Linux container after disconnecting its external network.
The controller records comparisons; a green controller is not N2 acceptance.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from decimal import Decimal

BINARY = Path('/evidence/build_gate/target/debug/cpw-n2-history-route')
ROOT = Path('/evidence/native-physical')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def redis(*args, data=None):
    command = ['redis-cli', '-p', '6397', '--raw']
    if data is not None:
        command.append('-x')
    result = subprocess.run(command + list(args), input=data, capture_output=True, timeout=10)
    assert result.returncode == 0, result.stderr
    return result.stdout.removesuffix(b'\n')


def records():
    keys = redis('--scan').splitlines()
    return {key.decode(): sha(redis('DUMP', key.decode())) for key in sorted(keys)}


def child(mode, root, label):
    result = subprocess.run([str(BINARY), mode, str(root)], capture_output=True, timeout=60)
    (root / f'{label}.log').write_bytes(result.stdout + result.stderr)
    value = None
    if result.returncode == 0 and mode == 'restore':
        value = json.loads(result.stdout.splitlines()[-1])
    return {'returncode': result.returncode, 'receipt': value,
            'log': f'{root.name}/{label}.log'}


def main():
    assert not ROOT.exists(), 'fresh physical directory required; preserve prior evidence'
    assert redis('DBSIZE') == b'0', 'owned Redis must start empty'
    routes = Path('/proc/net/route').read_text().splitlines()
    assert len(routes) == 1, 'external network must be disconnected before physical work'
    ROOT.mkdir()
    started = time.monotonic()
    result = {'controller_pid': os.getpid(), 'binary_sha256': sha(BINARY.read_bytes()),
              'initial_dbsize': 0, 'external_routes': routes[1:], 'scenarios': []}
    for scenario in ('round_trip', 'reversal'):
        for termination in ('healthy', 'crash'):
            root = ROOT / f'{scenario}_{termination}'
            root.mkdir()
            with (root / 'producer.log').open('wb') as log:
                command = [str(BINARY), 'hold' if termination == 'crash' else 'produce', str(root), scenario]
                process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                try:
                    deadline = time.monotonic() + 90
                    while not (root / 'checkpoint.json').exists():
                        assert process.poll() is None, (root / 'producer.log').read_text()
                        assert time.monotonic() < deadline, 'producer checkpoint timed out'
                        time.sleep(.05)
                    data = (root / 'checkpoint.json').read_bytes()
                    checkpoint = json.loads(data)
                    assert checkpoint['pid'] == process.pid
                    if termination == 'crash':
                        assert process.poll() is None
                        process.kill()  # SIGKILL only this owned Popen handle, after acknowledged native close.
                    process.wait(timeout=10)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=10)
            baseline = records()
            restores = [child('restore', root, f'restore-{i}') for i in range(2)]
            after = records()
            expected = Decimal('29.836' if scenario == 'reversal' else '9.916')
            state = checkpoint['state']
            comparisons = {
                'producer_pnl': Decimal(state['portfolio_realized_pnl']) == expected,
                'producer_equity': Decimal(state['accounts'][0]['equity']) == Decimal(10000) + expected,
                'producer_closed': all(p['closed'] for p in state['positions']),
                'checkpoint_unchanged': sha(data) == sha((root / 'checkpoint.json').read_bytes()),
                'native_records_unchanged': baseline == after,
                'distinct_pids': len({process.pid, os.getpid()} | {
                    r['receipt']['pid'] for r in restores if r['receipt']}) == 4,
                'restores_equal': all(r['returncode'] == 0 and r['receipt']['equal'] for r in restores),
                'no_new_orders_fills_clients': all(r['receipt'] and all(r['receipt'][k] == 0
                    for k in ('new_orders', 'new_fills', 'execution_clients')) for r in restores),
                'termination_expected': process.returncode == (-9 if termination == 'crash' else 0),
            }
            row = {'scenario': scenario, 'termination': termination, 'producer_exit': process.returncode,
                   'checkpoint_sha256': sha(data), 'checkpoint': checkpoint, 'restores': restores,
                   'comparisons': comparisons, 'records_before': baseline, 'records_after': after}
            result['scenarios'].append(row)
            (ROOT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
            assert time.monotonic() - started < 3600, 'WP physical limit reached'
    # Trusted-source and venue-refusal controls run before a native restore is attempted.
    target = ROOT / 'reversal_healthy'
    original = (target / 'checkpoint.json').read_bytes()
    negatives = {}
    for field in ('source', 'binary_sha256', 'cargo_lock_sha256'):
        altered = json.loads(original)
        altered[field] = 'wrong-identity'
        (target / 'checkpoint.json').write_text(json.dumps(altered))
        negatives[field] = child('restore', target, f'negative-{field}')
    (target / 'checkpoint.json').write_bytes(original)
    negatives['no_venue_reconciliation'] = child('resume', target, 'negative-resume')
    snapshot_keys = [key for key in records() if 'position-snapshots' in key
                     and json.loads(original)['trader'] in key]
    assert len(snapshot_keys) == 1, snapshot_keys
    key = snapshot_keys[0]
    snapshot = redis('GET', key)
    for mutation, value in (('missing_snapshot', None), ('corrupt_snapshot', b'corrupt'),
                            ('truncated_snapshot', snapshot[:len(snapshot)//2])):
        try:
            redis('DEL', key) if value is None else redis('SET', key, data=value)
            negatives[mutation] = child('restore', target, f'negative-{mutation}')
        finally:
            redis('SET', key, data=snapshot)
    cp = json.loads(original)
    run_file = target / 'event_store' / cp['instance_id'] / (cp['run_id'] + '.redb')
    native_run = run_file.read_bytes()
    for mutation in ('missing_anchor_source', 'corrupt_anchor_source', 'truncated_anchor_source'):
        try:
            if mutation == 'missing_anchor_source':
                run_file.unlink()
            else:
                run_file.write_bytes(b'\0' * 64 if mutation == 'corrupt_anchor_source' else native_run[:32])
            negatives[mutation] = child('restore', target, f'negative-{mutation}')
        finally:
            run_file.write_bytes(native_run)
    altered = json.loads(original)
    altered['instance_id'] = '00000000-0000-4000-8000-000000000001'
    try:
        (target / 'checkpoint.json').write_text(json.dumps(altered))
        negatives['replay_identity_collision'] = child('restore', target, 'negative-replay-identity')
    finally:
        (target / 'checkpoint.json').write_bytes(original)
    duplicate = child('duplicate', target, 'negative-duplicate-fill')
    result['negative_controls'] = negatives
    result['duplicate_fill_control'] = duplicate
    result['physical_seconds'] = time.monotonic() - started
    result['outcome'] = ('NATIVE_V2_ROUTE_PROVEN' if all(all(r['comparisons'].values())
        for r in result['scenarios']) and all(n['returncode'] != 0 for n in negatives.values())
        and duplicate['returncode'] == 0
        else 'NATIVE_V2_ROUTE_FAILED')
    result['acceptance'] = 'BOUNDED_ROUTE_ONLY_N2_NOT_GRANTED' if result['outcome'].endswith('PROVEN') else 'PHYSICAL_FAILURE'
    (ROOT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'outcome': result['outcome'], 'acceptance': result['acceptance'],
                      'comparisons': [r['comparisons'] for r in result['scenarios']]}))
    return 0 if result['outcome'].endswith('PROVEN') else 2


if __name__ == '__main__':
    sys.exit(main())
