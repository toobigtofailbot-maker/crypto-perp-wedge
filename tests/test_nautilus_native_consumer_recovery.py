"""Fresh-process native reload; opt-in task-owned Redis only, never real account state."""
import json
import os
import subprocess
import sys
import uuid

import pytest


def launch(path, *mode, success=True):
    result = subprocess.run([sys.executable, "-B", "-m", "tools.nautilus_adapter.native_consumer_acceptance",
        "--config", str(path), *mode], text=True, capture_output=True, timeout=40)
    if success:
        assert result.returncode == 0, result.stdout + result.stderr
        return json.loads(result.stdout.splitlines()[-1])
    assert result.returncode != 0, result.stdout
    return result


@pytest.mark.skipif(os.environ.get("CPW_NATIVE_RECOVERY_TESTS") != "1",
                    reason="requires explicitly task-owned isolated Redis")
@pytest.mark.parametrize("case", ["open", "flat"])
def test_native_fresh_process_read_only_recovery_and_no_resume(tmp_path, case):
    redis = pytest.importorskip("redis")
    admin = redis.Redis(username="controller", socket_timeout=3)
    path = tmp_path / "profile.json"
    config = {"profile": "NONCAPITAL_NATIVE", "trader_id": "CPWNATIVE-" + uuid.uuid4().hex[:12],
              "macro_flags_path": str(tmp_path / "missing.json"), "persist": True}
    path.write_text(json.dumps(config))
    admin.acl_setuser("default", enabled=True, nopass=True, keys=["*"], commands=["+@all"])
    try:
        original = launch(path, "--synthetic-case", case)
        prefix = "trader-" + config["trader_id"] + ":*"
        before = {k: admin.dump(k) for k in admin.scan_iter(prefix)}
        assert before
        # The same namespace cannot be restarted as a producer even with write permission.
        blocked = launch(path, "--synthetic-case", case, success=False)
        assert "no automatic resume" in blocked.stderr
        admin.acl_setuser("default", enabled=True, nopass=True, keys=["*"],
            commands=["-@all", "+@read", "+ping", "+info", "+config|get", "+acl|getuser",
                      "+client|setinfo", "+client|setname"])
        restored = launch(path, "--recover")
        assert restored["commands"] == 0 and restored["private_clients"] == 0
        assert restored["recovery"] == "NATIVE_READ_ONLY_HOLD"
        for field in ("orders", "order_events", "positions", "balance", "quantity", "trader_id"):
            assert restored[field] == original[field], field
        assert {k: admin.dump(k) for k in admin.scan_iter(prefix)} == before
        assert "NO_RESUME" in restored["authority"]
        # A missing native order is unknown state, not flat or a reconstruction request.
        order_key = next(k for k in before if b":orders:" in k)
        admin.delete(order_key)
        refused = launch(path, "--recover", success=False)
        assert "recovery" in refused.stderr or "integrity" in refused.stderr
    finally:
        admin.acl_setuser("default", enabled=True, nopass=True, keys=["*"], commands=["+@all"])


@pytest.mark.skipif(os.environ.get("CPW_NATIVE_RECOVERY_TESTS") != "1",
                    reason="requires explicitly task-owned isolated Redis")
def test_consumer_process_death_reloads_native_facts_without_resume(tmp_path):
    redis = pytest.importorskip("redis")
    admin = redis.Redis(username="controller", socket_timeout=3)
    path = tmp_path / "crash.json"
    config = {"profile": "NONCAPITAL_NATIVE", "trader_id": "CPWNATIVE-" + uuid.uuid4().hex[:12],
              "macro_flags_path": str(tmp_path / "missing.json"), "persist": True}
    path.write_text(json.dumps(config))
    code = '''
import asyncio, json, os, runpy, sys, time, redis
from src.runtime.paper_trader import run_native_noncapital
helpers = runpy.run_path('tests/test_nautilus_native_consumer.py')
source, ticks = helpers['fixture_inputs'](2)
class Crash(helpers['Targets']):
    def compute_desired_position(self, *args, **kw):
        if self.calls:
            config=json.load(open(sys.argv[1]))
            db=redis.Redis()
            prefix='trader-'+config['trader_id']+':'
            # Kill after native durable read-back, not an unacknowledged buffer.
            for _ in range(500):
                keys=list(db.scan_iter(prefix+'*'))
                if (db.llen(prefix+'accounts:CPWSIM-001')==2
                    and any(b':positions:' in k for k in keys)
                    and any(b':orders:' in k and db.llen(k)==3 for k in keys)
                    and db.exists(prefix+'index:orders_closed')):
                    time.sleep(.1)
                    os._exit(17)
                time.sleep(.01)
            raise AssertionError('native durable read-back unavailable')
        return super().compute_desired_position(*args, **kw)
asyncio.run(run_native_noncapital(sys.argv[1], signal_provider=Crash(), ticks=ticks, instrument=source))
'''
    child = subprocess.run([sys.executable, "-B", "-c", code, str(path)],
                           capture_output=True, text=True, timeout=40)
    assert child.returncode == 17, child.stdout + child.stderr
    before = {k: admin.dump(k) for k in admin.scan_iter("trader-" + config["trader_id"] + ":*")}
    admin.acl_setuser("default", enabled=True, nopass=True, keys=["*"],
        commands=["-@all", "+@read", "+ping", "+info", "+config|get", "+acl|getuser",
                  "+client|setinfo", "+client|setname"])
    try:
        first = launch(path, "--recover")
        second = launch(path, "--recover")
        assert first == second
        assert first["quantity"] == "0.001" and first["balance"] == "9999.96"
        assert first["commands"] == 0 and len(first["orders"]) == 1
        assert {k: admin.dump(k) for k in admin.scan_iter("trader-" + config["trader_id"] + ":*")} == before
    finally:
        admin.acl_setuser("default", enabled=True, nopass=True, keys=["*"], commands=["+@all"])
