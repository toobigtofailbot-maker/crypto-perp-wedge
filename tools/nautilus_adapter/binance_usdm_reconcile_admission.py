"""N3-05 proof-only fail-closed admission for native Binance USD-M mass status into a disposable LiveExecutionEngine.

Extends the merged N3-03/N3-04 harnesses (imported, unchanged). Before any
``ExecEngine.reconcile_execution_mass_status`` send, a report must be complete
for the instrument (required queries actually issued, including ``userTrades``),
monotone over the proof-local applied state, and economically explained by
venue-confirmed fills so the engine has nothing to infer or synthesise.
Refusal never repairs or merges. Post-application detectors only label a
disposable run for discard; they are not rollback. Warm caches are in-memory
only. Every decision stays fixed; nothing here can adopt, cancel, trade or resume.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import sys
from contextlib import contextmanager, nullcontext
from decimal import Decimal
from pathlib import Path

from tools.nautilus_adapter import binance_usdm_engine_reconcile as n3_04
from tools.nautilus_adapter.binance_usdm_offline_reports import canonical, digest, require

n3_03 = n3_04.n3_03
n3_01 = n3_03.n3_01
DECISION = n3_03.DECISION
ENDPOINT_CALL = "nautilus_trader.live.execution_engine.LiveExecutionEngine.reconcile_execution_mass_status"
# Native mass status must have issued each of these (HTTP 200) once per produced report.
REQUIRED_QUERIES = ("positionRisk", "openOrders", "allOrders", "userTrades")
STANDING_UNKNOWNS = {"FUNDING_LIQUIDATION_MULTI_CYCLE_ACCOUNTING_NOT_PROVED",
                     "HISTORY_BEYOND_NATIVE_1000_ROW_NO_PAGINATION_NOT_RECOVERED"}
# Config that would let the engine drop or skip venue truth the predicates rely on.
REQUIRED_CONFIG = {"filter_unclaimed_external_orders": False, "filter_position_reports": False}
TERMINAL = {"FILLED", "CANCELED", "EXPIRED", "REJECTED"}
RANK = {"SUBMITTED": 0, "ACCEPTED": 1, "TRIGGERED": 1, "PENDING_UPDATE": 1, "PENDING_CANCEL": 1, "PARTIALLY_FILLED": 2}
TRIPWIRES = {"ENGINE_FILL_NOT_VENUE_CONFIRMED", "ENGINE_SYNTHETIC_RECONCILIATION_ORDER", "ENGINE_NO_LIQUIDITY_SIDE_FILL"}
DISCARD = "ENGINE_STATE_UNTRUSTED_DISCARD"
PROOF_STRATEGY = "N3PROOF-005"
SIGN = {"BUY": 1, "SELL": -1, "LONG": 1, "SHORT": -1, "FLAT": 0}


def completeness(witness, receipt, log):
    """N3-04 admission plus: every required query issued by each report's own requests, no non-standing unknown."""
    reasons = n3_04.admit(witness)["refusal_reasons"]
    extra = sorted(set(witness["unknowns"]) - STANDING_UNKNOWNS)
    # Each reconnect report's requests start at the native transport interruption that triggered it.
    cuts = [w["after_request"] for w in receipt["websocket"] if w["event"] == "transport_interrupted_and_reconnected"]
    bounds = [0, *cuts, len(log)]
    require(not receipt["routes"] or len(bounds) == len(receipt["routes"]) + 1, "route/request segmentation mismatch")
    for index, route in enumerate(receipt["routes"]):
        segment = log[bounds[index]:bounds[index + 1]]
        for query in REQUIRED_QUERIES:
            if not any(e["path"].endswith("/" + query) and e.get("outcome") == "200" for e in segment):
                extra.append(f"REQUIRED_QUERY_NOT_OBSERVED:{query}:{route['route']}")
    if extra and "INCOMPLETE_OR_UNKNOWN" not in reasons:
        reasons.insert(0, "INCOMPLETE_OR_UNKNOWN")
    reasons += extra
    return {"admitted": not reasons, "refusal_reasons": reasons,
            "label": "REFUSED_BEFORE_APPLICATION" if reasons else "ADMITTED_FOR_OBSERVATION_ONLY"}


