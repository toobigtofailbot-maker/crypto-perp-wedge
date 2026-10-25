"""Offline N2-06 funding/liquidation verdict controls; physical Rust/Redis proof is separately mandatory."""
import copy
import hashlib
import importlib.util
import json
import re
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tools/nautilus_adapter/v2_history_route"
SPEC = importlib.util.spec_from_file_location("n2_06_controller", FIXTURE / "run_proof.py")
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)

B = proof.BOUNDARY_NS


def view(side="LONG", quantity="1.000", closed=False, cash=None, commission="0.04", settlements=None,
         run_error=None, fills=None):
    adjustments = [] if cash is None else [{"adjustment_type": "FUNDING", "pnl_change": f"{cash} USDT", "ts_event": B}]
    equity = 10000 - float(commission) + (float(cash) if cash else 0)
    return {"run_error": run_error, "settlements": settlements or [],
            "accounts": [{"equity": f"{equity:.8f}", "balances": [], "initial_margins": [],
                          "maintenance_margins": [["BTCUSDT-PERP.SIM", "5.00000000"]]}],
            "positions": [{"closed": closed, "pnl": None, "side": side, "quantity": quantity,
                           "commissions": {"USDT": f"{commission} USDT"}, "adjustments": adjustments}],
            "orders": [], "fills": fills or [], "pnl": ["0", "0", "0"]}


def settled(rate):
    return [{"instrument_id": "BTCUSDT-PERP.SIM", "rate": rate, "settlement_price": "100.00",
             "currency": "USDT", "ts_event": B}]


# Native observations from the frozen-binary producers: long pays positive, short pays negative.
@pytest.mark.parametrize("scenario,side,rate,cash", [
    ("funding_long_pos", "LONG", "0.01", "-1.00000000"), ("funding_long_neg", "LONG", "-0.01", "1.00000000"),
    ("funding_short_pos", "SHORT", "0.01", "1.00000000"), ("funding_short_neg", "SHORT", "-0.01", "-1.00000000")])
def test_native_settlement_matching_cpw_sign_and_basis_is_proven(scenario, side, rate, cash):
    row = proof.funding_verdict(scenario, view(side, cash=cash, settlements=settled(rate)))
    assert row["verdict"] == "PROVEN"
    assert Decimal(row["cpw_reference_cash"]) == Decimal(row["native_cash"]) == Decimal(cash)


@pytest.mark.parametrize("scenario", ["funding_flat_pos", "funding_flat_neg", "funding_missing", "funding_no_boundary"])
def test_flat_missing_or_boundaryless_rate_has_no_cash_effect(scenario):
    flat = scenario.startswith("funding_flat")
    assert proof.funding_verdict(scenario, view("FLAT" if flat else "LONG", "0.000" if flat else "1.000",
                                                closed=flat))["verdict"] == "PROVEN"


@pytest.mark.parametrize("mutation", ["double_settlement", "double_adjustment", "wrong_amount", "wrong_sign",
                                      "wrong_boundary", "wrong_basis", "equity_drift", "flat_charged"])
def test_divergent_native_settlement_is_never_proven(mutation):
    scenario, v = "funding_long_pos", view(cash="-1.00000000", settlements=settled("0.01"))
    if mutation == "double_settlement":
        v["settlements"] *= 2
    elif mutation == "double_adjustment":
        v["positions"][0]["adjustments"] *= 2
    elif mutation == "wrong_amount":
        v = view(cash="-2.00000000", settlements=settled("0.01"))
    elif mutation == "wrong_sign":
        v = view(cash="1.00000000", settlements=settled("0.01"))
    elif mutation == "wrong_boundary":
        v["settlements"][0]["ts_event"] = B + 1
    elif mutation == "wrong_basis":
        v["settlements"][0]["settlement_price"] = "105.00"
    elif mutation == "equity_drift":
        v["accounts"][0]["equity"] = "10000.00000000"
    else:
        scenario, v = "funding_flat_pos", view("FLAT", "0.000", closed=True, cash="-1.00000000",
                                               settlements=settled("0.01"))
    assert proof.funding_verdict(scenario, v)["verdict"] == "BOUNDED_DIVERGENCE"


def test_absent_native_settlement_is_unsupported_not_parity():
    assert proof.funding_verdict("funding_long_pos", view())["verdict"] == "UNSUPPORTED_PINNED"


@pytest.mark.parametrize("scenario,error", [
    ("funding_stale", "Late funding boundary for BTCUSDT-PERP.SIM on SIM: 1 < replay timestamp 2"),
    ("funding_cross_instrument", "Funding settlement failed for ETHUSDT-PERP.SIM on SIM at 1")])
