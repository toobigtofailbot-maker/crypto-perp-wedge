"""N3-04 offline native LiveExecutionEngine application of N3-03 Binance USD-M mass status.

The real NautilusTrader 1.231.0 ``LiveExecutionEngine`` receives the actual
``ExecutionMassStatus`` objects produced by the N3-03 native Binance futures
client (startup and transport-originated reconnect), through its own bus
endpoint, in a disposable Cache/Portfolio. A proof-only admission check built on
the N3-03 witness runs first; refused reports never reach the gated engine.
Ungated hazard probes run in separate disposable state and are labelled
non-authoritative. Engine results, cache contents and the engine-local boolean
are observations only: every decision stays fixed, nothing here can adopt,
cancel, trade or resume.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from tools.nautilus_adapter import binance_usdm_private_reconcile as n3_03
from tools.nautilus_adapter.binance_usdm_offline_reports import Rejected, canonical, digest, require

n3_01 = n3_03.n3_01
DECISION = n3_03.DECISION
ENDPOINT = "ExecEngine.reconcile_execution_mass_status"
ENGINE_SOURCE_SHA256 = "7482c888455010fac2488e341a4be159becf43c0f4652c9c564c6fa9572da81d"  # installed 1.231.0 wheel
# Venue moved since CPW's held receipt. A complete snapshot carrying only these is applied for observation.
OBSERVABLE = {"ORDER_STATE_ADVANCED", "POSITION_CHANGED_VS_HELD", "UNHELD_FILL_DISCOVERED", "UNKNOWN_EXTERNAL_OPEN_ORDER"}
GATE_BASE = "active"  # refused reports are offered to the populated ordinary state: it must not change
PROBES = {"missing_fill": {}, "rate_limited": {}, "duplicate_trade": {},
          "external_order": {"filter_unclaimed_external_orders": True}}
PROBE_LABEL = "NON_AUTHORITATIVE_HAZARD_OBSERVATION"
CONFIG_FIELDS = ("reconciliation", "filter_unclaimed_external_orders", "filter_position_reports",
                 "generate_missing_orders", "allow_overfills", "manage_own_order_books")
# Engine-synthesised identities: random UUID4 client ids, ids hashed from them, partial-window "S-" ids.
_ENGINE_ID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|S-[0-9a-f]{16}-[0-9a-f]{8}")


def admit(witness):
    """Proof-only admission: never a CPW permission, only whether the disposable engine may see the report."""
    reasons = sorted(set(witness["anomalies"]) - OBSERVABLE)
    if witness["state_completeness"] != "COMPLETE_FOR_ISSUED_QUERIES":
        reasons.insert(0, "INCOMPLETE_OR_UNKNOWN")
    return {"admitted": not reasons, "refusal_reasons": reasons,
            "label": "REFUSED_BEFORE_APPLICATION" if reasons else "ADMITTED_FOR_OBSERVATION_ONLY"}


def _observe(loop, fixture, tape, name):
    native = {}
    receipt, log = loop.run_until_complete(n3_03._native_run(fixture, tape, name, native=native))
    loop.run_until_complete(asyncio.sleep(0))  # let cancelled native tasks finish
    return receipt, n3_03.witness(fixture, name, receipt, log), native


def _engine(loop, native, overrides):
    from nautilus_trader.cache.cache import Cache
    from nautilus_trader.common.component import MessageBus, TestClock
    from nautilus_trader.config import LiveExecEngineConfig
    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    from nautilus_trader.model.identifiers import TraderId
    from nautilus_trader.portfolio.portfolio import Portfolio

    clock = TestClock()
    clock.set_time(n3_03.CLOCK_NS)
    msgbus = MessageBus(TraderId("N3-004"), clock)
    cache = Cache()
    portfolio = Portfolio(msgbus, cache, clock)
    cache.add_instrument(native["instrument"])
    portfolio.update_account(native["account_state"])
    config = LiveExecEngineConfig(**overrides)
    engine = LiveExecutionEngine(loop=loop, msgbus=msgbus, cache=cache, clock=clock, config=config)
    require(type(engine) is LiveExecutionEngine and ENDPOINT in msgbus.endpoints(), "engine endpoint not bound")
    events = []
    msgbus.subscribe("events.order.*", events.append)
    msgbus.subscribe("events.position.*", events.append)
    return {"msgbus": msgbus, "cache": cache, "portfolio": portfolio, "events": events, "seen": 0, "watermark": 0,
            "instrument_id": native["instrument"].id, "config": {k: getattr(config, k) for k in CONFIG_FIELDS}}


def _event(event):
    data = type(event).to_dict(event)
    data.pop("event_id", None)
    return data


def snapshot(state):
    from nautilus_trader.model.enums import position_side_to_str
    from nautilus_trader.model.events import OrderFilled
    cache, iid = state["cache"], state["instrument_id"]
    orders = []
    # Sorted on economics, never on engine-synthesised ids (they are random per process).
    for order in sorted(cache.orders(), key=lambda o: (o.ts_last, o.side_string(), str(o.quantity), o.client_order_id.value)):
        orders.append({"client_order_id": order.client_order_id.value, "venue_order_id": str(order.venue_order_id),
                       "strategy_id": order.strategy_id.value, "tags": order.tags, "status": order.status_string(),
                       "side": order.side_string(), "type": order.type_string(), "quantity": str(order.quantity),
                       "filled_qty": str(order.filled_qty), "trade_ids": [t.value for t in order.trade_ids],
                       "events": [type(e).__name__ for e in order.events],
                       "venue_index": str(cache.client_order_id(order.venue_order_id)) if order.venue_order_id else None})
    fills = [_event(e) for o in cache.orders() for e in o.events if isinstance(e, OrderFilled)]
    positions = [{"id": p.id.value, "side": position_side_to_str(p.side), "signed_qty": str(p.signed_decimal_qty()),
                  "quantity": str(p.quantity), "avg_px_open": str(p.avg_px_open), "realized_pnl": str(p.realized_pnl),
                  "commissions": [str(c) for c in p.commissions()], "trade_ids": [t.value for t in p.trade_ids],
                  "is_open": p.is_open} for p in sorted(cache.positions(), key=lambda p: p.id.value)]
    fills.sort(key=lambda f: (f["ts_event"], f["order_side"], f["last_qty"], f["trade_id"]))
    return {"orders": orders, "fills": fills, "positions": positions,
            "net_position": str(state["portfolio"].net_position(iid)),
            "account_balances": [str(m) for m in cache.account_for_venue(iid.venue).balances_total().values()], "counts": {
                "orders": len(orders), "fills": len(fills), "positions": len(positions), "events": len(state["events"])}}


def apply(state, route, mass, calls):
    """Deliver one native mass status to the real engine endpoint, as the native client does."""
    before = dict(calls)
    state["msgbus"].send(ENDPOINT, mass)
    trace = {k.rsplit(".", 1)[-1]: v - before.get(k, 0) for k, v in calls.items()
             if ".live.execution_engine." in k and v != before.get(k, 0)}
    new, state["seen"] = state["events"][state["seen"]:], len(state["events"])
    return {"route": route, "engine_application_attempted": True, "engine_calls": dict(sorted(trace.items())),
            "events": [_event(e) for e in new], "after": snapshot(state)}


def _observations(result, venue_trades):
    """CPW labels for what the engine did. Labels never authorise adoption, cancel or resume."""
    labels, final = set(), result["after"]
    for order in final["orders"]:
        if "VENUE" in (order["tags"] or []):
            labels.add("ENGINE_EXTERNAL_ORDER_IN_DISPOSABLE_CACHE_NOT_ADOPTABLE")
        if "RECONCILIATION" in (order["tags"] or []) or order["venue_order_id"].startswith("S-"):
            labels.add("ENGINE_SYNTHETIC_RECONCILIATION_ORDER")
    for fill in final["fills"]:
        if fill["trade_id"] not in venue_trades:
            labels.add("ENGINE_FILL_NOT_VENUE_CONFIRMED")
    return sorted(labels)


def _normalize(value, ids):
    """Engine-synthesised identities become first-seen tokens (raw values go to provenance); economics untouched."""
    if isinstance(value, dict):
        return {k: _normalize(v, ids) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v, ids) for v in value]
    if isinstance(value, str):
        return _ENGINE_ID.sub(lambda m: ids.setdefault(m.group(0), f"ENGINE_ID#{len(ids)}"), value)
    return value


def _watermark(mass):
    """Latest venue time in a native report (order ts_last, fill ts_event); native position ts_last is init time."""
    return max([r.ts_last for r in mass.order_reports.values()] +
               [f.ts_event for rows in mass.fill_reports.values() for f in rows], default=0)


def gated_apply(state, witness, native, calls):
    """The only gated delivery path: refused reports, and reports older than applied state, are never sent."""
    admission, records = admit(witness), []
    for route, mass in native["mass"] if admission["admitted"] else ():
        mark = _watermark(mass)
        if mark < state["watermark"]:
            # The engine has no ordering guard: an older snapshot makes it synthesise position-diff trades.
            records.append({"route": route, "engine_application_attempted": False,
                            "refusal_reasons": ["REPORT_OLDER_THAN_APPLIED_STATE"]})
            continue
        state["watermark"] = mark
        records.append(apply(state, route, mass, calls))
    return admission, records


def _run_engine(loop, observed, calls, overrides=None, gated=True):
    receipt, witness, native = observed
    state = _engine(loop, native, overrides or {})
    before = snapshot(state)
    if gated:
        applications = gated_apply(state, witness, native, calls)[1]
    else:
        applications = [apply(state, route, mass, calls) for route, mass in native["mass"]]
    result = {"config": state["config"], "before": before, "applications": applications,
              "engine_application_attempted": any(a["engine_application_attempted"] for a in applications)}
    return _finish(result, state, receipt), state


def _finish(result, state, receipt):
    result["after"] = snapshot(state)
    venue_trades = {f["trade_id"] for r in receipt["routes"] if r["mass_status"] for f in r["mass_status"]["fills"]}
    result["engine_observations"] = _observations(result, venue_trades)
    return result


def run_all(loop):
    require(sys.version_info[:3] == (3, 12, 10), "requires isolated CPython 3.12.10")
    import nautilus_trader.live.execution_engine as engine_module
    require(hashlib.sha256(Path(engine_module.__file__).read_bytes()).hexdigest() == ENGINE_SOURCE_SHA256,
            "installed LiveExecutionEngine source differs from the pinned wheel")
    state = n3_03._STATE
    require(state is not None and state["allow"] is engine_module.LiveExecutionEngine,
            "run only inside the N3-03 boundary with the exact LiveExecutionEngine opt-in")
    calls = state["calls"]
    fixture, tape = n3_03.load_fixture(), n3_01.load_fixture(n3_01.FIXTURE)
    observed = {name: _observe(loop, fixture, tape, name) for name in n3_03.SCENARIOS}
    results, states = {}, {}
    for name in n3_03.SCENARIOS:
        witness = observed[name][1]
        result = results[name] = {"witness_anomalies": witness["anomalies"], "state_completeness": witness["state_completeness"],
                                  "admission": admit(witness), "engine_application_attempted": False, "decision": DECISION}
        if not result["admission"]["admitted"]:
            continue
        applied, states[name] = _run_engine(loop, observed[name], calls)
        result.update(applied)
        # Replay: a freshly generated native report of the same venue state, applied to the same engine.
        _, witness2, native2 = _observe(loop, fixture, tape, name)
        require(witness2 == witness, "fresh native report diverged: " + name)
        result["replay"] = gated_apply(states[name], witness2, native2, calls)[1]
        result["replay_state_unchanged"] = snapshot(states[name]) == result["after"]
    base = states[GATE_BASE]
    reference = snapshot(base)
    for name, result in results.items():
        if not result["admission"]["admitted"]:
            # Offer the refused report to the populated ordinary state through the same gate.
            _, applications = gated_apply(base, observed[name][1], observed[name][2], calls)
            result.update(gated_against=GATE_BASE, state_unchanged=not applications and snapshot(base) == reference)
    # Probes use fresh native reports: the engine mutates the reports it reconciles.
    probes = {name: {"label": PROBE_LABEL, "decision": DECISION,
                     **_run_engine(loop, _observe(loop, fixture, tape, name), calls, overrides, gated=False)[0]}
              for name, overrides in PROBES.items()}
    observed_gap = _observe(loop, fixture, tape, "reconnect_gap")
    stale, state = _run_engine(loop, observed_gap, calls, gated=False)
    older = dict(_observe(loop, fixture, tape, "reconnect_gap")[2]["mass"])["startup"]
    stale["applications"].append(apply(state, "stale_redelivery/startup", older, calls))
    probes["stale_redelivery"] = {"label": PROBE_LABEL, "decision": DECISION, **_finish(stale, state, observed_gap[0])}
    ids = {}
    semantic = _normalize({"scenarios": results, "hazard_probes": probes}, ids)
    return semantic, {token: raw for raw, token in ids.items()}


def engine_identity():
    import inspect
    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    return {"class": LiveExecutionEngine.__module__ + "." + LiveExecutionEngine.__qualname__,
            "source": inspect.getsourcefile(LiveExecutionEngine), "source_sha256": ENGINE_SOURCE_SHA256,
            "public_entry_returns": "None (engine-local bool is internal and never a CPW clearance)"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    output = n3_01.prepare_output(args.output_dir)
    sys.dont_write_bytecode = True
    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    loop = asyncio.new_event_loop()
    seccomp = n3_03.deny_socket_syscalls()
    output.mkdir()
    with n3_03.safety_boundary(output, allow=LiveExecutionEngine) as boundary:
        try:
            semantic, volatile = run_all(loop)
            require(not boundary["violations"], "observed forbidden behavior")
            require(hashlib.sha256(n3_03.FIXTURE.read_bytes()).hexdigest() == n3_03.FIXTURE_SHA256, "input changed during run")
            semantic = {"fixture_id": n3_03.FIXTURE_ID, "native_pin": "1.231.0", "engine": engine_identity(),
                        "decision": DECISION, **semantic}
            records = {"semantic.json": semantic,
                       "provenance.json": {"pid": os.getpid(), "seccomp": seccomp, "native_calls": boundary["calls"],
                                           "engine_ids": volatile, "violations": boundary["violations"],
                                           "upstream_modules": n3_01.upstream_inventory()}}
            hashes = {}
            for file, record in records.items():
                data = canonical(record) + b"\n"
                (output / file).write_bytes(data)
                hashes[file] = hashlib.sha256(data).hexdigest()
            manifest = {"fixture_id": n3_03.FIXTURE_ID, "input_sha256": n3_03.FIXTURE_SHA256,
                        "semantic_sha256": digest(semantic), "files": hashes,
                        "module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        "n3_03_module_sha256": hashlib.sha256(Path(n3_03.__file__).read_bytes()).hexdigest(),
                        "decision": DECISION, "verdict": "N3_04_NATIVE_ENGINE_APPLICATION_OBSERVED"}
            manifest["self_sha256"] = digest(manifest)
            (output / "manifest.json").write_bytes(canonical(manifest) + b"\n")
            print(json.dumps({"verdict": manifest["verdict"], "semantic_sha256": manifest["semantic_sha256"], "seccomp": seccomp}))
            return 0
        except Exception as exc:
            failure = {"verdict": "N3_04_BLOCKED", "error_type": type(exc).__name__, "error": str(exc),
                       "decision": DECISION, "violations": boundary["violations"]}
            (output / "failure.json").write_bytes(canonical(failure) + b"\n")
            print(json.dumps(failure), file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
