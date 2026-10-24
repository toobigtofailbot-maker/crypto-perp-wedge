"""Physical v1.231.0 report oracles and fail-closed N3-01 boundary controls."""
import ast
import copy
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.nautilus_adapter import binance_usdm_offline_reports as proof

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def tape():
    return proof.load_fixture(proof.FIXTURE)


@pytest.fixture(scope="module")
def parsed(tmp_path_factory):
    with proof.safety_boundary(tmp_path_factory.mktemp("native-parser")) as state:
        result = proof.parse_tape(proof.load_fixture(proof.FIXTURE))
        assert state["violations"] == []
    return result


def test_actual_native_classes_filters_and_all_lifecycle_fields(parsed, tape):
    semantic, raw, objects = parsed
    from nautilus_trader.execution.reports import OrderStatusReport, FillReport, PositionStatusReport
    from nautilus_trader.model.instruments import CryptoPerpetual
    assert isinstance(objects[0], CryptoPerpetual)
    assert len(objects) == 28  # one instrument, 27 actual native reports
    assert sum(isinstance(r, OrderStatusReport) for r in objects) == 13
    assert sum(isinstance(r, FillReport) for r in objects) == 8
    assert sum(isinstance(r, PositionStatusReport) for r in objects) == 6
    assert len(raw) == 27
    assert semantic["instrument"] == {
        "type": "CryptoPerpetual", "id": "BTCUSDT-PERP.BINANCE", "is_inverse": False,
        "price_precision": 2, "size_precision": 3, "price_increment": "0.10",
        "size_increment": "0.001", "min_quantity": "0.001", "max_quantity": "1000.000",
        "min_notional": "5.00000000 USDT"}
    for rows in (semantic["rest_orders"], semantic["stream"]):
        assert [r["native"]["order_status"] for r in rows] == ["ACCEPTED", "PARTIALLY_FILLED", "FILLED", "ACCEPTED", "CANCELED"]
        assert [r["native"]["filled_qty"] for r in rows] == ["0.000", "0.004", "0.010", "0.000", "0.000"]
        assert [r["native"]["reduce_only"] for r in rows] == [False, False, False, True, True]
        for index, row in enumerate(rows):
            report = row["native"]
            source = tape["rest_orders"][index]
            assert report["account_id"] == "BINANCE-N3TEST"
            assert report["instrument_id"] == "BTCUSDT-PERP.BINANCE"
            assert report["venue_order_id"] == str(source["orderId"])
            assert report["client_order_id"] == source["clientOrderId"]
            assert report["order_side"] == source["side"]
            assert report["quantity"] == source["origQty"]
            assert report["price"] == source["price"]
            assert report["ts_last"] == source["updateTime"] * 1000000
            assert report["ts_init"] == source["updateTime"] * 1000000
    assert [r["source_last_qty"] for r in semantic["stream"]] == ["0.000", "0.004", "0.006", "0.000", "0.000"]
    # Native REST and WS acceptance-time behavior is intentionally different.
    assert semantic["rest_orders"][2]["native"]["ts_accepted"] == 1700000001000000000
    assert semantic["stream"][2]["native"]["ts_accepted"] == 1700000003000000000


def test_exact_native_fills_fees_and_position_signs(parsed):
    semantic, _, _ = parsed
    fills = [r["native"] for r in semantic["fills"]]
    assert [f["trade_id"] for f in fills] == ["501", "502"]
    assert [f["venue_order_id"] for f in fills] == ["101", "101"]
    assert [f["client_order_id"] for f in fills] == [None, None]
    assert [f["last_qty"] for f in fills] == ["0.004", "0.006"]
    assert [f["last_px"] for f in fills] == ["60000.00", "60000.00"]
    assert [f["liquidity_side"] for f in fills] == ["MAKER", "TAKER"]
    assert [f["commission"] for f in fills] == ["0.04800000 USDT", "0.18000000 USDT"]
    assert sum(Decimal(f["commission"].split()[0]) for f in fills) == Decimal("0.22800000")
    assert [f["ts_event"] for f in fills] == [1700000002000000000, 1700000003000000000]
    positions = semantic["positions"]
    assert [r["native"]["position_side"] for r in positions] == ["FLAT", "LONG", "SHORT"]
    assert [r["native"]["quantity"] for r in positions] == ["0.000", "0.010", "0.010"]
    assert [r["source_position_amt"] for r in positions] == ["0.000", "0.010", "-0.010"]
    assert all(r["native"]["venue_position_id"] is None for r in positions)
    assert all(r["native"]["ts_last"] == 1700000004000000000 for r in positions)