def _fill_key(voi, side, qty, px, commission, liquidity):
    return voi, side, Decimal(qty), Decimal(px), commission, liquidity


def view(mass):
    """Economic identity of one native report, taken before the engine (which mutates reports) sees it."""
    stable = n3_03._mass(mass)
    fills = [(f["trade_id"], _fill_key(f["venue_order_id"], f["order_side"], f["last_qty"], f["last_px"], f["commission"],
                                       f["liquidity_side"])) for f in stable["fills"]]
    return {"digest": digest({k: stable[k] for k in ("orders", "fills", "positions")}), "watermark": n3_04._watermark(mass),
            "fills": fills, "orders": {o["venue_order_id"]: (o["order_status"], Decimal(o["filled_qty"])) for o in stable["orders"]},
            "position": sum(SIGN[p["position_side"]] * Decimal(p["quantity"]) for p in stable["positions"])}


def monotone(memory, report):
    """Refusal reasons against proof-local applied state; None means an exact replay (no-op)."""
    if memory is None:
        return []
    if report["digest"] == memory["digest"]:
        return None
    reasons = set()
    if report["watermark"] < memory["watermark"]:
        reasons.add("REPORT_OLDER_THAN_APPLIED_STATE")
    elif report["watermark"] == memory["watermark"]:
        reasons.add("CONFLICTING_EQUAL_WATERMARK")
    fills = dict(report["fills"])
    regressed = any(fills.get(tid) != econ for tid, econ in memory["fills"].items())
    for voi, (status, filled) in memory["orders"].items():
        now = report["orders"].get(voi)
        if now is None or now[1] < filled or (status in TERMINAL and now[0] != status) or (
                now[0] not in TERMINAL and RANK.get(now[0], -1) < RANK.get(status, -1)):
            regressed = True
    if regressed:
        reasons.add("REPORT_NOT_MONOTONE_OVER_APPLIED_STATE")
    return sorted(reasons)


def _cached_fills(cache, instrument_id):
    from nautilus_trader.model.events import OrderFilled
    fills = {}
    for order in cache.orders(instrument_id=instrument_id):
        for e in order.events:
            if isinstance(e, OrderFilled):
                f = OrderFilled.to_dict(e)
                fills[f["trade_id"]] = _fill_key(f["venue_order_id"], f["order_side"], f["last_qty"], f["last_px"],
                                                 f["commission"], f["liquidity_side"])
    return fills


def coherence(state, report):
    """Every engine-visible quantity must be explained by venue-confirmed fills, or the engine would infer/synthesise."""
    cache, reasons = state["cache"], set()
    applied = _cached_fills(cache, state["instrument_id"])
    union = dict(applied)
    seen = set()
    for tid, econ in report["fills"]:
        if tid in seen:
            reasons.add("DUPLICATE_TRADE_ID_IN_REPORT")
        seen.add(tid)
        if tid in union and union[tid] != econ:
            reasons.add("TRADE_ECONOMICS_CONFLICT_WITH_APPLIED")
        union.setdefault(tid, econ)
    for voi, (_, filled) in report["orders"].items():
        if sum(econ[2] for econ in union.values() if econ[0] == voi) != filled:
            reasons.add("FILL_UNION_QTY_MISMATCH")
    if any(econ[0] not in report["orders"] for _, econ in report["fills"]):
        reasons.add("FILL_WITHOUT_ORDER_REPORT")
    if any(o.venue_order_id is not None and o.venue_order_id.value not in report["orders"]
           for o in cache.orders(instrument_id=state["instrument_id"])):
        reasons.add("CACHED_ORDER_ABSENT_FROM_REPORT")
    if sum(SIGN[econ[1]] * econ[2] for econ in union.values()) != report["position"]:
        reasons.add("POSITION_NOT_EXPLAINED_BY_VENUE_FILLS")
    if any(state["config"][k] != v for k, v in REQUIRED_CONFIG.items()):
        reasons.add("ENGINE_CONFIG_DROPS_VENUE_TRUTH")
    return sorted(reasons)


