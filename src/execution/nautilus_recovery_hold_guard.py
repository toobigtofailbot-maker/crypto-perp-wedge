"""CPW denial-only recovery seam. No evidence can authorize an exchange effect."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

from src.execution.interfaces import (
    ExchangeClient,
    Fill,
    OMSState,
    OrderIntent,
    OrderUpdate,
    ReconcileActionType,
    ReconcileSnapshot,
)


@dataclass(frozen=True)
class HoldDecision:
    evidence_verified: bool = False
    reason: str = "RECOVERY_EVIDENCE_ABSENT"
    hold_sha256: str | None = None

    @property
    def state(self) -> OMSState:
        return OMSState.FROZEN

    @property
    def action(self) -> ReconcileActionType:
        return ReconcileActionType.FREEZE

    @property
    def authority(self) -> str:
        return "RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY"


class RecoveryHoldRefusal(RuntimeError):
    """Typed refusal, with no raw input or exchange payload in the reason."""

    def __init__(self) -> None:
        super().__init__("RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME")


def inspect_hold(path: Path, expected_sha256: str) -> HoldDecision:
    # Lazy import keeps the pure refusal seam independent of proof tooling on import.
    from tools.nautilus_adapter import noncapital_supervisor_hold as hold

    try:
        if ".." in Path(path).parts:
            return HoldDecision(reason="RECOVERY_EVIDENCE_BLOCKED")
        result = hold.verify(path, expected_sha256)
        expected = {"status": "VERIFIED_HOLD", **hold.DENIAL,
                    "hold_sha256": expected_sha256, **hold.ZERO,
                    "inspection": "OFFLINE_ARTIFACT_ONLY_NOT_FRESH_NATIVE_RECOVERY"}
        if set(result) != set(expected) | {"pid"} or any(
            hold.p.encoded(result[k]) != hold.p.encoded(v) for k, v in expected.items()
        ) or type(result["pid"]) is not int or result["pid"] <= 0:
            return HoldDecision(reason="RECOVERY_CONTRACT_DISAGREEMENT")
    except Exception:  # noqa: BLE001 - Untrusted proof and verification errors never unblock.
        return HoldDecision(reason="RECOVERY_EVIDENCE_BLOCKED")
    return HoldDecision(True, "VERIFIED_HOLD_RECONCILIATION_REQUIRED", expected_sha256)


def refuse_before_send() -> NoReturn:
    raise RecoveryHoldRefusal()


class FrozenExchangeClient:
    """Injected ExchangeClient seam; every operation refuses before transport.

    The isolated harness is its first consumer. No production supervisor is wired.
    """

    def __init__(self, underlying: ExchangeClient) -> None:
        self._underlying = underlying

    def place_order(self, intent: OrderIntent) -> OrderUpdate:
        refuse_before_send()

    def cancel_order(self, symbol: str, order_ref: str) -> OrderUpdate:
        refuse_before_send()

    def get_open_orders(self, symbol: str) -> list[OrderUpdate]:
        refuse_before_send()

    def get_position(self, symbol: str) -> ReconcileSnapshot:
        refuse_before_send()

    def get_fills(self, symbol: str, since_cursor: str | None = None) -> list[Fill]:
        refuse_before_send()

    def flatten(self, symbol: str) -> NoReturn:
        refuse_before_send()
