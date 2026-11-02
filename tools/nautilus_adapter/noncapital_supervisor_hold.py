"""Manual N4-03 proof contract. Offline inspection never reconstructs or resumes trading."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
import uuid

from tools.nautilus_adapter import noncapital_persistent_session as p

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "cpw_n4_03_supervisor_hold_v1"
BLOCKERS = ["AUTHENTICATED_VENUE_STATE_ABSENT", "PRODUCTION_SUPERVISOR_NOT_CONNECTED",
            "ACTIVE_TRADING_RESUME_NOT_AUTHORIZED", "MULTICYCLE_HISTORY_NOT_PROVEN",
            "FUNDED_STATE_AND_LIQUIDATION_UNPROVEN"]
DENIAL = {**p.LABELS, "authority": p.AUTHORITY, "disposition": "HOLD",
          "cpw_production_supervisor_connected": False, "authenticated_venue_reconciled": False,
          "execution_permit_issued": False, "blockers": BLOCKERS}
CASES = [("clean-open", "open", False, False), ("clean-flat", "flat", False, False),
         ("ack-kill", "open", True, False), ("preack-kill", "open", False, True)]
ZERO = {"new_orders": 0, "new_fills": 0, "execution_clients": 0, "native_commands": 0, "native_events": 0}
MANIFEST_KEYS = set("source authority trader case run_id instance_id pid process time_ns environment sources backend instrument quotes mark mark_observed_ns filter_sha256 requests state economics records chain aof".split()) | set(p.LABELS)
READER_KEYS = set("status authority pid process instance_id native projection_sha256 records_sha256 manifest_sha256".split()) | set(p.LABELS) | set(ZERO)
REFUSALS = ("missing-ack", "torn-ack", "untrusted", "expired", "source", "version", "trader", "run",
            "fee", "stale-quote", "filter", "mark", "missing-record", "corrupt-record", "out-of-order-record")
require = p.require


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_bytes(), object_pairs_hook=pairs,
                      parse_constant=lambda value: require(False, "nonfinite JSON: " + value))


def last(receipt):
    return json.loads(receipt["stdout"].splitlines()[-1], object_pairs_hook=pairs)


def external(path, *, empty=False):
    path = Path(path).absolute()
    require(path.is_dir(), "ordinary external directory required")
    for part in (path, *path.parents):
        require(not part.is_symlink() and not part.is_junction(), "linked output forbidden")
    root = path.resolve()
    require(not root.is_relative_to(ROOT) and not any(x.name == ".git" for x in root.iterdir()),
            "repository output forbidden")
    # Other checkouts also remain protected, including the root checkout on Windows.
    require(not any((x / ".git").exists() for x in (root, *root.parents)), "repository output forbidden")
    if empty:
        require(not any(root.iterdir()), "empty external output required")
    return root


def inventory(root):
    result = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink() and not path.is_junction(), "linked source forbidden")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {"size": path.stat().st_size, "sha256": sha(path)}
        else:
            require(path.is_dir(), "nonordinary evidence")
    return result


def labels(value):
    require(all(value.get(k) is v for k, v in p.LABELS.items()), "proof labels differ")


def identity(value):
    require(set(value) == {"pid", "pid_namespace"} and type(value["pid"]) is int and value["pid"] > 0
            and re.fullmatch(r"pid:\[\d+\]", value["pid_namespace"]), "missing process namespace/identity")
    return value["pid_namespace"], value["pid"]


def no_authority(value):
    if isinstance(value, dict):
        for key, item in value.items():
            require(not re.search(r"permit|authenticated_venue|admitted|ready_for|trading_ready|allow_orders|resume_authorized", key, re.I),
                    "unexpected authority assertion")
            no_authority(item)
    elif isinstance(value, list):
        for item in value:
            no_authority(item)


def checkpoint(root, trusted, sealed_ns):
    """Read-only source assertions; no backend, engine, client or current quote is loaded."""
    m = load(root / "manifest.json")
    require(set(m) == MANIFEST_KEYS, "unsupported native manifest fields")
    labels(m)
    no_authority(m)
    require(set(m["state"]) == {"native", "snapshots", "realized", "unrealized", "balance", "equity"}
            and set(m["state"]["native"]) == {"instruments", "accounts", "orders", "positions"}, "native state schema")
    require(sha(root / "manifest.json") == trusted and load(root / "ack.json") ==
            {**p.LABELS, "pid": m["pid"], "sha256": trusted, "run_id": m["run_id"]}, "native acknowledgement binding")
    require(m["source"] == p.SOURCE and m["authority"] == p.AUTHORITY and m["sources"] == p.sources(), "native source drift")
    require(0 <= sealed_ns - m["time_ns"] < 3_600_000_000_000, "stale checkpoint at seal")
    require(identity(m["process"])[1] == m["pid"], "producer identity mismatch")
    require(str(uuid.UUID(m["run_id"])) == m["run_id"] and str(uuid.UUID(m["instance_id"])) == m["instance_id"], "native run identity")
    e = m["environment"]
    lock = Path(p.public.n2.__file__).with_name("requirements-win-py312.lock.txt")
    pins = dict(line.split("==") for line in lock.read_text().splitlines())
    require(set(e) == {"python", "versions", "lock_sha256", "installed_sha256"}
            and e["python"] == "3.12.10" and e["versions"] == pins
            and e["lock_sha256"] == sha(lock) and bool(e["installed_sha256"])
            and all(re.fullmatch(r"[0-9a-f]{64}", x) for x in e["installed_sha256"].values()), "native environment pins")
    require(m["aof"] == {"aof_enabled": 1, "aof_last_write_status": "ok", "aof_pending_bio_fsync": 0}, "AOF incomplete")
    b = m["backend"]
    require(set(b) == {"run_id", "redis_version", "owner"}
            and set(b["owner"]) == set(p.LABELS) | {"source", "controller", "redis_run_id"}
            and b["redis_version"] == "7.4.2" and b["run_id"] == b["owner"]["redis_run_id"]
            and b["owner"]["source"] == p.SOURCE, "backend identity")
    labels(b["owner"])
    p.public.local_spec(m["instrument"])
    require(m["filter_sha256"] == p.digest(m["instrument"]["info"]["filters"]), "public filter mismatch")
    for i, row in enumerate(m["chain"]):
        require(set(row) == {"seq", "previous", "payload", "sha256"} and row["seq"] == i
                and row["previous"] == (m["chain"][i-1]["sha256"] if i else None)
                and row["sha256"] == p.digest({k: v for k, v in row.items() if k != "sha256"}), "native chain mismatch")
    payloads = [r["payload"] for r in m["chain"]]
    require(payloads[:1 + len(m["quotes"])] == [m["instrument"], *m["quotes"]]
            and payloads[-2:] == [m["state"], m["records"]], "native context binding")
    published = payloads[1 + len(m["quotes"]):-2]
    native = m["state"]["native"]
    events = [e for o in native["orders"].values() for e in o["events"] if e["type"] != "OrderInitialized"]
    events += [e for account in native["accounts"].values() for e in account[1:]]
    expected = {e["event_id"]: e for e in events}
    require(len(expected) == len(events), "duplicate native publication identity")
    observed, positions = {}, []
    for event in published:
        require(event["event_id"] not in observed, "duplicate publication")
        observed[event["event_id"]] = event
        if event["type"] in ("PositionOpened", "PositionClosed"):
            positions.append(event)
        else:
            require(event == expected.get(event["event_id"]), "publication/native event mismatch")
    require({k: v for k, v in observed.items() if v["type"] not in ("PositionOpened", "PositionClosed")} == expected,
            "missing native publication")
    require([e["type"] for e in positions] == (["PositionOpened"] if m["case"] == "open" else
            ["PositionOpened", "PositionClosed"]), "position publication sequence")
    for index, event in enumerate(positions):
        position = native["positions"][event["position_id"]]
        state, fill = position["state"], position["events"][index]
        for key in ("position_id", "trader_id", "account_id", "strategy_id", "instrument_id", "opening_order_id", "avg_px_open"):
            require(event[key] == state[key], "position publication identity")
        require(event["currency"] == state["settlement_currency"]
                and all(event[k] == fill[k] for k in ("last_px", "last_qty"))
                and event["ts_event" if index == 0 else "ts_closed"] == fill["ts_event"], "position publication/fill linkage")
        if index == len(positions)-1:
            require(all(event[k] == state[k] for k in ("signed_qty", "quantity", "side", "peak_qty", "realized_pnl"))
                    and event["duration_ns"] == (0 if m["case"] == "open" else state["duration_ns"]),
                    "final position publication/state mismatch")
        else:
            require(p.D(str(event["signed_qty"])) == p.public.QTY and p.D(event["quantity"]) == p.public.QTY
                    and event["side"] == "LONG" and p.public.n2._money(event["realized_pnl"]) == -p.public.n2._money(fill["commission"]),
                    "opening position publication mismatch")
    require(all(a["ts_event"] < b["ts_event"] for a, b in zip(m["quotes"], m["quotes"][1:])), "quote sequence")
    for q in m["quotes"]:
        p.public.validate_quote({k: v for k, v in q.items() if k != "observed_ns"}, m["instrument"], q["observed_ns"])
    mark = m["mark"]
    require(mark["kind"] == "mark" and mark["instrument_id"] == p.public.n3.NATIVE_ID
            and mark["native_type"] == "nautilus_trader.adapters.binance.futures.types.BinanceFuturesMarkPriceUpdate"
            and mark["source_hash"] == p.public.n3.digest({k: v for k, v in mark.items() if k not in ("source_hash", "ts_init")})
            and 0 <= m["mark_observed_ns"] - mark["ts_event"] <= 10_000_000_000
            and m["mark_observed_ns"] < mark["next_funding_ns"], "public mark binding")
    p.public.n3.positive(mark["mark"])
    p.public.n3.positive(mark["index"])
    require(p.D(mark["funding_rate"]).is_finite(), "nonfinite funding context")
    require(p.validate(m["state"], m["trader"], m["case"], m["quotes"]) == m["economics"], "economic summary mismatch")
    require(len(m["requests"]) == 2 and all(r == {"method": "GET", "url": p.public.n3.REST + "/fapi/v1/exchangeInfo", "signed": False}
            for r in m["requests"]), "nonpublic request")
    return m


def inspect_native(root, sealed_ns):
    """Bind native results to physical command receipts, independent readers and cleanup."""
    files = inventory(root)
    allowed_top = {"controller-result.json", "cleanup.json", "refusals.json", "native-negative-clone-dump.json",
                   "ack-kill-retained-checkpoint.json", "preack-kill-retained-checkpoint.json"}
    allowed_top |= {label + "-result.json" for label, *_ in CASES}
    dirs = {label for label, *_ in CASES} | {"refusal-" + x for x in REFUSALS}
    require(all(x.name in dirs for x in root.iterdir() if x.is_dir()), "alien source directory")
    for path in files:
        parts = path.split("/")
        require((len(parts) == 1 and (path in allowed_top or re.fullmatch(r"command-\d{3}\.json", path)))
                or (len(parts) == 2 and parts[0] in dirs and parts[1] in {"manifest.json", "ack.json", "unacknowledged.json"}),
                "alien source file: " + path)
    commands = [load(root / name) for name in sorted(files) if re.fullmatch(r"command-\d{3}\.json", name)]
    require(commands and [f"command-{i:03d}.json" for i in range(1, len(commands)+1)] ==
            sorted(x for x in files if re.fullmatch(r"command-\d{3}\.json", x)), "torn command sequence")
    for c in commands:
        labels(c)
        require(set(c) == set(p.LABELS) | {"argv", "exit", "stdout", "stderr", "time_ns"}
                and c["argv"][0] == "docker" and c["time_ns"] <= sealed_ns, "command provenance")
        if c["exit"]:
            require("restore" in c["argv"] and c["exit"] == 1 and last(c)["status"] == "BLOCKED", "failed physical command")
    def matching(*tokens):
        return [c for c in commands if all(t in c["argv"] for t in tokens)]
    def snapshots(name):
        return [json.loads(c["stdout"])[0] for c in matching("inspect", name)]
    summary = load(root / "controller-result.json")
    require(summary == {**p.LABELS, "authority": p.AUTHORITY,
            "status": "NATIVE_SCENARIOS_PROVEN_PENDING_OTHER_WP_GATES",
            "cases": [load(root / (label + "-result.json")) for label, *_ in CASES]}, "incomplete native matrix")
    cleanup = load(root / "cleanup.json")
    labels(cleanup)
    prefix = cleanup["network_removed"].removesuffix("-public")
    require(re.fullmatch(r"cpw-n4-02-[0-9a-f]{12}", prefix), "foreign controller")
    removed = matching("rm", "-f", "-v")
    names = [c["argv"][-1] for c in removed]
    require(cleanup["removed"] == len(names) == len(set(names)) and names, "cleanup incomplete")
    launches = matching("run", "--name")
    launched = [c["argv"][c["argv"].index("--name")+1] for c in launches]
    require(len(launched) == len(set(launched)) and set(launched) == set(names), "owned container cleanup mismatch")
    require(all("cpw.wp=CPW-NAUTILUS-N4-02" in c["argv"] for c in launches), "unlabelled fixture")
    require(len(matching("network", "rm", prefix + "-public")) == 1, "network not removed")
    net = matching("network", "inspect", prefix + "-public")
    require(net and json.loads(net[-1]["stdout"])[0]["Labels"].get("cpw.wp") == "CPW-NAUTILUS-N4-02"
            and not json.loads(net[-1]["stdout"])[0]["Containers"], "network cleanup ownership/attachments")
    for name in names:
        require(name.startswith(prefix + "-"), "foreign cleanup")
        info = snapshots(name)
        require(info and all(x["Config"]["Labels"].get("cpw.wp") == "CPW-NAUTILUS-N4-02" for x in info), "container ownership")
    bindings, runs, traders, namespaces = [], set(), set(), set()
    environment = None
    image = matching("image", "inspect")[0]["stdout"].strip()
    for label, case, crash, before_ack in CASES:
        result = load(root / (label + "-result.json"))
        require(set(result) == set(p.LABELS) | {"case", "manifest_sha256", "readers", "status"}, "case schema")
        labels(result)
        require(result["case"] == label and len(result["readers"]) == 2, "case/reader count")
        status = "N4_02_NATIVE_SINGLE_EXPOSURE_RECOVERY_PROVEN" if case == "open" else "N4_02_NATIVE_CLOSED_CYCLE_RECOVERY_PROVEN"
        require(result["status"] == ("N4_02_UNACKNOWLEDGED_CRASH_REFUSED" if before_ack else
                "N4_02_ACKNOWLEDGED_CRASH_RECOVERY_PROVEN" if crash else status), "forged native positive label")
        redis_name = prefix + "-redis-" + label
        infos = snapshots(redis_name)
        require(infos and any(not x["NetworkSettings"]["Networks"] for x in infos), "recovery not offline")
        redis_id = infos[0]["Id"]
        require(all(x["Id"] == redis_id for x in infos), "backend container changed")
        require(matching("network", "disconnect", prefix + "-public", redis_name), "public network retained")
        reads = matching("restore", "/tmp/proof/" + label)
        require(len(reads) == (3 if label == "clean-open" else 2)
                and [last(c) for c in reads[:2]] == result["readers"], "reader receipt binding")
        acl = [c for c in matching("container:" + redis_name, "-c") if "acl_log()" in c["argv"][-1]]
        require(len(acl) == 1 and last(acl[0]) == [], "ACL/write violation")
        acl_setup = [c for c in matching("container:" + redis_name, "-c") if "-@all" in c["argv"][-1]]
        require(len(acl_setup) == 1 and acl_setup[0]["time_ns"] < reads[0]["time_ns"], "read-only ACL absent")
        disconnected = matching("network", "disconnect", prefix + "-public", redis_name)
        require(disconnected[0]["time_ns"] < acl_setup[0]["time_ns"] and acl[0]["time_ns"] > reads[1]["time_ns"],
                "reader network/ACL chronology")
        producers = matching("produce", "/tmp/proof/" + label)
        require(len(producers) == 1, "producer receipt absent")
        producer_name = producers[0]["argv"][producers[0]["argv"].index("--name")+1]
        require(producer_name in names, "producer cleanup absent")
        if crash or before_ack:
            retained = load(root / (label + "-retained-checkpoint.json"))
            labels(retained)
            require(retained["producer"]["Name"] == "/" + producer_name
                    and retained["producer"]["State"]["Running"] is True
                    and "produce" in retained["processes"] and matching("kill", "KILL", producer_name)
                    and any(not x["State"]["Running"] and x["State"]["ExitCode"] == 137 for x in snapshots(producer_name)), "SIGKILL evidence absent")
            require(matching("exec", redis_name, "cat", f"/proc/{retained['checkpoint']['pid']}/cmdline"), "producer PID command linkage absent")
        if before_ack:
            require(result["manifest_sha256"] == "0"*64 and not (root / label / "ack.json").exists()
                    and not (root / label / "manifest.json").exists(), "pre-ack sealed unexpectedly")
            require(all(c["exit"] == 1 and last(c)["status"] == "BLOCKED" for c in reads), "pre-ack recovery admitted")
            for reader in result["readers"]:
                require(set(reader) == set(p.LABELS) | {"status", "authority", "pid", "error"}
                        and reader["authority"] == p.AUTHORITY and type(reader["pid"]) is int and reader["pid"] > 0
                        and reader["error"], "invalid pre-ack refusal")
                labels(reader)
            require(len({r["pid"] for r in result["readers"]}) == 2, "nonfresh pre-ack readers")
            require(retained["checkpoint"] == load(root / label / "unacknowledged.json"), "pre-ack kill binding")
            continue
        m = checkpoint(root / label, result["manifest_sha256"], sealed_ns)
        if not crash:
            require(last(producers[0]) == {**p.LABELS, "pid": m["pid"], "sha256": result["manifest_sha256"],
                    "case": case, "economics": m["economics"]}, "producer receipt/manifest mismatch")
        require(environment is None or environment == m["environment"], "conflicting native environment")
        environment = m["environment"]
        require(m["case"] == case and m["backend"]["owner"]["controller"] == prefix, "case/controller mismatch")
        require(m["run_id"] not in runs and m["trader"] not in traders, "replayed source")
        runs.add(m["run_id"])
        traders.add(m["trader"])
        processes = [identity(m["process"])]
        require(m["process"]["pid_namespace"] not in namespaces, "alien/shared case namespace")
        namespaces.add(m["process"]["pid_namespace"])
        for receipt in reads:
            r = last(receipt)
            require(set(r) == READER_KEYS, "reader schema")
            labels(r)
            require(receipt["exit"] == 0 and r["status"] == status and r["authority"] == p.AUTHORITY
                    and all(type(r[k]) is int and r[k] == v for k, v in ZERO.items()), "reader execution or invalid status")
            require(r["native"] == m["state"] and r["projection_sha256"] == p.digest(m["state"])
                    and r["records_sha256"] == p.digest(m["records"]) and r["manifest_sha256"] == result["manifest_sha256"], "reader projection conflict")
            proc = identity(r["process"])
            require(proc[1] == r["pid"] and proc[0] == processes[0][0] and proc not in processes
                    and r["instance_id"] != m["instance_id"], "nonfresh native reader")
            processes.append(proc)
            argv = receipt["argv"]
            name = argv[argv.index("--name")+1]
            info = snapshots(name)[-1]
            require(name in names and info["Image"] == image and info["HostConfig"]["PidMode"] == "container:" + redis_id
                    and info["HostConfig"]["NetworkMode"] == "container:" + redis_id
                    and any(x["Destination"] == "/tmp/proof" and x["RW"] is False for x in info["Mounts"]), "reader isolation binding")
        require(len({r["instance_id"] for r in result["readers"]}) == 2, "same native reader instance")
        if crash:
            require(retained["checkpoint"] == load(root / label / "ack.json"), "acknowledged kill binding")
        bindings.append({"case": label, "run_id": m["run_id"], "trader": m["trader"], "producer": m["process"],
                         "readers": [r["process"] for r in result["readers"]], "manifest_sha256": result["manifest_sha256"],
                         "projection_sha256": p.digest(m["state"]), "records_sha256": p.digest(m["records"]),
                         "economics": m["economics"]})
    refusals = load(root / "refusals.json")
    labels(refusals)
    require([x["case"] for x in refusals["cases"]] == list(REFUSALS)
            and all(x["exit"] == 1 and x["error"] for x in refusals["cases"]), "incomplete genuine recovery negatives")
    for refusal in refusals["cases"]:
        receipts = matching("restore", "/tmp/proof/refusal-" + refusal["case"])
        require(len(receipts) == 1 and receipts[0]["exit"] == 1 and last(receipts[0])["status"] == "BLOCKED"
                and last(receipts[0])["error"] == refusal["error"], "native refusal receipt binding")
    return {"controller": prefix, "image_id": image, "sources": p.sources(), "cases": bindings,
            "preack_refused": True, "cleanup_verified": True}


def durable(path, value):
    p.public.durable(path, p.encoded(value))


def seal(root):
    sealed_ns = time.time_ns()
    binding = inspect_native(root / "native", sealed_ns)
    shutil.copytree(root / "native", root / "source-proofs")
    record = {"schema": SCHEMA, "owner": "CPW-NAUTILUS-N4-03", **DENIAL,
              "sealed_ns": sealed_ns, "binding": binding, "bridge_sha256": sha(Path(__file__)),
              "files": inventory(root)}
    durable(root / "supervisor-hold.json", record)
    trusted = sha(root / "supervisor-hold.json")
    # Last write is the acknowledgment. A killed/torn seal has no valid HOLD package.
    durable(root / "hold-ack.json", {"schema": SCHEMA, "hold_sha256": trusted, "sealed_ns": sealed_ns})
    return trusted


def verify(output, expected):
    root = external(output)
    require({x.name for x in root.iterdir()} == {"native", "source-proofs", "supervisor-hold.json", "hold-ack.json"},
            "incomplete/alien HOLD package")
    require(re.fullmatch(r"[0-9a-f]{64}", expected or ""), "caller trust digest required")
    require(sha(root / "supervisor-hold.json") == expected, "untrusted HOLD digest")
    record = load(root / "supervisor-hold.json")
    require(set(record) == {"schema", "owner", "sealed_ns", "binding", "bridge_sha256", "files"} | set(DENIAL), "unknown HOLD fields")
    require(record["schema"] == SCHEMA and record["owner"] == "CPW-NAUTILUS-N4-03"
            and all(p.encoded(record[k]) == p.encoded(v) for k, v in DENIAL.items()), "denial/schema contradiction")
    require(record["bridge_sha256"] == sha(Path(__file__)), "bridge source drift")
    require(type(record["sealed_ns"]) is int and 0 < record["sealed_ns"] <= time.time_ns(), "invalid seal timestamp")
    require(load(root / "hold-ack.json") == {"schema": SCHEMA, "hold_sha256": expected, "sealed_ns": record["sealed_ns"]}, "missing/torn HOLD acknowledgment")
    before = inventory(root)
    require({k: v for k, v in before.items() if k not in {"supervisor-hold.json", "hold-ack.json"}} == record["files"], "source file set/hash mismatch")
    require(inventory(root / "native") == inventory(root / "source-proofs"), "copied source mismatch")
    require(record["binding"] == inspect_native(root / "source-proofs", record["sealed_ns"]), "physical binding mismatch")
    require(inventory(root) == before, "verification changed evidence")
    return {"status": "VERIFIED_HOLD", **DENIAL, "hold_sha256": expected, "pid": os.getpid(),
            "inspection": "OFFLINE_ARTIFACT_ONLY_NOT_FRESH_NATIVE_RECOVERY", **ZERO}


def run(output):
    from tools.nautilus_adapter.noncapital_persistent_proof import Controller
    root = external(output, empty=True)
    source_at_start = (sha(Path(__file__)), p.sources())
    native = root / "native"
    native.mkdir()
    controller = Controller(native)
    result = {**p.LABELS, "authority": p.AUTHORITY, "status": "BLOCKED", "cases": []}
    try:
        for label, case, crash, before in CASES:
            result["cases"].append(controller.scenario(label, case, crash=crash, before_ack=before))
        result["status"] = "NATIVE_SCENARIOS_PROVEN_PENDING_OTHER_WP_GATES"
    except Exception as exc:  # noqa: BLE001 - Retain failed proof, always clean owned resources.
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        controller.cleanup()
        durable(native / "controller-result.json", result)
    require(result["status"] != "BLOCKED", result.get("error", "native recovery absent"))
    require(source_at_start == (sha(Path(__file__)), p.sources()), "source changed during physical proof")
    trusted = seal(root)
    return verify(root, trusted)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    execute = sub.add_parser("run")
    execute.add_argument("--public-noncapital-proof", required=True, action="store_true")
    execute.add_argument("--output", type=Path, required=True)
    inspect = sub.add_parser("verify")
    inspect.add_argument("--output", type=Path, required=True)
    inspect.add_argument("--expected-hold-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        result = run(args.output) if args.action == "run" else verify(args.output, args.expected_hold_sha256)
    except Exception as exc:  # noqa: BLE001 - Invalid evidence has no successful HOLD attestation.
        result = {"status": "BLOCKED", "authority": p.AUTHORITY, "execution_permit_issued": False,
                  "error": f"{type(exc).__name__}: {exc}", "pid": os.getpid()}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "VERIFIED_HOLD" else 1


if __name__ == "__main__":
    raise SystemExit(main())