def detect(state, venue_trades):
    """Post-application observation in disposable state only. A trip discards the run; it repairs nothing."""
    after = n3_04.snapshot(state)
    labels = set(n3_04._observations({"after": after}, venue_trades))
    if any(f["liquidity_side"] == "NO_LIQUIDITY_SIDE" for f in after["fills"]):
        labels.add("ENGINE_NO_LIQUIDITY_SIDE_FILL")
    return sorted(labels), bool(labels & TRIPWIRES)


def gated(state, admission, masses, calls):
    """The only send path: every predicate passes before ``msgbus.send``; anything else is refused unsent."""
    records = []
    for route, mass in masses:
        before, sent = n3_04.snapshot(state), calls.get(ENDPOINT_CALL, 0)
        record = {"route": route, "engine_application_attempted": False, "decision": DECISION}
        if state.get("discarded"):
            reasons = [DISCARD]
        elif not admission["admitted"] or mass is None:
            reasons = admission["refusal_reasons"] or ["MASS_STATUS_UNAVAILABLE"]
        else:
            report = view(mass)
            reasons = monotone(state.get("memory"), report)
            reasons = None if reasons is None else reasons + coherence(state, report)
        if reasons is None:
            record["outcome"] = "IDENTICAL_REPLAY_NO_OP"
        elif reasons:
            record.update(outcome="REFUSED_BEFORE_APPLICATION", refusal_reasons=reasons)
        else:
            record = {**n3_04.apply(state, route, mass, calls), "decision": DECISION}
            confirmed = state.setdefault("venue_trades", set())
            confirmed.update(tid for tid, _ in report["fills"])
            record["engine_observations"], tripped = detect(state, confirmed)
            if tripped:
                state["discarded"] = True
                record["outcome"] = DISCARD
            else:
                record["outcome"] = "APPLIED_FOR_OBSERVATION_ONLY"
                state["memory"] = {k: report[k] for k in ("digest", "watermark", "orders")} | {"fills": dict(report["fills"])}
            records.append(record)
            continue
        record["endpoint_calls_delta"] = calls.get(ENDPOINT_CALL, 0) - sent
        record["state_unchanged"] = n3_04.snapshot(state) == before
        require(record["endpoint_calls_delta"] == 0 and record["state_unchanged"], "refused report reached the engine: " + route)
        records.append(record)
    return records