def test_three_snapshot_inputs_and_duplicate_observations_have_no_authority(parsed):
    semantic, _, _ = parsed
    assert [c["case_id"] for c in semantic["snapshots"]] == ["consistent", "missing_fill", "external_order"]
    assert [c["classifications"] for c in semantic["snapshots"]] == [
        ["CONSISTENT_INPUTS"], ["MISSING_FILL", "POSITION_DRIFT"], ["UNSEEN_EXTERNAL_ORDER"]]
    assert semantic["snapshots"][1]["missing_trade_ids"] == ["502"]
    assert semantic["snapshots"][2]["unseen_order_ids"] == ["303"]
    assert semantic["counted_trade_ids"] == ["501", "502"]
    assert [d["classification"] for d in semantic["duplicates"]] == ["IDENTICAL_DUPLICATE", "CONFLICTING_DUPLICATE"]
    assert all(d["counted"] is False for d in semantic["duplicates"])
    assert all(row["authority"] == proof.NO_AUTHORITY for row in semantic["snapshots"] + semantic["duplicates"])
    assert semantic["authority"] == proof.NO_AUTHORITY


# Each row changes one material input contract, including rehashed semantic
# defects: these tests reach validation directly rather than only a hash gate.
DEFECTS = [
    ("symbol", ("symbol",), "ETHUSDT"),
    ("venue", ("venue",), "OTHER"),
    ("account_mode", ("account_mode",), "HEDGE"),
    ("schema", ("schema",), "latest"),
    ("coin_m", ("exchange_info", "marginAsset"), "BTC"),
    ("ignored_native_amount", ("exchange_info", "liquidationFee"), "NaN"),
    ("native_enum", ("exchange_info", "orderTypes", 1), "INVALID"),
    ("enum", ("rest_orders", 0, "side"), "UP"),
    ("ws_enum", ("stream", 1, "o", "x"), "UNKNOWN"),
    ("missing_order_id", ("rest_orders", 0, "orderId"), None),
    ("missing_client_id", ("rest_orders", 0, "clientOrderId"), ""),
    ("missing_trade_id", ("trades", 0, "id"), None),
    ("nan", ("trades", 0, "price"), "NaN"),
    ("infinity", ("positions", 0, "positionAmt"), "Infinity"),
    ("negative_fee", ("trades", 0, "commission"), "-0.1"),
    ("negative_quantity", ("rest_orders", 0, "origQty"), "-0.010"),
    ("zero_step", ("exchange_info", "filters", 1, "stepSize"), "0.000"),
    ("invalid_step", ("exchange_info", "filters", 1, "stepSize"), "0.003"),
    ("price_off_step", ("rest_orders", 0, "price"), "60000.01"),
    ("fill_inconsistent", ("rest_orders", 2, "executedQty"), "0.009"),
    ("fill_quote", ("trades", 0, "quoteQty"), "241"),
    ("fill_side", ("trades", 0, "buyer"), False),
    ("fill_time", ("trades", 0, "time"), 1700000002500),
    ("stale_update", ("rest_orders", 1, "updateTime"), 1700000000001),
    ("event_order", ("stream", 1, "T"), 1700000000001),
    ("identity_conflict", ("rest_orders", 1, "clientOrderId"), "N3-FOREIGN"),
    ("cross_snapshot", ("snapshots", 0, "snapshot_id"), "N3-missing_fill"),
    ("snapshot_account", ("snapshots", 0, "account_id"), "BINANCE-OTHER"),
    ("snapshot_time", ("snapshots", 0, "position", "updateTime"), 1700000003000),
    ("snapshot_qty", ("snapshots", 0, "position", "positionAmt"), "0.005"),
    ("snapshot_order", ("snapshots", 0, "open_orders", 0, "clientOrderId"), "N3-FOREIGN"),
    ("position_mode", ("positions", 1, "positionSide"), "LONG"),
    ("malformed", ("stream", 0, "o"), {}),
]


def defective(tape, keys, value):
    changed = copy.deepcopy(tape)
    node = changed
    for key in keys[:-1]:
        node = node[key]
    node[keys[-1]] = value
    return changed


