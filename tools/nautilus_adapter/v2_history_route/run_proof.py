"""Offline N2-05 continuity and N2-06 funding/liquidation proof. Native clones have no production or order authority."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import time
from decimal import Decimal

BINARY = Path('/tmp/cpw-target/debug/cpw-n2-history-route')
ROOT = Path(os.environ.get('CPW_PROOF_ROOT', '/evidence/physical-n2-06'))
READONLY_USER = 'cpw-restore-readonly'
NO_AUTHORITY = 'NO_NEW_ORDERS / NO_RESUME'


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


def run_binary(mode, target, env):
    with subprocess.Popen([str(BINARY), mode, str(target)], env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        try:
            stdout, stderr = process.communicate(timeout=60)
        except BaseException:
            process.kill()
            process.communicate()
            raise

    def read(name):
        path = target / name
        return json.loads(path.read_bytes()) if path.exists() else None
    return {'exit': process.returncode, 'pid': process.pid, 'log': (stdout + stderr).decode(errors='replace'),
            'admission': read('admission.json'), 'process': read('restore-process.json'),
            'native_receipt': read('restore-receipt.json'), 'collision_receipt': read('collision-receipt.json')}


def child(root, mode, label, checkpoint, source, records, source_contents, fault=None,
          resign=False, runs=1, readonly=True):
    """One disposable native clone. `resign` models a defective producer receipt that still
    carries a trusted digest, so the semantic gate itself (not the digest) must refuse it."""
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
        env = dict(os.environ, CPW_ROUTE_REDIS_PORT='6398')
        acl = None
        if readonly:
            # Fresh per-clone loopback ACL user; Redis itself denies every write command.
            token = secrets.token_hex(16)
            redis(6398, 'ACL', 'SETUSER', READONLY_USER, 'on', '>' + token, '~*', '&*', '+@all', '-@write')
            acl = redis(6398, 'ACL', 'GETUSER', READONLY_USER).decode()
            env.update(CPW_ROUTE_REDIS_READONLY_USER=READONLY_USER, CPW_ROUTE_REDIS_READONLY_TOKEN=token)
        redis(6398, 'ACL', 'LOG', 'RESET')
        fault_before = native_records(6398)
        content_before = contents(6398)
        source_before = files(target / 'event_store')
        trusted = target / 'checkpoint.json' if resign else checkpoint
        # Trusted digest belongs to the original producer unless this is a re-signed defect model.
        env['CPW_EXPECTED_CHECKPOINT_SHA256'] = sha(trusted.read_bytes()) if trusted.exists() else '0' * 64
        attempts = []
        for run in range(runs):
            attempt = run_binary(mode, target, env)
            if runs > 1:
                directory = target / f'run-{run + 1}'
                directory.mkdir()
                for name in ('admission.json', 'restore-process.json', 'restore-receipt.json'):
                    if (target / name).exists():
                        shutil.copyfile(target / name, directory / name)
            attempts.append(attempt)
        (target / 'child.log').write_text(''.join(a['log'] for a in attempts))
        # Native process closes its backing writer before exit; no sleep-based drain claim.
        after = native_records(6398)
        content_after = contents(6398)
        denied = json.loads(subprocess.check_output(['redis-cli', '-p', '6398', '--json', 'ACL', 'LOG', '1000']))
        row = dict(attempts[-1], mode=mode, mutation=mutation, resigned=resign, readonly_acl=acl,
            runs=[{k: a[k] for k in ('exit', 'pid', 'admission', 'process', 'native_receipt')} for a in attempts],
            acl_denied=denied,
            acl_denied_commands=[entry.get('object') if isinstance(entry, dict) else entry for entry in denied],
            native_clone_exact=before == records, native_clone_content_equal=clone_contents == source_contents,
            contents_before=content_before, contents_after=content_after,
            content_changed_keys=[key for key in sorted(set(content_before) | set(content_after))
                                  if content_before.get(key) != content_after.get(key)],
            records_before=hashes(fault_before), records_after=hashes(after),
            changed_keys=[key for key in sorted(set(fault_before) | set(after)) if fault_before.get(key) != after.get(key)],
            source_files_before=source_before, source_files_after=files(target / 'event_store'),
            checkpoint_after=sha((target / 'checkpoint.json').read_bytes()) if (target / 'checkpoint.json').exists() else None)
        del row['log']
        for name, values in [('before', fault_before), ('after', after)]:
            directory = target / ('native-record-' + name)
            directory.mkdir()
            save(directory / 'keys.json', {str(i): key for i, key in enumerate(values)})
            for i, value in enumerate(values.values()):
                (directory / f'{i}.dump').write_bytes(value)
        save(target / 'controller-receipt.json', row)
        return row
    finally:
        stop_redis(clone, 6398)


def resigned(change):
    """Rewrite the clone receipt; used only together with resign=True."""
    def mutate(target):
        path = target / 'checkpoint.json'
        data = json.loads(path.read_bytes())
        detail = change(data, target)
        save(path, data)
        return {'resigned_receipt_change': detail}
    return mutate


def mutate_identity(field):
    def mutate(target):
        path = target / 'checkpoint.json'
        data = json.loads(path.read_bytes())
        data[field] = ('00000000-0000-4000-8000-000000000001' if field == 'instance_id' else 'wrong-' + field)
        save(path, data)
        return {'checkpoint_field': field}
    return mutate


def frame_key(keys, index):
    found = [key for key in keys if key.endswith(f'/{index}') and ':general:cache://position-snapshots/' in key]
    assert len(found) == 1, keys
    return found[0]


def require_result(row, admitted=False, reason=None, duplicate=False, open_exposure=False):
    """Fail the matrix on any mutation, mismatched PID, or weakened disposition."""
    assert not row['changed_keys'], row
    assert not row['content_changed_keys'], row
    assert row['source_files_before'] == row['source_files_after'], row
    for run in row.get('runs') or [row]:
        assert run['process']['pid'] == run['pid'], row
        decision = run['admission']
        assert decision['pid'] == run['pid'], row
        assert decision.get('order_authority', NO_AUTHORITY) == NO_AUTHORITY, row
        expected = ('OPEN_EXPOSURE_RECONSTRUCTED_NO_RESUME' if open_exposure else
                    'RECOVERY_ADMITTED_SEALED' if admitted else 'RECONCILIATION_REQUIRED')
        assert decision['decision'] == expected, row
        assert (run['exit'] == 0) is (admitted or open_exposure), row
        if reason:
            assert reason in decision['error'], row
        if admitted or open_exposure:
            native = run['native_receipt']
            assert native['equal'] is True and native['tail_replay_invoked'] is False, row
            assert native['bus_publishes'] == native['bus_sends'] == [], row
            assert native['bus_responses'] == 0 and native['registered_endpoints'] == [], row
            assert native.get('market_context_applied', False) is open_exposure, row
            if open_exposure:
                assert decision['venue_reconciliation_required_before_activation'] is True, row
                assert native['resume'] == 'VENUE_RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME', row
            if duplicate:
                probe = native['duplicate']
                assert probe['position_id'] and probe['unchanged'], row
                assert len(probe['attempts']) == 3, row
                assert all(a['unchanged'] and a['native_error'] for a in probe['attempts']), row
    return True


def dec(value):
    return Decimal(value) if value is not None else None


def require_continuity(row, producer, witness):
    """Independent producer-vs-restore comparison from native observations of each process.
    The fixture witness values are acceptance assertions only; they never feed restoration."""
    expected = producer['checkpoint']['state']
    for run in row['runs']:
        native = run['native_receipt']
        state = native['state']
        assert run['pid'] != producer['pid'], row
        for key in ('accounts', 'orders', 'positions', 'fills', 'archived', 'snapshots'):
            assert state[key] == expected[key], key
        for key in ('portfolio_realized_pnl', 'portfolio_unrealized_pnl', 'portfolio_net_exposure'):
            assert dec(state[key]) == dec(expected[key]), key
        frames = sorted(state['snapshots'], key=lambda f: f['index'])
        assert [f['index'] for f in frames] == list(range(len(frames))), frames
        assert [f['sha256'] for f in frames] == [sha(bytes(f['bytes'])) for f in frames]
        chain = native['anchor_chain']
        assert chain == producer['checkpoint']['anchor_chain'], chain
        assert len(chain) == len(frames) == witness['frames'], chain
        assert chain[-1:] == ([producer['checkpoint']['anchor']] if producer['checkpoint']['anchor'] else []), chain
        assert all(a['blob_ref'].endswith(f'/{i}') for i, a in enumerate(chain)), chain
        assert [a['high_watermark'] for a in chain] == sorted({a['high_watermark'] for a in chain}), chain
        # Total realized PnL must include every archived cycle plus the current position.
        archived = sum(Decimal(p['pnl']) for p in state['archived'])
        current = sum(Decimal(p['pnl']) for p in state['positions'])
        assert archived + current == dec(state['portfolio_realized_pnl']), (archived, current)
        commissions = [c for p in state['positions'] for c in p['native']['commissions']]
        assert commissions == [c for p in expected['positions'] for c in p['native']['commissions']]
        equity = dec(state['accounts'][0]['equity'])
        for key, value in witness['decimal'].items():
            assert (equity if key == 'equity' else dec(state[key])) == Decimal(value), (key, state)
        if witness.get('open'):
            context = producer['checkpoint']['market_context']
            assert native['restored_mark'] == json.loads(context['native']), native['restored_mark']
            assert native['restored_mark']['ts_event'] == context['ts_event']
            open_positions = [p for p in state['positions'] if not p['closed']]
            assert [p['native']['quantity'] for p in open_positions] == [witness['quantity']], open_positions
            assert state['accounts'][0].get('maintenance_margins') == expected['accounts'][0].get('maintenance_margins')
            assert state['accounts'][0].get('initial_margins') == expected['accounts'][0].get('initial_margins')
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
                    except (OSError, json.JSONDecodeError):  # absent or mid-write on the bind mount; retried
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
        receipt = {'label': label, 'pid': producer.pid, 'exit': producer.returncode, 'boundary': boundary,
                   'checkpoint_sha256': sha(cp.read_bytes()) if cp.exists() else None,
                   'checkpoint': checkpoint, 'state': state, 'records': hashes(records),
                   'contents': semantic, 'source_files': files(root / 'event_store'),
                   'record_files': files(directory)}
        save(root / 'producer-receipt.json', receipt)
        return root, records, semantic, receipt
    finally:
        stop_redis(authority, 6397)


MULTI_WITNESS = {'frames': 2, 'decimal': {'portfolio_realized_pnl': '59.752', 'equity': '10059.752',
                                          'portfolio_unrealized_pnl': '0', 'portfolio_net_exposure': '0'}}
OPEN_WITNESS = {'frames': 0, 'open': True, 'quantity': '1.000',
                'decimal': {'portfolio_unrealized_pnl': '10', 'portfolio_net_exposure': '110', 'equity': '9999.96'}}

# N2-06. CPW references are the unchanged N1-02 oracle (tests/test_nautilus_n1_02_parity.py):
# funding_paid = side * rate * 100 for q=1 at 100; short 100 @ 100 liquidates at the first adverse
# close (195 maintenance, 200/250 zero floor) with final equity 0. Native values are never adjusted.
BOUNDARY_NS = 1_800_000_001_500_000_000
FIRST_STRESS_NS = 1_800_000_001_000_000_000
FUNDING = {'funding_long_pos': (1, '0.01'), 'funding_long_neg': (1, '-0.01'), 'funding_short_pos': (-1, '0.01'),
           'funding_short_neg': (-1, '-0.01'), 'funding_flat_pos': (0, '0.01'), 'funding_flat_neg': (0, '-0.01'),
           'funding_duplicate': (1, '0.01'), 'funding_missing': (1, None), 'funding_no_boundary': (1, None)}
FUNDING_REFUSALS = {'funding_stale': 'Late funding boundary', 'funding_cross_instrument': 'Funding settlement failed'}
LIQUIDATION = [f'liquidation_{mode}_{price}' for price in (195, 200, 250) for mode in ('on', 'off')]
VERDICTS = ('PROVEN', 'BOUNDED_DIVERGENCE', 'UNSUPPORTED_PINNED', 'UNVERIFIED')


def money(value):
    return Decimal(value.split()[0])


def economics(checkpoint):
    """Stable native projection for repeat comparison; volatile UUIDs, PIDs and run IDs are excluded."""
    state = checkpoint['state']
    return {'run_error': checkpoint['run_error'],
            'settlements': [{k: s[k] for k in ('instrument_id', 'rate', 'settlement_price', 'currency', 'ts_event')}
                            for s in checkpoint['funding_settlements']],
            'accounts': [{k: a.get(k) for k in ('equity', 'balances', 'initial_margins', 'maintenance_margins')}
                         for a in state['accounts']],
            'positions': [{'closed': p['closed'], 'pnl': p['pnl'], 'side': p['native']['side'],
                           'quantity': p['native']['quantity'], 'commissions': p['native']['commissions'],
                           'adjustments': [{k: a[k] for k in ('adjustment_type', 'pnl_change', 'ts_event')}
                                           for a in p['native']['adjustments']]} for p in state['positions']],
            'orders': sorted((o['id'].startswith('LIQUIDATION-'), o['status'], o['filled']) for o in state['orders']),
            'fills': sorted((f['payload']['order_side'], f['payload']['last_qty'], f['payload']['last_px'],
                             f['payload']['ts_event'], f['order_id'].startswith('LIQUIDATION-')) for f in state['fills']),
            'pnl': [state[k] for k in ('portfolio_realized_pnl', 'portfolio_unrealized_pnl', 'portfolio_net_exposure')]}


def funding_verdict(scenario, view):
    """One verdict from native observations against the unchanged CPW funding reference."""
    side, rate = FUNDING.get(scenario, (1, '0.01'))
    adjustments = [a for p in view['positions'] for a in p['adjustments'] if a['adjustment_type'] == 'FUNDING']
    commissions = sum(money(c) for p in view['positions'] for c in p['commissions'].values())
    cash = sum((money(a['pnl_change']) for a in adjustments), Decimal(0))
    equity = Decimal(view['accounts'][0]['equity'])
    expected = -side * Decimal(rate) * 100 if rate else Decimal(0)
    row = {'scenario': scenario, 'cpw_reference_cash': str(expected), 'native_cash': str(cash),
           'native_settlements': view['settlements'], 'native_adjustments': adjustments,
           'native_equity': str(equity), 'native_commissions': str(commissions), 'run_error': view['run_error']}
    if scenario in FUNDING_REFUSALS:
        refused = FUNDING_REFUSALS[scenario] in (view['run_error'] or '') and not adjustments and not view['settlements']
        row['verdict'] = 'PROVEN' if refused else 'UNVERIFIED'
        row['proven'] = 'native fail-closed run error at the settlement gate; no cash effect' if refused else None
        return row
    if view['run_error']:
        row['verdict'] = 'UNVERIFIED'
    elif expected and not view['settlements']:
        row['verdict'] = 'UNSUPPORTED_PINNED'
    else:
        settled = [(s['rate'], s['settlement_price'], s['ts_event']) for s in view['settlements']]
        exact = (settled == ([(rate, '100.00', BOUNDARY_NS)] if expected else [])
                 and len(adjustments) == (1 if expected else 0)
                 and cash == expected and equity == 10000 - commissions + cash)
        row['verdict'] = 'PROVEN' if exact else 'BOUNDED_DIVERGENCE'
    return row


def liquidation_verdict(scenario, view, paired_on=None):
    """Native mechanism vs the unchanged CPW liquidation reference; `off` proves the disable switch."""
    liquidations = [f for f in view['fills'] if f[4]]
    position = view['positions'][0]
    equity = Decimal(view['accounts'][0]['equity'])
    row = {'scenario': scenario, 'native_liquidation_fills': liquidations, 'native_equity': str(equity),
           'native_position': position, 'native_maintenance_margins': view['accounts'][0]['maintenance_margins'],
           'cpw_reference': {'liquidated_at_ns': FIRST_STRESS_NS, 'final_equity': '0', 'surviving_position': False},
           'run_error': view['run_error']}
    if view['run_error']:
        row['verdict'] = 'UNVERIFIED'
    elif '_off_' in scenario:
        disabled = (not liquidations and not position['closed'] and position['quantity'] == '100.000'
                    and paired_on is not None and paired_on['native_liquidation_fills'])
        row['verdict'] = 'PROVEN' if disabled else 'UNVERIFIED'
    elif not liquidations:
        row['verdict'] = 'UNSUPPORTED_PINNED'
    else:
        at_first_stress = [f[3] for f in liquidations] == [FIRST_STRESS_NS] and position['closed']
        row['verdict'] = ('UNVERIFIED' if not at_first_stress else 'PROVEN' if equity == 0 else 'BOUNDED_DIVERGENCE')
    return row


def funding_not_persisted(checkpoint):
    """Native rc7 Redis `update_position` re-appends the position's last fill for a funding adjustment and
    the native loader rejects the duplicate (redis/queries.rs `Duplicate fill event`): the funded position
    cannot be rebuilt from the cache. True only when the producer's own native records show exactly that."""
    adjusted = any(a['adjustment_type'] == 'FUNDING'
                   for p in checkpoint['state']['positions'] for a in p['native']['adjustments'])
    records = [r['value'] for key, r in checkpoint['redis_contents'].items() if ':positions:' in key]
    events = [[json.loads(e) for e in record] for record in records]
    duplicated = any(len(rows) != len({e['event_id'] for e in rows}) for rows in events)
    return adjusted and duplicated and all(e['type'] == 'OrderFilled' for rows in events for e in rows)