def test_stale_or_cross_instrument_rate_requires_native_fail_closed_refusal(scenario, error):
    assert proof.funding_verdict(scenario, view(run_error=error))["verdict"] == "PROVEN"
    assert proof.funding_verdict(scenario, view())["verdict"] == "UNVERIFIED"  # no native gate observed
    charged = view(run_error=error, cash="-1.00000000", settlements=settled("0.01"))
    assert proof.funding_verdict(scenario, charged)["verdict"] == "UNVERIFIED"
    assert proof.funding_verdict("funding_long_pos", view(run_error=error))["verdict"] == "UNVERIFIED"


def liquidated(equity, at=proof.FIRST_STRESS_NS):
    v = view("FLAT", "0.000", closed=True, commission="11.80", fills=[
        ("SELL", "100.000", "100.00", 1_800_000_000_000_000_000, False), ("BUY", "100.000", "195.00", at, True)])
    v["accounts"][0]["equity"] = equity
    return v


def test_native_liquidation_with_surviving_equity_is_bounded_divergence_not_parity():
    assert proof.liquidation_verdict("liquidation_on_195", liquidated("488.20000000"))["verdict"] == "BOUNDED_DIVERGENCE"
    assert proof.liquidation_verdict("liquidation_on_250", liquidated("-5014.00000000"))["verdict"] == "BOUNDED_DIVERGENCE"
    assert proof.liquidation_verdict("liquidation_on_200", liquidated("0E-8"))["verdict"] == "PROVEN"


def test_late_missing_or_failed_liquidation_is_not_classified_as_native_mechanism():
    assert proof.liquidation_verdict("liquidation_on_195", liquidated("0", at=proof.FIRST_STRESS_NS + 1))[
        "verdict"] == "UNVERIFIED"
    survived = view("SHORT", "100.000", commission="4")
    assert proof.liquidation_verdict("liquidation_on_195", survived)["verdict"] == "UNSUPPORTED_PINNED"
    assert proof.liquidation_verdict("liquidation_on_195", dict(survived, run_error="x"))["verdict"] == "UNVERIFIED"


def test_disabled_liquidation_requires_the_paired_native_liquidation():
    on = proof.liquidation_verdict("liquidation_on_195", liquidated("488.20000000"))
    survived = view("SHORT", "100.000", commission="4")
    assert proof.liquidation_verdict("liquidation_off_195", survived, on)["verdict"] == "PROVEN"
    assert proof.liquidation_verdict("liquidation_off_195", survived, None)["verdict"] == "UNVERIFIED"
    assert proof.liquidation_verdict("liquidation_off_195", liquidated("488.2"), on)["verdict"] == "UNVERIFIED"


def checkpoint():
    position = {"closed": False, "pnl": "-1.04", "native": {"side": "LONG", "quantity": "1.000",
                "commissions": {"USDT": "0.04 USDT"}, "event_id": "e-1", "trader_id": "N2Ha-001",
                "adjustments": [{"adjustment_type": "FUNDING", "pnl_change": "-1 USDT", "ts_event": B,
                                 "event_id": "u-1", "reason": "funding_settlement:u-2"}]}}
    return {"run_error": None, "funding_settlements": [dict(settled("0.01")[0], event_id="u-2")],
            "state": {"accounts": [{"equity": "9998.96", "balances": [], "id": "SIM-001"}], "positions": [position],
                      "orders": [{"id": "O-1", "status": "FILLED", "filled": "1.000"}],
                      "fills": [{"order_id": "O-1", "payload": {"order_side": "BUY", "last_qty": "1.000",
                                 "last_px": "100.00", "ts_event": 0}}],
                      "portfolio_realized_pnl": "-1.04", "portfolio_unrealized_pnl": "0",
                      "portfolio_net_exposure": "100"}}


def test_repeat_projection_ignores_volatile_identity_but_not_economics():
    a, b = checkpoint(), checkpoint()
    b["funding_settlements"][0]["event_id"] = "u-9"
    b["state"]["positions"][0]["native"].update(event_id="e-9", trader_id="N2Hb-001")
    assert proof.economics(a) == proof.economics(b)
    b["state"]["positions"][0]["native"]["adjustments"][0]["pnl_change"] = "-2 USDT"
    assert proof.economics(a) != proof.economics(b)


def funded_records(*events):
    return {"trader:positions:P": {"type": "list", "value": [json.dumps(e) for e in events]}}


def test_funded_restore_is_unsupported_only_on_native_duplicate_fill_evidence():
    cp = checkpoint()
    fill = {"type": "OrderFilled", "event_id": "f-1", "trade_id": "T-1"}
    cp["redis_contents"] = funded_records(fill, fill)  # native re-append of the last fill, no adjustment record
    assert proof.funding_not_persisted(cp)
    cp["redis_contents"] = funded_records(fill)
    assert not proof.funding_not_persisted(cp)  # nothing duplicated: a refusal would be unexplained
    cp["redis_contents"] = funded_records(fill, fill, {"type": "PositionAdjusted", "event_id": "u-1"})
    assert not proof.funding_not_persisted(cp)  # adjustment persisted: not the observed native limit
    cp["redis_contents"] = funded_records(fill, fill)
    cp["state"]["positions"][0]["native"]["adjustments"] = []
    assert not proof.funding_not_persisted(cp)  # unfunded positions must restore exactly


