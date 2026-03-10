"""Execution contracts derived from docs/architecture (D1-D5).

References:
- docs/architecture/oms_state_machine.md
- docs/architecture/reconciliation_loop.md
- docs/architecture/safe_mode_flatten.md
- docs/architecture/execution_policy.md
- docs/architecture/event_log_schema.md

Redaction rule: EventRecord.payload must not include secrets, headers,
or raw signed payloads.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Protocol


class OMSState(Enum):
    """OMS states from docs/architecture/oms_state_machine.md."""

    INIT = "INIT"
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    SUBMITTING = "SUBMITTING"
    WORKING = "WORKING"
    RECONCILING = "RECONCILING"
    SAFE_FLATTENING = "SAFE_FLATTENING"
    FROZEN = "FROZEN"
    ERROR_TERMINAL = "ERROR_TERMINAL"


class OMSEventType(Enum):
    """OMS events from docs/architecture/oms_state_machine.md."""

    E1_START = "E1_START"
    E2_DESIRED_UPDATE = "E2_DESIRED_UPDATE"
    E3_TIMER_TICK = "E3_TIMER_TICK"
    E4_MARKET_DATA = "E4_MARKET_DATA"
    E5_ORDER_ACK = "E5_ORDER_ACK"
    E6_ORDER_REJECT = "E6_ORDER_REJECT"
    E7_CANCEL_ACK = "E7_CANCEL_ACK"
    E8_CANCEL_REJECT = "E8_CANCEL_REJECT"
    E9_FILL = "E9_FILL"
    E10_RECONCILE_DONE_OK = "E10_RECONCILE_DONE_OK"
    E11_RECONCILE_DONE_FAIL = "E11_RECONCILE_DONE_FAIL"
    E12_SAFE_MODE_TRIGGER = "E12_SAFE_MODE_TRIGGER"
    E13_SAFE_MODE_CLEARED = "E13_SAFE_MODE_CLEARED"
    E14_RESET = "E14_RESET"
    E15_SHUTDOWN = "E15_SHUTDOWN"


class ReconcileDiffType(Enum):
    """Reconcile diff types from docs/architecture/reconciliation_loop.md."""

    DesiredDiff = "DesiredDiff"
    ExchangeUnknownOrder = "ExchangeUnknownOrder"
    InternalUnknownOrderStatus = "InternalUnknownOrderStatus"
    OrderMismatch = "OrderMismatch"
    PositionDrift = "PositionDrift"
    FillGap = "FillGap"
    FiltersChanged = "FiltersChanged"
    CancelFailure = "CancelFailure"
    RateLimitOrTransportFailure = "RateLimitOrTransportFailure"


class ReconcileActionType(Enum):
    """Reconcile actions from docs/architecture/reconciliation_loop.md."""

    CANCEL = "CANCEL"
    FLATTEN = "FLATTEN"
    PLACE = "PLACE"
    VERIFY = "VERIFY"
    PERSIST = "PERSIST"
    EMIT = "EMIT"
    FREEZE = "FREEZE"
    NOOP = "NOOP"
    RECONCILE = "RECONCILE"


class OrderSide(Enum):
    """Order side from docs/architecture/execution_policy.md."""

    BUY = "BUY"
    SELL = "SELL"


class PositionSide(Enum):
    """Position side from docs/architecture/safe_mode_flatten.md."""

    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(Enum):
    """Order type from docs/architecture/execution_policy.md."""

    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderStatus(Enum):
    """Order status from docs/architecture/reconciliation_loop.md."""

    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class Severity(Enum):
    """Event severity from docs/architecture/event_log_schema.md."""

    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class EventType(Enum):
    """Event types from docs/architecture/event_log_schema.md."""

    STATE_TRANSITION = "STATE_TRANSITION"
    DECISION_MADE = "DECISION_MADE"
    ORDER_INTENT_CREATED = "ORDER_INTENT_CREATED"
    ORDER_SENT = "ORDER_SENT"
    ORDER_ACK = "ORDER_ACK"
    ORDER_REJECT = "ORDER_REJECT"
    CANCEL_SENT = "CANCEL_SENT"
    CANCEL_ACK = "CANCEL_ACK"
    CANCEL_REJECT = "CANCEL_REJECT"
    FILL_RECEIVED = "FILL_RECEIVED"
    POSITION_SNAPSHOT = "POSITION_SNAPSHOT"
    RECONCILE_START = "RECONCILE_START"
    RECONCILE_DIFF = "RECONCILE_DIFF"
    RECONCILE_ACTION = "RECONCILE_ACTION"
    RECONCILE_DONE = "RECONCILE_DONE"
    SAFE_MODE_TRIGGERED = "SAFE_MODE_TRIGGERED"
    SAFE_MODE_STEP = "SAFE_MODE_STEP"
    SAFE_MODE_DONE = "SAFE_MODE_DONE"
    ERROR = "ERROR"
    HEARTBEAT = "HEARTBEAT"


@dataclass(frozen=True)
class DesiredPosition:
    """Desired target from docs/architecture/execution_policy.md."""

    symbol: str
    target_qty: Optional[Decimal]
    target_notional: Optional[Decimal]
    timestamp_utc: str
    source_timeframe: Optional[str]
    decision_id: str
    correlation_id: str
    run_id: str


@dataclass(frozen=True)
class OrderIntent:
    """Order intent from docs/architecture/execution_policy.md."""

    symbol: str
    side: OrderSide
    qty: Decimal
    price: Optional[Decimal]
    order_type: OrderType
    reduce_only: bool
    client_order_id: str
    tif: Optional[str]
    urgency: Optional[str]
    correlation_id: str
    decision_id: str


@dataclass(frozen=True)
class OrderUpdate:
    """Order update from docs/architecture/reconciliation_loop.md."""

    client_order_id: str
    exchange_order_id: Optional[str]
    status: OrderStatus
    filled_qty: Decimal
    avg_price: Optional[Decimal]
    update_ts_utc: str
    raw_status: Optional[str]


@dataclass(frozen=True)
class Fill:
    """Fill event from docs/architecture/reconciliation_loop.md."""

    client_order_id: str
    exchange_order_id: Optional[str]
    fill_qty: Decimal
    fill_price: Decimal
    fee: Optional[Decimal]
    ts_utc: str


@dataclass(frozen=True)
class ReconcileSnapshot:
    """Reconcile snapshot from docs/architecture/reconciliation_loop.md."""

    symbol: str
    position_amt: Decimal
    open_orders_count: int
    open_orders_ids: list[str]
    ts_utc: str
    source: str


@dataclass(frozen=True)
class ReconcileDiff:
    """Reconcile diff from docs/architecture/reconciliation_loop.md."""

    diff_type: ReconcileDiffType
    details_sanitized: dict[str, Any]


@dataclass(frozen=True)
class ReconcileAction:
    """Reconcile action from docs/architecture/reconciliation_loop.md."""

    action_type: ReconcileActionType
    target_ref: Optional[str]
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ReconcileResult:
    """Reconcile result from docs/architecture/reconciliation_loop.md."""

    ok: bool
    diffs: list[ReconcileDiff]
    actions: list[ReconcileAction]
    safe_mode_triggered: bool
    error_summary: Optional[str]
    next_state: OMSState
    notes: Optional[str]


@dataclass(frozen=True)
class ExecutionDecision:
    """Execution decision from docs/architecture/execution_policy.md."""

    chosen_order_intents: list[OrderIntent]
    reason: str
    emergency: bool
    policy_used: str  # "DEFAULT" or "EMERGENCY"
    decision_id: str
    correlation_id: str
    run_id: str
    ts_utc: str


@dataclass(frozen=True)
class EventRecord:
    """Event record from docs/architecture/event_log_schema.md."""

    event_type: EventType
    ts_utc: str
    correlation_id: str
    run_id: str
    decision_id: str
    symbol: Optional[str]
    severity: Severity
    payload: dict[str, Any]


class ExchangeClient(Protocol):
    """Exchange contract from docs/architecture/reconciliation_loop.md."""

    def get_open_orders(self, symbol: str) -> list[OrderUpdate]: ...

    def place_order(self, intent: OrderIntent) -> OrderUpdate: ...

    def cancel_order(self, symbol: str, order_ref: str) -> OrderUpdate: ...

    def get_position(self, symbol: str) -> ReconcileSnapshot: ...

    def get_fills(self, symbol: str, since_cursor: Optional[str] = None) -> list[Fill]: ...


class OMSStore(Protocol):
    """Store contract from docs/architecture/oms_state_machine.md."""

    def load_snapshot(self, symbol: str) -> Optional[ReconcileSnapshot]: ...

    def persist_event(self, event: EventRecord) -> None: ...

    def persist_order_updates(self, updates: list[OrderUpdate]) -> None: ...

    def persist_fills(self, fills: list[Fill]) -> None: ...


class Reconciler(Protocol):
    """Reconciler contract from docs/architecture/reconciliation_loop.md."""

    def reconcile(self, symbol: str, desired: DesiredPosition) -> ReconcileResult: ...