def require_refusal_without_admission(row):
    """`resume` must exit non-zero before any admission receipt and leave every store unchanged."""
    assert row['exit'] != 0 and row['admission'] is None and row['native_receipt'] is None, row
    assert not row['changed_keys'] and not row['content_changed_keys'], row
    assert row['source_files_before'] == row['source_files_after'], row
    return True


def stage_d(matrix, retain, produce):
    """N2-06: every scenario produced twice on the frozen binary; verdicts from native observations only;
    each successful producer restored twice through the unchanged N2-05 read-only path."""
    matrix['n2_06_cases'] = []
    producers = {}
    for scenario in list(FUNDING) + list(FUNDING_REFUSALS) + LIQUIDATION:
        runs = [produce(f'{scenario}_{repeat}', scenario) for repeat in 'ab']
        views = [economics(run[3]['checkpoint']) for run in runs]
        assert views[0] == views[1], ('NONDETERMINISTIC_NATIVE_ECONOMICS', scenario, views)
        producers[scenario] = runs[0]
        if scenario.startswith('liquidation_'):
            paired = (next(c for c in matrix['n2_06_cases'] if c['scenario'] == scenario.replace('_off_', '_on_'))
                      if '_off_' in scenario else None)
            case = liquidation_verdict(scenario, views[0], paired)
        else:
            case = funding_verdict(scenario, views[0])
        assert case['verdict'] in VERDICTS
        case['repeat_identical'] = True
        case['producer_pids'] = [run[3]['pid'] for run in runs]
        matrix['n2_06_cases'].append(case)
        save(ROOT / 'results.json', matrix)

    # Funded and liquidated terminal states through the existing read-only restore, twice per clone.
    for scenario, (root, records, semantic, receipt) in producers.items():
        cp, store = root / 'checkpoint.json', root / 'event_store'
        if receipt['checkpoint']['run_error']:
            retain(child(root, 'restore', 'native-run-failed', cp, store, records, semantic), reason='NATIVE_RUN_FAILED')
            continue
        case = next(c for c in matrix['n2_06_cases'] if c['scenario'] == scenario)
        row = child(root, 'restore', 'restore-twice', cp, store, records, semantic, runs=2)
        if funding_not_persisted(receipt['checkpoint']):
            retain(row, reason='NATIVE_CURRENT_ARCHIVE_ERROR')  # fails closed, zero store mutation
            case['restore'] = 'RECONCILIATION_REQUIRED'
            case['restore_verdict'] = 'UNSUPPORTED_PINNED'
            continue
        is_open = any(not p['closed'] for p in receipt['checkpoint']['state']['positions'])
        retain(row, admitted=not is_open, open_exposure=is_open)  # native `equal`: full producer state, both runs
        case['restore'] = 'OPEN_EXPOSURE_RECONSTRUCTED_NO_RESUME' if is_open else 'RECOVERY_ADMITTED_SEALED'
        case['restore_verdict'] = 'PROVEN'

    # Adversarial controls. Receipt/binding gates run before any native load, so they use the funded
    # producer; history and authority controls use producers whose genuine restore is admitted.
    funded, f_records, f_semantic, _ = producers['funding_long_pos']
    f_cp, f_store = funded / 'checkpoint.json', funded / 'event_store'
    liquidated, l_records, l_semantic, _ = producers['liquidation_on_195']
    l_cp, l_store = liquidated / 'checkpoint.json', liquidated / 'event_store'
    survived, s_records, s_semantic, _ = producers['liquidation_off_195']
    s_cp, s_store = survived / 'checkpoint.json', survived / 'event_store'

    def funded_cash(data, _):
        data['state']['positions'][0]['native']['adjustments'][0]['pnl_change'] = '-2.00000000 USDT'
        return 'funding adjustment doubled in receipt'

    def binding(field, value):
        def change(data, _):
            data[field] = value
            return field
        return change

    def missing_position(target):
        key = next(k for k in redis(6398, '--scan').decode().splitlines() if ':positions:' in k)
        redis(6398, 'DEL', key)
        return {'deleted_native_key': key}

    def missing_position_resigned(data, target):
        key = missing_position(target)['deleted_native_key']
        del data['redis_contents'][key]
        return 'liquidated position record deleted; receipt contents follow it'

    def widened(data, _):
        data['resume'] = 'RESUME_AUTHORIZED'
        data['order_authority'] = 'ORDERS_PERMITTED'
        return 'receipt claims resume/order authority'

    def liquidation_order(data, _):
        order = next(o for o in data['state']['orders'] if o['id'].startswith('LIQUIDATION-'))
        order['status'] = 'CANCELED'
        return 'liquidation order status altered'

    for label, args, kwargs, expect in [
            ('tampered-funded-receipt', (resigned(funded_cash),), {}, {'reason': 'UNVERIFIED_AUTHORITY_RECEIPT'}),
            ('altered-source-binding', (resigned(binding('source', '0' * 40)),), {'resign': True},
             {'reason': 'SOURCE_IDENTITY'}),
            ('altered-lock-binding', (resigned(binding('cargo_lock_sha256', '0' * 64)),), {'resign': True},
             {'reason': 'LOCK_IDENTITY'}),
            ('missing-funded-position', (missing_position,), {}, {'reason': 'REDIS_PRODUCER_PAIR_MISMATCH'})]:
        retain(child(funded, 'restore', label, f_cp, f_store, f_records, f_semantic, *args, **kwargs), **expect)
    for label, args, kwargs, expect in [
            ('tampered-liquidation-resigned', (resigned(liquidation_order),), {'resign': True},
             {'reason': 'NATIVE_CURRENT_ARCHIVE_ERROR'}),
            ('missing-liquidated-position', (missing_position,), {}, {'reason': 'REDIS_PRODUCER_PAIR_MISMATCH'}),
            ('missing-liquidated-position-resigned', (resigned(missing_position_resigned),), {'resign': True},
             {'reason': 'NATIVE_CURRENT_ARCHIVE_ERROR'})]:
        retain(child(liquidated, 'restore', label, l_cp, l_store, l_records, l_semantic, *args, **kwargs), **expect)
    retain(child(survived, 'restore', 'widened-authority-receipt', s_cp, s_store, s_records, s_semantic,
                 resigned(widened), resign=True), open_exposure=True)
    for root, records, semantic in ((funded, f_records, f_semantic), (liquidated, l_records, l_semantic)):
        row = child(root, 'resume', 'resume-refused', root / 'checkpoint.json', root / 'event_store',
                    records, semantic)
        matrix['cases'].append(row)
        require_refusal_without_admission(row)
    save(ROOT / 'results.json', matrix)