def resume_row(**changes):
    row = {"exit": 1, "admission": None, "native_receipt": None, "changed_keys": [], "content_changed_keys": [],
           "source_files_before": {"a": "1"}, "source_files_after": {"a": "1"}}
    row.update(changes)
    return row


def test_resume_refuses_before_admission_and_without_mutation():
    assert proof.require_refusal_without_admission(resume_row())
    for change in [{"exit": 0}, {"admission": {"decision": "RECOVERY_ADMITTED_SEALED"}}, {"native_receipt": {}},
                   {"changed_keys": ["k"]}, {"source_files_after": {"a": "2"}}]:
        with pytest.raises(AssertionError):
            proof.require_refusal_without_admission(resume_row(**change))


def refused_row(error):
    admission = {"pid": 7, "decision": "RECONCILIATION_REQUIRED", "error": error,
                 "order_authority": proof.NO_AUTHORITY, "venue_reconciliation_required_before_activation": True}
    run = {"pid": 7, "process": {"pid": 7}, "exit": 1, "admission": admission, "native_receipt": None}
    return {"changed_keys": [], "content_changed_keys": [], "source_files_before": {}, "source_files_after": {},
            "runs": [run]}


def test_failed_native_run_must_refuse_with_its_reason():
    assert proof.require_result(refused_row("NATIVE_RUN_FAILED"), reason="NATIVE_RUN_FAILED")
    with pytest.raises(AssertionError):
        proof.require_result(refused_row("STALE_WATERMARK"), reason="NATIVE_RUN_FAILED")
    admitted = copy.deepcopy(refused_row(None))
    admitted["runs"][0].update(exit=0)
    admitted["runs"][0]["admission"]["decision"] = "RECOVERY_ADMITTED_SEALED"
    with pytest.raises(AssertionError):
        proof.require_result(admitted, reason="NATIVE_RUN_FAILED")


def test_fixture_adds_inputs_only_and_no_synthetic_accounting():
    source = (FIXTURE / "src/main.rs").read_text()
    for forbidden in ("adjust_account_balance", "update_position_from_adjustment", "FundingSettlement::new",
                      "PositionAdjusted::new", "process_liquidations(", "liquidate_open_positions",
                      "process_funding_settlement", "settle_funding"):
        assert forbidden not in source, forbidden
    assert source.count("FundingRateUpdate::new(") == 1
    # The bus has one tap slot and native event-store capture owns it while producing; only restore taps.
    assert source.count("set_bus_tap(") == 1 and source.index("set_bus_tap(") > source.index("fn restore(")
    assert ".liquidation_enabled(scenario.starts_with(\"liquidation_on\"))" in source
    assert re.search(r'"round_trip", "reversal", "multi_cycle", "open",', source)
    assert 'ensure!(checkpoint["run_error"].is_null(), "NATIVE_RUN_FAILED")' in source
    assert '"resume" => anyhow::bail!("RECONCILIATION_UNVERIFIED / NO_NEW_ORDERS")' in source


def test_fixture_remains_offline_and_non_authoritative():
    text = (FIXTURE / "src/main.rs").read_text() + (FIXTURE / "run_proof.py").read_text()
    for forbidden in ("binance", "api_key", "api_secret", "socket", "urllib", "requests", "http://", "https://",
                      "secrets/", "submit_order_list", "LiveExecution"):
        assert forbidden not in text.lower(), forbidden
    assert "'external network present'" in text
    # Unchanged since N2-05 (merged #750): no crate, feature or pin change.
    for name, digest in [("Cargo.toml", "e03190233756caca529d8be8aa821b6baed1b2acb6c5ea4937167d9d0630d207"),
                         ("Cargo.lock", "b1447750316780b32fe71616906a9bf030e6f45b6cbd368063badca49ec1709d")]:
        assert hashlib.sha256((FIXTURE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == digest


def test_cpw_oracle_references_are_unchanged():
    oracle = (ROOT / "tests/test_nautilus_n1_02_parity.py").read_text()
    assert "assert cpw.funding_paid == pytest.approx(side * float(rate) * 100, rel=0, abs=1e-12)" in oracle
    assert '@pytest.mark.parametrize("rate", [".01", "-.01"])' in oracle
    assert "frame = _frame([100., 100., 195., 195., 195., 195.])" in oracle
    assert '@pytest.mark.parametrize("last_price", [200., 250.])' in oracle
    assert oracle.count("assert cpw.equity_curve.iloc[-1] == 0") == 2
    assert proof.LIQUIDATION == ["liquidation_on_195", "liquidation_off_195", "liquidation_on_200",
                                 "liquidation_off_200", "liquidation_on_250", "liquidation_off_250"]