@pytest.mark.parametrize("name,keys,value", DEFECTS, ids=[d[0] for d in DEFECTS])
def test_semantic_defects_fail_closed_without_output(tape, tmp_path, name, keys, value):
    with proof.safety_boundary(tmp_path):
        with pytest.raises((proof.Rejected, KeyError, TypeError, ValueError)):
            proof.parse_tape(defective(tape, keys, value))
    assert list(tmp_path.iterdir()) == []


def test_closed_native_payload_and_extra_tape_fields(tape, tmp_path):
    tape["exchange_info"]["unexpected"] = "anything"
    with proof.safety_boundary(tmp_path), pytest.raises(proof.Rejected, match="unknown native payload"):
        proof.parse_tape(tape)
    tape.pop("trades")
    with pytest.raises(proof.Rejected):
        proof.validate(tape)


def test_missing_distinct_fill_and_duplicate_primary_trade_id(tape):
    tape["trades"][1]["id"] = 501
    with pytest.raises(proof.Rejected):
        proof.validate(tape)
    tape["trades"].pop()
    with pytest.raises(proof.Rejected):
        proof.validate(tape)


@pytest.mark.parametrize("field,value", [("price", "60000.10"), ("qty", "0.005"), ("commission", "0.04900000")])
def test_conflicting_duplicate_price_quantity_or_fee_never_counts_again(tape, tmp_path, field, value):
    row = tape["duplicates"][1]
    row[field] = value
    row["quoteQty"] = str(Decimal(row["qty"]) * Decimal(row["price"]))
    with proof.safety_boundary(tmp_path):
        semantic, _, _ = proof.parse_tape(tape)
    assert semantic["counted_trade_ids"] == ["501", "502"]
    assert semantic["duplicates"][1]["classification"] == "CONFLICTING_DUPLICATE"
    assert semantic["duplicates"][1]["counted"] is False


def test_invalid_cli_writes_failure_only_even_when_hash_gate_is_satisfied(tape, tmp_path, monkeypatch):
    # Test-only loader replacement exercises main's post-hash invalid-data path.
    # It never substitutes any native conversion or report/domain class.
    changed = defective(tape, ("rest_orders", 2, "executedQty"), "0.009")
    monkeypatch.setattr(proof, "load_fixture", lambda _: changed)
    output = tmp_path / "failed"
    assert proof.main(["--output-dir", str(output)]) == 2
    assert {p.name for p in output.iterdir()} == {"failure.json"}
    assert json.loads((output / "failure.json").read_bytes())["verdict"] == "FAILED"


def test_input_path_hash_and_output_containment(tmp_path):
    other = tmp_path / "tape.json"
    other.write_bytes(proof.FIXTURE.read_bytes())
    with pytest.raises(proof.Rejected):
        proof.load_fixture(other)
    with pytest.raises(proof.Rejected):
        proof.load_fixture(Path("tests/fixtures/nautilus_n3_01/binance_usdm_tape.json"))
    for path in (ROOT / "reports" / "n3-proof", Path("relative-proof"), tmp_path):
        with pytest.raises(proof.Rejected):
            proof.prepare_output(path)
    link = tmp_path / "linked"
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(proof.Rejected):
        proof.prepare_output(link / "out")