def seed(state, held, mass):
    """Warm in-memory cache: held-receipt identities under a proof strategy; economics from matching venue rows only."""
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.model.enums import OmsType, OrderType
    from nautilus_trader.model.events import (
        OrderAccepted,
        OrderFilled,
        OrderSubmitted,
        PositionChanged,
        PositionOpened,
    )
    from nautilus_trader.model.identifiers import (
        ClientOrderId,
        PositionId,
        StrategyId,
        TradeId,
        VenueOrderId,
    )
    from nautilus_trader.model.orders import LimitOrder
    from nautilus_trader.model.position import Position

    cache, msgbus, iid = state["cache"], state["msgbus"], state["instrument_id"]
    account_id, strategy = cache.account_for_venue(iid.venue).id, StrategyId(PROOF_STRATEGY)
    position_id, instrument = PositionId(f"{iid}-{strategy}"), cache.instrument(iid)  # native NETTING id scheme
    fills = {f.trade_id.value: f for rows in mass.fill_reports.values() for f in rows}
    seeded = []
    # The live engine's event endpoint only enqueues (it is never started here), so events go
    # straight through the public model API: order state machine, Position, Cache, Portfolio.
    for voi, info in sorted(held["orders"].items()):
        report = mass.order_reports.get(VenueOrderId(voi))
        require(report is not None and report.client_order_id == ClientOrderId(info["client_order_id"]), "held order not in venue rows")
        require(report.order_type == OrderType.LIMIT, "warm seeding supports held LIMIT orders only: " + voi)
        cid = report.client_order_id
        order = LimitOrder(msgbus.trader_id, strategy, iid, cid, report.order_side, report.quantity, report.price, UUID4(),
                           report.ts_accepted, time_in_force=report.time_in_force, reduce_only=report.reduce_only)
        cache.add_order(order)
        common = (msgbus.trader_id, strategy, iid, cid)
        order.apply(OrderSubmitted(*common, account_id, UUID4(), report.ts_accepted, report.ts_accepted))
        order.apply(OrderAccepted(*common, report.venue_order_id, account_id, UUID4(), report.ts_accepted, report.ts_accepted))
        cache.update_order(order)
        for tid, trade in sorted(held["trades"].items()):
            fill = fills.get(tid)
            if fill is None or fill.venue_order_id != report.venue_order_id:
                continue
            require((fill.last_qty.as_decimal(), fill.last_px.as_decimal(), fill.commission.as_decimal()) == (
                Decimal(trade["qty"]), Decimal(trade["price"]), Decimal(trade["commission"])), "held trade economics differ")
            event = OrderFilled(*common, report.venue_order_id, account_id, TradeId(tid), position_id, report.order_side,
                                report.order_type, fill.last_qty, fill.last_px, fill.commission.currency, fill.commission,
                                fill.liquidity_side, UUID4(), fill.ts_event, fill.ts_event)
            order.apply(event)
            cache.update_order(order)
            position = cache.position(position_id)
            if position is None:
                position = Position(instrument, event)
                cache.add_position(position, OmsType.NETTING)
                state["portfolio"].update_position(PositionOpened.create(position, event, UUID4(), event.ts_event))
            else:
                position.apply(event)
                cache.update_position(position)
                state["portfolio"].update_position(PositionChanged.create(position, event, UUID4(), event.ts_event))
        require(order.status_string() == info["status"], "seeded order status differs from held receipt: " + voi)
        seeded.append(voi)
    # Trade IDs CPW already held and the venue confirmed: the detectors' confirmed set starts here.
    state["venue_trades"] = {tid for tid in held["trades"] if tid in fills}
    return seeded


def identities(state, held):
    """Native ownership observations only; a held-receipt match is never adoption or permission."""
    result = {}
    for order in state["cache"].orders(instrument_id=state["instrument_id"]):
        voi = order.venue_order_id.value
        info = held["orders"].get(voi)
        result[voi] = {"client_order_id": order.client_order_id.value, "strategy_id": order.strategy_id.value, "tags": order.tags,
                       "status": order.status_string(),
                       "held_receipt_identity_match": info is not None and info["client_order_id"] == order.client_order_id.value
                       and order.strategy_id.value == PROOF_STRATEGY, "classification": "OBSERVATION_ONLY_NOT_ADOPTABLE"}
    return dict(sorted(result.items()))


@contextmanager
def warm_native_cache(cache):
    """Hand the native client a pre-seeded real Cache (same idiom as N3-03's WebSocket transport injection)."""
    import nautilus_trader.cache.cache as module
    original = module.Cache
    module.Cache = lambda *args, **kwargs: cache
    try:
        yield
    finally:
        module.Cache = original


def _scenario(loop, fixture, tape, name, calls, cache=None):
    native = {}
    with warm_native_cache(cache) if cache is not None else nullcontext():
        receipt, log = loop.run_until_complete(n3_03._native_run(fixture, tape, name, native=native))
    loop.run_until_complete(asyncio.sleep(0))  # let cancelled native tasks finish
    witness = n3_03.witness(fixture, name, receipt, log)
    return {"receipt": receipt, "log": log, "witness": witness, "native": native,
            "admission": completeness(witness, receipt, log),
            "user_trades_queried": any(e["path"].endswith("/userTrades") for e in log)}


def _derive(mass, change):
    """An in-memory variant of a real native report (public to_dict/from_dict); used only as refused adversarial input."""
    from nautilus_trader.execution.reports import ExecutionMassStatus
    data = mass.to_dict()
    change(data)
    return ExecutionMassStatus.from_dict(data)


def _fill_rows(data):
    return [f for rows in data["fill_reports"].values() for f in rows]


