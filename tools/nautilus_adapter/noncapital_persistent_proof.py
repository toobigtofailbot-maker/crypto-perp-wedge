"""Finite, opt-in N4-02 Docker/PID controller. Owns only uniquely labelled resources."""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from tools.nautilus_adapter import noncapital_persistent_session as session

ROOT = Path(__file__).resolve().parents[2]
IMAGE = "cpw-n4-02-env01:exact-pins"
REDIS = "redis:7.4.2-bookworm"


class Controller:
    def __init__(self, output):
        self.output = Path(output).resolve()
        if not self.output.is_dir() or self.output.is_symlink() or self.output.is_junction() or any(self.output.iterdir()) or self.output.is_relative_to(ROOT):
            raise ValueError("empty ordinary external output required")
        self.prefix = "cpw-n4-02-" + uuid.uuid4().hex[:12]
        self.owned = []
        self.receipts = []
        self.counter = 0
        self.image = self.call(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"])["stdout"].strip()

    def call(self, args, *, ok=True, timeout=150):
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        receipt = {**session.LABELS, "argv": args, "exit": result.returncode,
                   "stdout": result.stdout, "stderr": result.stderr, "time_ns": time.time_ns()}
        self.receipts.append(receipt)
        (self.output / f"command-{len(self.receipts):03d}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        if ok and result.returncode:
            raise RuntimeError(f"command failed ({result.returncode}): {args}; {result.stdout[-2000:]} {result.stderr[-2000:]}")
        return receipt

    def owned_container(self, name):
        info = json.loads(self.call(["docker", "inspect", name])["stdout"])[0]
        if name not in self.owned or info["Config"]["Labels"].get("cpw.wp") != "CPW-NAUTILUS-N4-02":
            raise ValueError("unowned resource")
        return info

    def python(self, redis_name, code):
        return self.call(["docker", "run", "--rm", "--network", "container:" + redis_name,
                          "-v", str(self.output) + ":/tmp/proof:ro",
                          "-v", str(ROOT) + ":/repo:ro", "-w", "/repo",
                          "--entrypoint", "python", self.image, "-B", "-c", code])

    def command(self, redis_name, case_root, *args, hold=False):
        self.counter += 1
        name = self.prefix + "-python-" + str(self.counter)
        command = ["docker", "run", "--name", name, "--label", "cpw.wp=CPW-NAUTILUS-N4-02",
                   "--pid", "container:" + redis_name, "--network", "container:" + redis_name,
                   "--entrypoint", "python", "-v", str(ROOT) + ":/repo:ro",
                   "-v", str(self.output) + ":/tmp/proof" + (":ro" if args[0] == "restore" else ""),
                   "-w", "/repo", self.image, "-B", "-m", "tools.nautilus_adapter.noncapital_persistent_session",
                   args[0], "--proof-only", "--output", "/tmp/proof/" + case_root.name, *args[1:]]
        self.owned.append(name)
        if hold:
            # Detached only for the finite controller's acknowledged/unacknowledged OS kill.
            command.insert(2, "-d")
            self.call(command)
            return name
        result = self.call(command, ok=False)
        return name, result

    def readonly(self, name):
        self.call(["docker", "network", "disconnect", "bridge", name])
        info = self.owned_container(name)
        if info["NetworkSettings"]["Networks"]:
            raise ValueError("reader namespace retains external network")
        self.python(name, "import redis; d=redis.Redis(); d.acl_setuser('controller',enabled=True,nopass=True,keys=['*'],commands=['+@all']); "
                    "d.execute_command('ACL','SETUSER','default','on','nopass','~*','-@all','+@read','+ping','+info','+config|get','+acl|getuser','+client|setinfo','+client|setname')")

    def scenario(self, label, case, *, crash=False, before_ack=False):
        name = self.prefix + "-redis-" + label
        case_root = self.output / label
        case_root.mkdir()
        trader = "N2R" + uuid.uuid4().hex[:12] + "-001"
        self.call(["docker", "run", "-d", "--name", name, "--label", "cpw.wp=CPW-NAUTILUS-N4-02",
                   "--network", "bridge", REDIS, "redis-server", "--bind", "127.0.0.1", "--appendonly", "yes", "--appendfsync", "always"])
        self.owned.append(name)
        self.owned_container(name)
        self.python(name, "import redis,json; from tools.nautilus_adapter import noncapital_persistent_session as p; "
            "d=redis.Redis(); assert d.dbsize()==0; "
            f"owner={{**p.LABELS,'source':p.SOURCE,'controller':{self.prefix!r},'redis_run_id':d.info('server')['run_id']}}; "
            "d.set(p.OWNER_KEY,json.dumps(owner)); print(json.dumps(owner))")
        args = ["produce", "--case", case, "--trader", trader]
        if crash or before_ack:
            producer = self.command(name, case_root, *args, "--hold", *( ["--before-ack"] if before_ack else []), hold=True)
            checkpoint = case_root / ("unacknowledged.json" if before_ack else "ack.json")
            for _ in range(120):
                if checkpoint.exists():
                    break
                if not self.owned_container(producer)["State"]["Running"]:
                    raise RuntimeError(self.call(["docker", "logs", producer])["stdout"])
                time.sleep(1)
            else:
                raise TimeoutError("producer checkpoint absent")
            ack = json.loads(checkpoint.read_bytes())
            command_line = self.call(["docker", "exec", name, "cat", f"/proc/{int(ack['pid'])}/cmdline"])["stdout"]
            if "tools.nautilus_adapter.noncapital_persistent_session" not in command_line or "produce" not in command_line:
                raise ValueError("checkpoint PID does not identify owned native producer")
            if not before_ack:
                if session.public.file_hash(case_root / "manifest.json") != ack["sha256"]:
                    raise ValueError("pre-kill independent digest mismatch")
                self.python(name, "import json; from tools.nautilus_adapter import noncapital_persistent_session as p; "
                    f"m=json.load(open('/tmp/proof/{case_root.name}/manifest.json')); d,identity=p.backend(); "
                    "assert identity==m['backend'] and p.native.records(d,m['trader'])==m['records']; "
                    "a=d.info('persistence'); assert a['aof_last_write_status']=='ok' and a['aof_pending_bio_fsync']==0; "
                    "print(json.dumps({'verified_native_records':True,'aof':a['aof_last_write_status'],**p.LABELS}))")
            # Retained independently by controller before killing the producer.
            retained = {**session.LABELS, "checkpoint": ack, "producer": self.owned_container(producer),
                        "processes": self.call(["docker", "top", producer, "-eo", "pid,ppid,args"])["stdout"]}
            session.native.write_json(self.output / (label + "-retained-checkpoint.json"), retained)
            self.call(["docker", "kill", "--signal", "KILL", producer])
            stopped = self.owned_container(producer)["State"]
            if stopped["Running"] or stopped["ExitCode"] != 137:
                raise ValueError("OS kill not demonstrated")
        else:
            producer, result = self.command(name, case_root, *args)
            if result["exit"]:
                raise RuntimeError(result["stdout"] + result["stderr"])
        self.readonly(name)
        trusted = session.public.file_hash(case_root / "manifest.json") if not before_ack else "0" * 64
        if not before_ack:
            ack = json.loads((case_root / "ack.json").read_bytes())
            if ack["sha256"] != trusted:
                raise ValueError("controller independent digest mismatch")
        outcomes = []
        for _ in range(2):
            _, receipt = self.command(name, case_root, "restore", "--expected-manifest-sha256", trusted)
            result = json.loads(receipt["stdout"].splitlines()[-1])
            if before_ack:
                if receipt["exit"] != 1 or result["status"] != "BLOCKED":
                    raise ValueError("unacknowledged kill was admitted")
            elif receipt["exit"] or "_PROVEN" not in result["status"]:
                raise RuntimeError(receipt["stdout"] + receipt["stderr"])
            outcomes.append(result)
        if not before_ack and (outcomes[0]["pid"] == outcomes[1]["pid"] or outcomes[0]["projection_sha256"] != outcomes[1]["projection_sha256"]):
            raise ValueError("fresh reader projections differ")
        acl = self.python(name, "import redis,json; print(json.dumps(redis.Redis(username='controller',decode_responses=True).acl_log()))")
        if json.loads(acl["stdout"].splitlines()[-1]):
            raise ValueError("native reader attempted prohibited command")
        if label == "clean-open":
            self.refusals(name, case_root, trusted)
        result = {**session.LABELS, "case": label, "manifest_sha256": trusted, "readers": outcomes,
                  "status": "N4_02_UNACKNOWLEDGED_CRASH_REFUSED" if before_ack else
                            "N4_02_ACKNOWLEDGED_CRASH_RECOVERY_PROVEN" if crash else outcomes[0]["status"]}
        (self.output / (label + "-result.json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    def refusals(self, name, original, trusted):
        """Corrupt disposable evidence/record clones; keep the acknowledged source untouched."""
        manifest = json.loads((original / "manifest.json").read_bytes())
        before = session.public.file_hash(original / "manifest.json")
        outcomes = []
        for mutation in ("missing-ack", "torn-ack", "untrusted", "expired", "source", "version",
                         "trader", "run", "fee", "stale-quote", "filter", "mark"):
            target = self.output / ("refusal-" + mutation)
            shutil.copytree(original, target)
            m = copy.deepcopy(manifest)
            if mutation == "expired":
                m["time_ns"] -= 3_600_000_000_001
            elif mutation == "source":
                m["source"] = "wrong-source"
            elif mutation == "version":
                m["environment"]["versions"]["nautilus-trader"] = "wrong-version"
            elif mutation == "trader":
                m["trader"] = "N2R000000000000-001"
            elif mutation == "run":
                m["run_id"] = "wrong-run"
            elif mutation == "fee":
                m["state"]["balance"] = "10000"
            elif mutation == "stale-quote":
                m["quotes"][0]["observed_ns"] += 60_000_000_000
            elif mutation == "filter":
                m["filter_sha256"] = "0" * 64
            elif mutation == "mark":
                m["mark"]["mark"] = "1"
            # Re-seal the witness chain to exercise semantic checks beyond outer hashes.
            m["chain"][0]["payload"] = m["instrument"]
            for i, q in enumerate(m["quotes"], 1):
                m["chain"][i]["payload"] = q
            m["chain"][-2]["payload"] = m["state"]
            for i, row in enumerate(m["chain"]):
                row["previous"] = m["chain"][i-1]["sha256"] if i else None
                row["sha256"] = session.digest({k: v for k, v in row.items() if k != "sha256"})
            (target / "manifest.json").write_bytes(session.encoded(m))
            bound = session.public.file_hash(target / "manifest.json")
            ack = {**session.LABELS, "pid": m["pid"], "sha256": bound, "run_id": m["run_id"]}
            if mutation == "run":
                ack["run_id"] = manifest["run_id"]
            (target / "ack.json").write_bytes(session.encoded(ack))
            if mutation == "missing-ack":
                (target / "ack.json").unlink()
            if mutation == "torn-ack":
                (target / "ack.json").write_bytes(b'{"torn":')
            _, receipt = self.command(name, target, "restore", "--expected-manifest-sha256", "0" * 64 if mutation == "untrusted" else bound)
            result = json.loads(receipt["stdout"].splitlines()[-1])
            if receipt["exit"] != 1 or result["status"] != "BLOCKED":
                raise ValueError("corrupt evidence admitted: " + mutation)
            outcomes.append({"case": mutation, "error": result["error"], "exit": receipt["exit"]})
        # Copy genuine Redis bytes into an isolated network-none negative fixture.
        dump = self.python(name, "import redis,json,base64; d=redis.Redis(); print(json.dumps({k.decode():base64.b64encode(d.dump(k)).decode() for k in d.scan_iter()}))")["stdout"]
        (self.output / "native-negative-clone-dump.json").write_text(dump, encoding="utf-8")
        clone = self.prefix + "-redis-negative-clone"
        self.call(["docker", "run", "-d", "--name", clone, "--label", "cpw.wp=CPW-NAUTILUS-N4-02", "--network", "none",
                   REDIS, "redis-server", "--bind", "127.0.0.1", "--appendonly", "yes", "--appendfsync", "always"])
        self.owned.append(clone)
        for mutation in ("missing-record", "corrupt-record", "out-of-order-record"):
            code = "import redis,json,base64; d=redis.Redis(); raw=json.load(open('/tmp/proof/native-negative-clone-dump.json')); "
            code += "[d.restore(k,0,base64.b64decode(v),replace=True) for k,v in raw.items()]; "
            code += "k=next(k for k in d.scan_iter() if b':orders:' in k and d.type(k)==b'list'); "
            code += {"missing-record": "d.delete(k); ", "corrupt-record": "d.lset(k,-1,b'{torn'); ",
                     "out-of-order-record": "values=d.lrange(k,0,-1); d.delete(k); d.rpush(k,*reversed(values)); "}[mutation]
            code += "from tools.nautilus_adapter import noncapital_persistent_session as p; owner=json.loads(d.get(p.OWNER_KEY)); "
            code += "owner['redis_run_id']=d.info('server')['run_id']; d.set(p.OWNER_KEY,json.dumps(owner)); print(json.dumps(p.backend()[1]))"
            identity = json.loads(self.python(clone, code)["stdout"].splitlines()[-1])
            target = self.output / ("refusal-" + mutation)
            shutil.copytree(original, target)
            m = copy.deepcopy(manifest)
            m["backend"] = identity
            (target / "manifest.json").write_bytes(session.encoded(m))
            bound = session.public.file_hash(target / "manifest.json")
            (target / "ack.json").write_bytes(session.encoded({**session.LABELS, "pid": m["pid"], "sha256": bound, "run_id": m["run_id"]}))
            _, receipt = self.command(clone, target, "restore", "--expected-manifest-sha256", bound)
            result = json.loads(receipt["stdout"].splitlines()[-1])
            if receipt["exit"] != 1 or "native source/backend mismatch" not in result["error"]:
                raise ValueError("corrupt native clone was not refused before loader: " + mutation)
            outcomes.append({"case": mutation, "error": result["error"], "exit": 1})
        if session.public.file_hash(original / "manifest.json") != before or before != trusted:
            raise ValueError("negative controls mutated original evidence")
        _, receipt = self.command(name, original, "restore", "--expected-manifest-sha256", trusted)
        if receipt["exit"]:
            raise ValueError("negative controls invalidated original native source")
        (self.output / "refusals.json").write_text(json.dumps({**session.LABELS, "cases": outcomes}, indent=2), encoding="utf-8")

    def cleanup(self):
        results = []
        for name in reversed(self.owned):
            self.owned_container(name)
            results.append(self.call(["docker", "rm", "-f", "-v", name]))
        (self.output / "cleanup.json").write_text(json.dumps({**session.LABELS, "removed": len(results)}, indent=2), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-noncapital-proof", required=True, action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    controller = Controller(args.output)
    result = {**session.LABELS, "authority": session.AUTHORITY, "status": "BLOCKED", "cases": []}
    try:
        for label, case, crash, before in [("clean-open", "open", False, False), ("clean-flat", "flat", False, False),
                                           ("ack-kill", "open", True, False), ("preack-kill", "open", False, True)]:
            result["cases"].append(controller.scenario(label, case, crash=crash, before_ack=before))
        result["status"] = "NATIVE_SCENARIOS_PROVEN_PENDING_OTHER_WP_GATES"
    except Exception as exc:  # noqa: BLE001 - Preserve failure evidence and clean owned resources.
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        controller.cleanup()
        (args.output / "controller-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