def _run(output, *, fixture=None, bootstrap=False):
    args = [sys.executable, "-B"]
    if bootstrap:
        # This harness is installed BEFORE the target module or its package is
        # imported, complementing the CLI's own native-import boundary.
        code = '''import os,sys,runpy,ctypes
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--output-dir')+1]).resolve()
sec=ctypes.CDLL('libseccomp.so.2',use_errno=True)
sec.seccomp_init.argtypes=[ctypes.c_uint];sec.seccomp_init.restype=ctypes.c_void_p
sec.seccomp_syscall_resolve_name.argtypes=[ctypes.c_char_p];sec.seccomp_syscall_resolve_name.restype=ctypes.c_int
sec.seccomp_rule_add.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_uint]
sec.seccomp_load.argtypes=[ctypes.c_void_p]
sec.seccomp_release.argtypes=[ctypes.c_void_p]
ctx=sec.seccomp_init(0x7fff0000)
assert ctx
for syscall in ('socket','socketpair','connect','sendto','sendmsg','sendmmsg','bind','listen','accept','accept4'):
    number=sec.seccomp_syscall_resolve_name(syscall.encode())
    assert number>=0 and sec.seccomp_rule_add(ctx,0x00050001,number,0)==0
assert sec.seccomp_load(ctx)==0
sec.seccomp_release(ctx)
libc=ctypes.CDLL(None,use_errno=True)
assert libc.socket(2,1,0)==-1 and ctypes.get_errno()==1
print('NETWORK_SYSCALL_FILTER_ACTIVE; native socket negative: EPERM',flush=True)
def guard(event,args):
    if event.startswith('socket.') or event in {'subprocess.Popen','os.system','os.posix_spawn'}:
        raise RuntimeError('FRESH_HARNESS_FORBIDDEN:'+event)
    if event=='open' and isinstance(args[0],(str,bytes)):
        p=Path(os.fsdecode(args[0])).absolute()
        if set(p.parts) & {'.env','credentials','.aws','.ssh','id_rsa','id_ed25519'}: raise RuntimeError('FRESH_HARNESS_CREDENTIAL_FILE')
        mode,flags=args[1:3]
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if writing and not p.resolve().is_relative_to(out): raise RuntimeError('FRESH_HARNESS_WRITE')
    if event=='import' and (args[0]=='src' or args[0].startswith(('src.','lib.'))): raise RuntimeError('FRESH_HARNESS_PROTECTED_IMPORT')
def profile(frame,event,arg):
    if event!='call': return
    module=frame.f_globals.get('__name__','')
    name=frame.f_code.co_name
    key=str(frame.f_locals.get('key','')).upper()
    if module=='os' and name in {'__getitem__','getenv'} and any(s in key for s in ('SECRET','TOKEN','PASSWORD','API_KEY','BINANCE')): raise RuntimeError('FRESH_HARNESS_CREDENTIAL_ENV')
    if (module=='hmac' and name in {'new','__init__','digest','hexdigest','update','_init_hmac','_init_old'}) or name in {'sign','sign_request','_sign','_sign_request'}: raise RuntimeError('FRESH_HARNESS_SIGNING')
    if module.startswith(('nautilus_trader.trading.trader','nautilus_trader.trading.strategy','nautilus_trader.risk.engine','nautilus_trader.execution.engine')) and name in {'__init__','start','run','execute','submit_order'}: raise RuntimeError('FRESH_HARNESS_RUNTIME')
sys.addaudithook(guard)
sys.setprofile(profile)
runpy.run_module('tools.nautilus_adapter.binance_usdm_offline_reports',run_name='__main__')
'''
        args += ["-c", code]
    else:
        args += ["-m", "tools.nautilus_adapter.binance_usdm_offline_reports"]
    args += ["--output-dir", str(output)]
    if fixture is not None:
        args += ["--fixture", str(fixture)]
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=60)


def test_two_guarded_fresh_process_runs_compare_real_fields_and_manifest(tmp_path):
    source = Path(proof.__file__).read_bytes()
    data = proof.FIXTURE.read_bytes()
    observations = []
    for index in range(2):
        output = tmp_path / str(index)
        process = _run(output, bootstrap=True)
        assert process.returncode == 0, process.stdout + process.stderr
        assert "NETWORK_SYSCALL_FILTER_ACTIVE" in process.stdout
        manifest = json.loads((output / "manifest.json").read_bytes())
        expected_hash = manifest.pop("self_sha256")
        assert proof.digest(manifest) == expected_hash
        assert manifest["input_sha256"] == proof.FIXTURE_SHA256
        for name, checksum in manifest["files"].items():
            assert hashlib.sha256((output / name).read_bytes()).hexdigest() == checksum
        observation = json.loads((output / "observations.json").read_bytes())
        assert proof.digest(observation) == manifest["semantic_sha256"]
        assert observation["fills"][0]["native"]["last_qty"] == "0.004"
        assert observation["fills"][1]["native"]["commission"] == "0.18000000 USDT"
        assert observation["positions"][2]["native"]["position_side"] == "SHORT"
        boundary = json.loads((output / "boundary.json").read_bytes())
        assert boundary["violations"] == []
        names = {r["module"] for r in boundary["upstream_modules"]}
        assert {"nautilus_trader.trading.strategy", "nautilus_trader.risk.engine", "nautilus_trader.trading.trader"} <= names
        raw = json.loads((output / "native-diagnostics.json").read_bytes())
        assert all(r["report"]["report_id"] for r in raw)
        observations.append(observation)
    assert observations[0] == observations[1]
    assert Path(proof.__file__).read_bytes() == source
    assert proof.FIXTURE.read_bytes() == data