def run_all(loop):
    require(sys.version_info[:3] == (3, 12, 10), "requires isolated CPython 3.12.10")
    for package, version in (("nautilus-trader", "1.231.0"), ("pyarrow", "25.0.1")):
        require(importlib.metadata.version(package) == version, "native pin mismatch")
    import nautilus_trader.live.execution_engine as engine_module
    require(hashlib.sha256(Path(engine_module.__file__).read_bytes()).hexdigest() == n3_04.ENGINE_SOURCE_SHA256,
            "installed LiveExecutionEngine source differs from the pinned wheel")
    boundary = n3_03._STATE
    require(boundary is not None and boundary["allow"] is engine_module.LiveExecutionEngine,
            "run only inside the N3-03 boundary with the exact LiveExecutionEngine opt-in")
    calls = boundary["calls"]
    fixture, tape = n3_03.load_fixture(), n3_01.load_fixture(n3_01.FIXTURE)
    scenarios, states, refused = {}, {}, {}
    for name in n3_03.SCENARIOS:
        observed = _scenario(loop, fixture, tape, name, calls)
        if not observed["admission"]["admitted"]:
            refused[name] = observed
        result = scenarios[name] = {"witness_anomalies": observed["witness"]["anomalies"],
                                    "state_completeness": observed["witness"]["state_completeness"],
                                    "user_trades_queried": observed["user_trades_queried"], "admission": observed["admission"],
                                    "decision": DECISION}
        if observed["receipt"]["startup"]["status"] != "OK":
            result["applications"] = []
            continue
        state = states[name] = n3_04._engine(loop, observed["native"], {})
        result["applications"] = gated(state, observed["admission"], observed["native"]["mass"], calls)
        result["after"] = n3_04.snapshot(state)
        # Replay: a freshly generated native report of the same venue state.
        again = _scenario(loop, fixture, tape, name, calls)
        result["replay"] = gated(state, again["admission"], again["native"]["mass"], calls)
        result["replay_state_unchanged"] = n3_04.snapshot(state) == result["after"]
    # Refused reports are also offered to the populated ordinary state: gated() itself fails if any reaches the engine.
    for name, observed in refused.items():
        records = gated(states["active"], observed["admission"], observed["native"].get("mass", []), calls)
        scenarios[name]["gated_against_active"] = [[r["outcome"], r["endpoint_calls_delta"], r["state_unchanged"]] for r in records]
    adversarial = _adversarial(loop, fixture, tape, calls, states["reconnect_gap"])
    warm = _warm(loop, fixture, tape, calls)
    probes = _probes(loop, fixture, tape, calls)
    ids = {}
    semantic = n3_04._normalize({"scenarios": scenarios, "adversarial": adversarial, "warm": warm,
                                 "hazard_controls": probes}, ids)
    return semantic, {token: raw for raw, token in ids.items()}


def _adversarial(loop, fixture, tape, calls, state):
    """Variants of the applied reconnect report offered to the populated reconnect_gap engine: all refused unsent."""
    current = dict(_scenario(loop, fixture, tape, "reconnect_gap", calls)["native"]["mass"])
    admitted = {"admitted": True, "refusal_reasons": [], "label": "ADMITTED_FOR_OBSERVATION_ONLY"}

    def commission(data):
        _fill_rows(data)[0]["commission"] = "0.05000000 USDT"

    def drop_trade(data):
        rows = data["fill_reports"]["101"]
        rows[:] = [f for f in rows if f["trade_id"] != "501"]

    def qty_regression(data):
        data["order_reports"]["101"]["filled_qty"] = "0.006"

    def status_regression(data):
        from nautilus_trader.model.enums import OrderStatus
        data["order_reports"]["101"]["order_status"] = OrderStatus.PARTIALLY_FILLED.value  # was FILLED

    variants = {"stale_redelivery": current["startup"]}
    for label, change in (("equal_watermark_commission", commission), ("lost_applied_trade", drop_trade),
                          ("filled_qty_regression", qty_regression), ("status_regression", status_regression)):
        variants[label] = _derive(current["reconnect/1"], change)
    return {label: gated(state, admitted, [(label, mass)], calls)[0] for label, mass in variants.items()}


