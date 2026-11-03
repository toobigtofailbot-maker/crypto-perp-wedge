"""CPW enum mapping and unconditional refusal at the injected dispatch boundary."""
import copy
import subprocess
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.execution import nautilus_recovery_hold_guard as g
from src.execution.interfaces import OMSState, ReconcileActionType
from tools.nautilus_adapter import noncapital_cpw_safety_integration as integration
from tools.nautilus_adapter import noncapital_supervisor_hold as h


def verified():
    return {"status": "VERIFIED_HOLD", **copy.deepcopy(h.DENIAL), **h.ZERO,
            "hold_sha256": "a" * 64, "pid": 42,
            "inspection": "OFFLINE_ARTIFACT_ONLY_NOT_FRESH_NATIVE_RECOVERY"}


def test_default_and_all_decisions_remain_frozen():
    decision = g.HoldDecision()
    assert not decision.evidence_verified and decision.reason
    assert decision.state is OMSState.FROZEN
    assert decision.action is ReconcileActionType.FREEZE
    with pytest.raises(FrozenInstanceError):
        decision.reason = "allow"
    with pytest.raises(g.RecoveryHoldRefusal, match="NO_NEW_ORDERS / NO_RESUME"):
        g.refuse_before_send()


def test_calls_original_verifier_with_external_digest(monkeypatch):
    observed = []
    def verify(path, expected):
        observed.append((path, expected))
        return verified()
    monkeypatch.setattr(h, "verify", verify)
    result = g.inspect_hold(Path("external"), "a" * 64)
    assert observed == [(Path("external"), "a" * 64)]
    assert result.evidence_verified and result.state is OMSState.FROZEN
    assert result.reason == "VERIFIED_HOLD_RECONCILIATION_REQUIRED"
    assert integration.intercept()["underlying_calls"] == dict.fromkeys(integration.SpyClient().calls, 0)


@pytest.mark.parametrize("key,value", [("status", "BLOCKED"), ("authority", "ALLOW"),
    ("disposition", "RESUME"), ("blockers", []), ("hold_sha256", "b" * 64),
    ("execution_permit_issued", True), ("authenticated_venue_reconciled", True),
    ("cpw_production_supervisor_connected", True), ("new_orders", 1), ("new_fills", 1),
    ("native_commands", 1), ("pid", True), ("proof_only", 1), ("alien", True),
    ("inspection", "FRESH_RECONCILED")])
def test_disagreement_refuses_before_sink(monkeypatch, key, value):
    payload = verified()
    payload[key] = value
    monkeypatch.setattr(h, "verify", lambda *_: payload)
    result = g.inspect_hold(Path("external"), "a" * 64)
    assert not result.evidence_verified and result.state is OMSState.FROZEN
    assert result.reason == "RECOVERY_CONTRACT_DISAGREEMENT"
    assert integration.intercept()["refused_attempts"] == 9


@pytest.mark.parametrize("failure", [ValueError("secret-payload"), TimeoutError("secret"),
                                    OSError("secret"), KeyError("secret")])
def test_verifier_errors_are_sanitized_and_frozen(monkeypatch, failure):
    def fail(*_):
        raise failure
    monkeypatch.setattr(h, "verify", fail)
    result = g.inspect_hold(Path("external"), "a" * 64)
    assert not result.evidence_verified and result.reason == "RECOVERY_EVIDENCE_BLOCKED"
    assert "secret" not in repr(result)
    assert integration.intercept()["refused_attempts"] == 9


def test_guard_import_has_no_engine_network_or_proof_import():
    code = """
import sys
class RefuseImports:
    def find_spec(self, fullname, *args):
        if fullname.startswith(('nautilus_trader', 'tools.nautilus_adapter', 'src.runtime', 'socket')):
            raise AssertionError(fullname)
sys.meta_path.insert(0, RefuseImports())
from src.execution.nautilus_recovery_hold_guard import FrozenExchangeClient, RecoveryHoldRefusal
try:
    FrozenExchangeClient(object()).place_order(None)
except RecoveryHoldRefusal:
    pass
else:
    raise AssertionError('unguarded send')
"""
    result = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True,
                            text=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr


def test_missing_receipts_do_not_change_original(tmp_path):
    result = g.inspect_hold(tmp_path, "0" * 64)
    assert not result.evidence_verified and result.state is OMSState.FROZEN
    assert list(tmp_path.iterdir()) == []
    assert integration.intercept()["refused_attempts"] == 9
