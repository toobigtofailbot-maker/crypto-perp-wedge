"""Kill a real CLI producer after native durability, then start fresh read-only consumers."""
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

import pytest

from src.execution import nautilus_portfolio_contract as contract

helpers = runpy.run_path(str(Path(__file__).with_name("test_nautilus_native_portfolio.py")))
isolated_redis = helpers["isolated_redis"]

CRASH_PRODUCER = """
import sys, time
from src.execution import nautilus_native_backend as native
from src.runtime import paper_trader

observe = native._portfolio_observation
def pause(node, request, *args, **kwargs):
    import json
    evidence = observe(node, request, *args, **kwargs)
    if request["cycle_index"] == 2:
        print("P1_BEFORE_KILL:" + json.dumps(evidence), flush=True)
        time.sleep(30)
    return evidence

native._portfolio_observation = pause
sys.argv = ["paper_trader", "--native-portfolio", "--config", sys.argv[1]]
paper_trader.main()
"""


@isolated_redis
def test_two_symbol_process_kill_and_fresh_read_only_hold(tmp_path):
    import redis

    path = tmp_path / "requests.json"
    rows = helpers["requests"](targets=[("0.001", "0"), ("0.001", "0.40"), ("0", "0.40")])
    path.write_text(json.dumps(rows))
    profile = contract.profile(rows[0])
    prefix = f"trader-{profile['trader_id']}:"
    controller = redis.Redis(port=16379, username="controller", socket_timeout=2)
    process = subprocess.Popen([sys.executable, "-B", "-c", CRASH_PRODUCER, str(path)],
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for _ in range(500):
            keys = list(controller.scan_iter(prefix + "*"))
            order_keys = [key for key in keys if b":orders:" in key]
            if len(order_keys) == 3 and all(controller.llen(key) >= 3 for key in order_keys):
                if len([key for key in keys if b":positions:" in key]) == 2:
                    break
            if process.poll() is not None:
                break
            time.sleep(.04)
        else:
            pytest.fail("native durable order and position streams missing")
        assert process.poll() is None, process.communicate()
        def dump():
            return {key: controller.dump(key) for key in controller.scan_iter(prefix + "*")}
        # Require repeatable durable bytes before killing the still-running producer.
        before = dump()
        time.sleep(.25)
        assert before == dump()
        process.kill()
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode != 0
        original = json.loads(stdout.split("P1_BEFORE_KILL:")[-1])
        assert original["execution"]["registered_clients"] == 1
        assert len(original["portfolio"]["account_events"]) > 1
        assert {p["position_qty"] for p in original["per_symbol"]} == {"0", "0.40"}
        assert dump() == before
        controller.acl_setuser("default", enabled=True, nopass=True, keys=["*"],
            commands=["-@all", "+@read", "+ping", "+info", "+config|get", "+acl|getuser",
                      "+client|setinfo", "+client|setname"])
        with pytest.raises(redis.exceptions.NoPermissionError):
            redis.Redis(port=16379).set("cpw:laneb:p1:acl-negative", "refused")

        recovered = helpers["launch"](path, "--native-portfolio-recover")
        assert recovered.returncode == 0, recovered.stdout + recovered.stderr
        restore = json.loads(recovered.stdout.splitlines()[-1])["observations"][0]
        assert restore["execution"]["commands"] == restore["execution"]["registered_clients"] == 0
        assert restore["risk"]["disposition"] == "HOLD" and restore["risk"]["no_resume"]
        if evidence := os.environ.get("CPW_LANEB_P1_EVIDENCE"):
            out = Path(evidence)
            (out / "physical-request.json").write_bytes(path.read_bytes())
            (out / "physical-producer.json").write_text(json.dumps(original, indent=2))
            (out / "physical-recovery.json").write_text(recovered.stdout)
            (out / "physical-kill.json").write_text(json.dumps({
                "pid": process.pid, "exit": process.returncode, "stderr": stderr,
                "durable_sha256_before": {key.decode(): sha256(value).hexdigest()
                                          for key, value in before.items()},
                "durable_sha256_after": {key.decode(): sha256(value).hexdigest()
                                         for key, value in dump().items()},
            }, indent=2))
        assert restore["portfolio"] == original["portfolio"]
        for left, right in zip(original["per_symbol"], restore["per_symbol"], strict=True):
            for field in ("orders", "fills", "order_events", "positions", "position_qty", "position_snapshots"):
                assert left[field] == right[field], (field, left[field], right[field])
        assert dump() == before
        repeated = helpers["launch"](path, "--native-portfolio-recover")
        assert json.loads(repeated.stdout.splitlines()[-1])["observations"] == [restore]
        producer = helpers["launch"](path)
        assert producer.returncode and "no automatic resume" in producer.stderr
        assert dump() == before

        controller.delete(order_keys[0])
        corrupt = helpers["launch"](path, "--native-portfolio-recover")
        assert corrupt.returncode and "HOLD" in corrupt.stderr
        if evidence:
            (out / "physical-negative.log").write_text(
                producer.stderr + "\n" + corrupt.stderr)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=10)
        controller.acl_setuser("default", enabled=True, nopass=True, keys=["*"], commands=["+@all"])
@isolated_redis
def test_reopened_history_refuses_under_read_only_acl(tmp_path):
    import redis

    path = tmp_path / "requests.json"
    path.write_text(json.dumps(helpers["requests"]()))
    produced = helpers["launch"](path)
    assert produced.returncode == 0, produced.stdout + produced.stderr
    controller = redis.Redis(port=16379, username="controller", socket_timeout=2)
    controller.acl_setuser("default", enabled=True, nopass=True, keys=["*"],
        commands=["-@all", "+@read", "+ping", "+info", "+config|get", "+acl|getuser",
                  "+client|setinfo", "+client|setname"])
    try:
        refused = helpers["launch"](path, "--native-portfolio-recover")
        assert refused.returncode and "unsupported resized or reopened native position history; HOLD" in refused.stderr
    finally:
        controller.acl_setuser("default", enabled=True, nopass=True, keys=["*"], commands=["+@all"])