def test_cli_bad_fixture_retains_only_failure_details(tmp_path):
    bad = tmp_path / "tampered.json"
    bad.write_text('{"malformed":true}')
    output = tmp_path / "failed"
    process = _run(output, fixture=bad, bootstrap=True)
    assert process.returncode == 2
    assert {p.name for p in output.iterdir()} == {"failure.json"}
    assert "FAILED" in process.stderr


def test_committed_hash_tamper_refused_in_fresh_process(tmp_path):
    # Controlled synthetic repository copy keeps exact module-relative path.
    # No original fixture/source is edited, and no fake native module is used.
    copy_root = tmp_path / "copy"
    module = copy_root / "tools/nautilus_adapter/binance_usdm_offline_reports.py"
    module.parent.mkdir(parents=True)
    module.write_bytes(Path(proof.__file__).read_bytes())
    fixture = copy_root / "tests/fixtures/nautilus_n3_01/binance_usdm_tape.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(proof.FIXTURE.read_bytes() + b" ")
    process = subprocess.run([sys.executable, "-B", str(module), "--output-dir", str(tmp_path / "failed")], text=True, capture_output=True, timeout=60)
    assert process.returncode == 2 and "SHA-256 mismatch" in process.stderr
    assert not (tmp_path / "failed/observations.json").exists()


@pytest.mark.parametrize("operation", ["socket", "dns", "http", "subprocess", "shell", "credential_file", "credential_env", "signing", "write", "protected_import"])
def test_side_effect_guards_reject_attempts_before_effects(tmp_path, operation):
    import hmac
    import socket
    import urllib.request
    target = tmp_path.parent / "forbidden-proof-write"
    with proof.safety_boundary(tmp_path) as state:
        with pytest.raises(proof.Rejected, match="BOUNDARY"):
            if operation == "socket":
                socket.socket()
            elif operation == "dns":
                socket.getaddrinfo("example.invalid", 443)
            elif operation == "http":
                urllib.request.urlopen("https://example.invalid")
            elif operation == "subprocess":
                subprocess.run([sys.executable, "-c", "raise SystemExit(99)"])
            elif operation == "shell":
                os.system("exit 99")
            elif operation == "credential_file":
                (tmp_path / "credentials").read_bytes()
            elif operation == "credential_env":
                os.environ.get("BINANCE_API_KEY")
            elif operation == "signing":
                hmac.new(b"synthetic", b"never signed")
            elif operation == "write":
                target.write_text("forbidden")
            else:
                sys.audit("import", "src.execution.oms", None, None, None, None)
        assert state["violations"]
    assert not target.exists()


def test_native_trader_entry_is_blocked_before_constructor_body(tmp_path):
    # The upstream method is not patched. The profile exception fires at its
    # call event, before its first instruction, so no Trader is constructed.
    from nautilus_trader.trading.trader import Trader
    with proof.safety_boundary(tmp_path) as state, pytest.raises(proof.Rejected, match="authority runtime entry"):
        Trader.__init__(*([None] * 11))
    assert state["violations"]


def test_direct_authority_imports_and_constructor_calls_are_absent():
    tree = ast.parse(Path(proof.__file__).read_text())
    modules = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    assert all(not name.startswith(("src", "lib", *proof.CONTROL_MODULES)) for name in modules)
    allowed_native_modules = {
        "nautilus_trader.adapters.binance.common.enums",
        "nautilus_trader.adapters.binance.common.schemas.account",
        "nautilus_trader.adapters.binance.futures.enums",
        "nautilus_trader.adapters.binance.futures.providers",
        "nautilus_trader.adapters.binance.futures.schemas.account",
        "nautilus_trader.adapters.binance.futures.schemas.market",
        "nautilus_trader.adapters.binance.futures.schemas.user",
        "nautilus_trader.common.providers", "nautilus_trader.core.uuid",
        "nautilus_trader.model.identifiers"}
    assert {name for name in modules if name.startswith("nautilus_trader.")} <= allowed_native_modules
    assert not set(calls) & proof.CONTROL_NAMES
    assert not set(calls) & {"eval", "exec", "__import__", "import_module", "submit_order", "cancel_order", "flatten", "start", "connect"}