def main():
    assert not ROOT.exists(), 'fresh physical evidence required'
    assert len(Path('/proc/net/route').read_text().splitlines()) == 1, 'external network present'
    ROOT.mkdir()
    started = time.monotonic()
    matrix = {'controller_pid': os.getpid(), 'binary_sha256': sha(BINARY.read_bytes()),
              'producers': [], 'cases': [], 'stage_a_passed': False, 'outcome': 'N2_05_BLOCKED'}

    def retain(row, **requirements):
        matrix['cases'].append(row)
        save(ROOT / 'results.json', matrix)
        require_result(row, **requirements)

    def produce(label, scenario, boundary=None):
        produced = produce_case(label, scenario, boundary)
        matrix['producers'].append(produced[3])
        return produced

    try:
        # A: mandatory positives, each restored twice in one clone. Failure stops the matrix.
        multi, multi_records, multi_semantic, multi_p = produce('multi_cycle', 'multi_cycle')
        multi_cp, multi_store = multi / 'checkpoint.json', multi / 'event_store'
        row = child(multi, 'restore', 'restore-twice', multi_cp, multi_store, multi_records, multi_semantic, runs=2)
        retain(row, admitted=True)
        require_continuity(row, multi_p, MULTI_WITNESS)
        opened, open_records, open_semantic, open_p = produce('open', 'open')
        open_cp, open_store = opened / 'checkpoint.json', opened / 'event_store'
        row = child(opened, 'restore', 'restore-twice', open_cp, open_store, open_records, open_semantic, runs=2)
        retain(row, open_exposure=True)
        require_continuity(row, open_p, OPEN_WITNESS)
        matrix['stage_a_passed'] = True
        save(ROOT / 'results.json', matrix)

        # B: associated duplicates and negative controls on both genuine producers.
        retain(child(multi, 'duplicate', 'associated-duplicates', multi_cp, multi_store, multi_records, multi_semantic),
               admitted=True, duplicate=True)
        retain(child(opened, 'duplicate', 'associated-duplicates', open_cp, open_store, open_records, open_semantic),
               open_exposure=True, duplicate=True)
        reversal, rev_records, rev_semantic, rev_p = produce('quick_reversal', 'reversal')
        rev_cp, rev_store = reversal / 'checkpoint.json', reversal / 'event_store'
        foreign_anchor = rev_p['checkpoint']['anchor_chain'][0]
        keys = list(multi_records)
        frame0, frame1 = frame_key(keys, 0), frame_key(keys, 1)

        def chain_change(kind):
            def change(data, _):
                chain = data['anchor_chain']
                if kind == 'missing_prior_anchor':
                    chain.pop(0)
                elif kind == 'corrupt_prior_anchor':
                    chain[0]['content_hash'] = 'blake3:' + '0' * 64
                elif kind == 'stale_prior_anchor':
                    chain[0]['high_watermark'] = chain[1]['high_watermark'] + 1
                elif kind == 'cross_paired_anchor':
                    chain[0] = foreign_anchor
                else:
                    chain.reverse()
                return kind
            return change

        for kind in ('missing_prior_anchor', 'corrupt_prior_anchor', 'stale_prior_anchor',
                     'cross_paired_anchor', 'reordered_anchors'):
            retain(child(multi, 'restore', kind, multi_cp, multi_store, multi_records, multi_semantic,
                         resigned(chain_change(kind)), resign=True), reason='ARCHIVE_CONTINUITY_BLOCKED')

        def overwrite(target):
            redis(6398, 'SET', frame0, data=redis(6398, 'GET', frame1))
            return {'overwritten': frame0, 'with': frame1}
        retain(child(multi, 'restore', 'overwritten-frame', multi_cp, multi_store, multi_records, multi_semantic,
                     overwrite), reason='REDIS_PRODUCER_PAIR_MISMATCH')

        def overwrite_resigned(data, target):
            overwrite(target)
            data['redis_contents'][frame0] = data['redis_contents'][frame1]
            return 'Redis frame 0 overwritten after anchoring; receipt contents follow it'
        retain(child(multi, 'restore', 'overwritten-frame-resigned', multi_cp, multi_store, multi_records,
                     multi_semantic, resigned(overwrite_resigned), resign=True),
               reason='ARCHIVE_CONTINUITY_BLOCKED: Redis frame overwritten')

        def missing_frame_resigned(data, target):
            redis(6398, 'DEL', frame0)
            del data['redis_contents'][frame0]
            return 'Redis frame 0 deleted; receipt contents follow it'
        retain(child(multi, 'restore', 'missing-frame-resigned', multi_cp, multi_store, multi_records,
                     multi_semantic, resigned(missing_frame_resigned), resign=True),
               reason='ARCHIVE_CONTINUITY_BLOCKED: archived Redis blob absent')

        def truncate_store(target):
            path = next((target / 'event_store').rglob('*.redb'))
            path.write_bytes(path.read_bytes()[:32])
            return {'native_anchor_source': 'truncated'}
        retain(child(multi, 'restore', 'truncated-redb', multi_cp, multi_store, multi_records, multi_semantic,
                     truncate_store), reason='EVENT_STORE_PRODUCER_PAIR_MISMATCH')

        def quote_change(kind):
            def change(data, _):
                context = data['market_context']
                if kind == 'missing_quote':
                    del data['market_context']
                    return kind
                quote = json.loads(context['native'])
                if kind == 'altered_quote_bytes':
                    quote['bid_price'] = quote['ask_price'] = '120.00'
                    context['native'] = json.dumps(quote, separators=(',', ':'))
                    return kind
                if kind == 'stale_quote':
                    quote['ts_event'] = quote['ts_init'] = data['state']['positions'][0]['native']['ts_last'] - 1
                elif kind == 'wrong_instrument_quote':
                    quote['instrument_id'] = 'ETHUSDT-PERP.SIM'
                elif kind == 'divergent_mark':
                    quote['bid_price'] = quote['ask_price'] = '120.00'
                elif kind == 'cross_paired_quote':
                    context['source']['run_id'] = multi_p['checkpoint']['run_id']
                context['native'] = json.dumps(quote, separators=(',', ':'))
                context['sha256'] = sha(context['native'].encode())
                context['instrument_id'] = quote['instrument_id']
                context['ts_event'] = quote['ts_event']
                return kind
            return change

        for kind, reason in [('missing_quote', 'OPEN_EXPOSURE_REQUIRES_RECONCILIATION'),
                             ('altered_quote_bytes', 'OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote bytes'),
                             ('stale_quote', 'OPEN_EXPOSURE_REQUIRES_RECONCILIATION: stale quote'),
                             ('wrong_instrument_quote', 'OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote instrument'),
                             ('cross_paired_quote', 'OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote source'),
                             ('divergent_mark', 'RECOVERY_NOT_QUALIFIED')]:
            retain(child(opened, 'restore', kind, open_cp, open_store, open_records, open_semantic,
                         resigned(quote_change(kind)), resign=True), reason=reason)

        def contradictory_order(target):
            key = next(k for k in open_records if ':orders:' in k)
            redis(6398, 'DEL', key)
            return {'deleted_native_key': key}
        retain(child(opened, 'restore', 'contradictory-order', open_cp, open_store, open_records, open_semantic,
                     contradictory_order), reason='REDIS_PRODUCER_PAIR_MISMATCH')
        retain(child(opened, 'restore', 'writable-connection', open_cp, open_store, open_records, open_semantic,
                     readonly=False), reason='READ_ONLY_RESTORE_CONNECTION_REQUIRED')
        retain(child(opened, 'restore', 'different-valid-redis', open_cp, open_store, multi_records, multi_semantic),
               reason='REDIS_PRODUCER_PAIR_MISMATCH')
        retain(child(multi, 'restore', 'different-valid-redb', multi_cp, open_store, multi_records, multi_semantic),
               reason='EVENT_STORE_PRODUCER_PAIR_MISMATCH')
        retain(child(multi, 'restore', 'truncated_receipt', multi_cp, multi_store, multi_records, multi_semantic,
                     lambda t: (t / 'checkpoint.json').write_bytes(b'{')))

        # C: N2-04 regressions on the frozen binary: one-cycle, zero-cycle, torn pair, crash windows.
        retain(child(reversal, 'restore', 'sealed-restore', rev_cp, rev_store, rev_records, rev_semantic), admitted=True)
        retain(child(reversal, 'duplicate', 'associated-duplicates', rev_cp, rev_store, rev_records, rev_semantic),
               admitted=True, duplicate=True)

        def torn(target):
            key = next(k for k in rev_records if ':accounts:' in k)
            redis(6398, 'DEL', key)
            return {'deleted_native_key': key}
        retain(child(reversal, 'restore', 'torn-pair', rev_cp, rev_store, rev_records, rev_semantic, torn),
               reason='REDIS_PRODUCER_PAIR_MISMATCH')
        rt, rt_records, rt_semantic, _ = produce('round_trip', 'round_trip')
        retain(child(rt, 'restore', 'sealed-restore', rt / 'checkpoint.json', rt / 'event_store', rt_records,
                     rt_semantic), admitted=True)
        for label, fault in [('absent_receipt', lambda t: (t / 'checkpoint.json').unlink()),
                             ('wrong_run', mutate_identity('run_id')),
                             ('stale_watermark', mutate_identity('watermark')),
                             ('invalid_marker', mutate_identity('checkpoint'))]:
            retain(child(reversal, 'restore', label, rev_cp, rev_store, rev_records, rev_semantic, fault))
        for boundary in ('before_seal', 'after_seal', 'after_drain', 'acknowledged'):
            case_root, case_records, case_semantic, _ = produce('crash_' + boundary, 'reversal', boundary)
            retain(child(case_root, 'restore', 'restart', case_root / 'checkpoint.json',
                         case_root / 'event_store', case_records, case_semantic), admitted=boundary == 'acknowledged')

        matrix['n2_05_regression'] = 'N2_05_NATIVE_CONTINUITY_PASSED'
        stage_d(matrix, retain, produce)

        # Original producer stores and receipts are byte-identical after every restore.
        for producer in matrix['producers']:
            root = ROOT / producer['label']
            assert files(root / 'event_store') == producer['source_files'], producer['label']
            assert files(root / 'native-record-bytes') == producer['record_files'], producer['label']
            if producer['checkpoint_sha256']:
                assert sha((root / 'checkpoint.json').read_bytes()) == producer['checkpoint_sha256']
        matrix['producers_unchanged'] = True
        cases = matrix['n2_06_cases']
        accepted = all(c['verdict'] in ('PROVEN', 'BOUNDED_DIVERGENCE') for c in cases)
        restored = all(c.get('restore_verdict', 'PROVEN') == 'PROVEN' for c in cases)
        matrix['outcome'] = ('N2_06_BLOCKED_UNPROVEN_POSITIVE' if not accepted else 'N2_06_NATIVE_CHARACTERIZED'
                             if restored else 'N2_06_NATIVE_CHARACTERIZED_FUNDED_RESTORE_UNSUPPORTED')
    except BaseException as error:
        matrix['hard_stop'] = repr(error)
        if matrix['stage_a_passed']:
            matrix['outcome'] = 'N2_05_FAILED'
        raise
    finally:
        matrix['physical_seconds'] = time.monotonic() - started
        matrix['binary_unchanged'] = sha(BINARY.read_bytes()) == matrix['binary_sha256']
        save(ROOT / 'results.json', matrix)
        print(json.dumps({k: matrix[k] for k in ('outcome', 'stage_a_passed', 'physical_seconds')}))
        assert matrix['binary_unchanged']
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