def _warm(loop, fixture, tape, calls):
    """Warm in-memory caches seeded from held receipts: identity observation and warm-flat completeness."""
    external = _scenario(loop, fixture, tape, "external_order", calls)
    held = fixture["scenarios"]["external_order"]["held"]
    state = n3_04._engine(loop, external["native"], {})
    seeded = seed(state, held, external["native"]["mass"][0][1])
    before = n3_04.snapshot(state)
    applications = gated(state, external["admission"], external["native"]["mass"], calls)
    identity = {"seeded": seeded, "before": before, "applications": applications, "after": n3_04.snapshot(state),
                "identities": identities(state, held), "witness_anomalies": external["witness"]["anomalies"]}
    active = _scenario(loop, fixture, tape, "active", calls)
    warm_state = n3_04._engine(loop, active["native"], {})
    seed(warm_state, fixture["scenarios"]["active"]["held"], active["native"]["mass"][0][1])
    flat = _scenario(loop, fixture, tape, "clean_flat", calls, cache=warm_state["cache"])
    flat_record = {"user_trades_queried": flat["user_trades_queried"], "admission": flat["admission"],
                   "applications": gated(warm_state, flat["admission"], flat["native"]["mass"], calls)}
    return {"identity": identity, "warm_flat": flat_record}


def _probes(loop, fixture, tape, calls):
    """Deliberately ungated negative controls in independent disposable state: detectors must trip."""
    controls = {}
    for name, scenario, overrides in (
            ("missing_fill", "missing_fill", {}),
            ("missing_fill_generate_missing_orders_off", "missing_fill", {"generate_missing_orders": False}),
            ("external_order_filtered", "external_order", {"filter_unclaimed_external_orders": True})):
        observed = _scenario(loop, fixture, tape, scenario, calls)
        state = n3_04._engine(loop, observed["native"], overrides)
        for route, mass in observed["native"]["mass"]:
            n3_04.apply(state, route, mass, calls)
        venue = {f["trade_id"] for r in observed["receipt"]["routes"] if r["mass_status"] for f in r["mass_status"]["fills"]}
        labels, tripped = detect(state, venue)
        # Same scenario/config through the gate, on a fresh native report (the engine mutates reports it reconciles).
        fresh = _scenario(loop, fixture, tape, scenario, calls)
        refused = gated(n3_04._engine(loop, fresh["native"], overrides), fresh["admission"], fresh["native"]["mass"], calls)
        controls[name] = {"label": n3_04.PROBE_LABEL, "config": state["config"], "after": n3_04.snapshot(state),
                          "engine_observations": labels, "outcome": DISCARD if tripped else "NO_TRIP",
                          "gated_equivalent": refused, "decision": DECISION}
    return controls


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
            semantic = {"fixture_id": n3_03.FIXTURE_ID, "input_sha256": n3_03.FIXTURE_SHA256, "native_pin": "1.231.0",
                        "engine": n3_04.engine_identity(), "decision": DECISION, **semantic}
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
                        "n3_04_module_sha256": hashlib.sha256(Path(n3_04.__file__).read_bytes()).hexdigest(),
                        "n3_03_module_sha256": hashlib.sha256(Path(n3_03.__file__).read_bytes()).hexdigest(),
                        "decision": DECISION, "verdict": "N3_05_FAIL_CLOSED_ADMISSION_OBSERVED"}
            manifest["self_sha256"] = digest(manifest)
            (output / "manifest.json").write_bytes(canonical(manifest) + b"\n")
            print(json.dumps({"verdict": manifest["verdict"], "semantic_sha256": manifest["semantic_sha256"], "seccomp": seccomp}))
            return 0
        except Exception as exc:
            failure = {"verdict": "N3_05_BLOCKED", "error_type": type(exc).__name__, "error": str(exc),
                       "input_sha256": n3_03.FIXTURE_SHA256, "native_pin": "1.231.0",
                       "pinned_engine_source_sha256": n3_04.ENGINE_SOURCE_SHA256, "installed_engine_source_sha256":
                           hashlib.sha256(Path(sys.modules[LiveExecutionEngine.__module__].__file__).read_bytes()).hexdigest(),
                       "decision": DECISION,
                       "violations": boundary["violations"]}
            (output / "failure.json").write_bytes(canonical(failure) + b"\n")
            print(json.dumps(failure), file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
