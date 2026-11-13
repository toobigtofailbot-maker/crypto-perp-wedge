"""Versioned M1 source and economics bindings for isolated synthetic studies."""

from typing import Annotated, Literal

import json
from pydantic import Field, model_validator

from tools.data_ingestion.ccxt_public_funding_adapter import FUNDING_INTERVAL_MS
from tools.mcp.project_evidence.research_intent import BoundedResearchIntentV1

from .envelope import content_hash
from .models import Identity, Sha, StrictModel
from .nonholdout_qualification import CADENCE, Interval

M1_VERSION = "cpw_m1_fixture_source_v1"
M1_SOURCE_CLASS = "m1_test_only"
M1_MAPPING = "research_factory_mapping_m1_fixture_v1"
M1_ROOT = "scratch/m1/TEST_ONLY/"
M1_REAL_VERSION = "cpw_m1_historical_source_v1"
M1_REAL_SOURCE_CLASS = "m1_historical"
M1_REAL_MAPPING = "research_factory_mapping_m1_historical_v1"
M1_REAL_ROOT = "scratch/m1/historical/"
M1_REAL_SPEC_REF = "cpw-m1-historical-candidate:"
Symbol = Annotated[str, Field(pattern=r"^[A-Z0-9]+USDT$", max_length=30)]
BasisPoints = Annotated[float, Field(ge=0, lt=10_000)]


class M1Intent(BoundedResearchIntentV1):
    schema_version: Literal["cpw_m1_fixture_intent_v1"]
    instrument_scope: Annotated[str, Field(pattern=r"^[A-Z0-9]+USDT_BINANCE_USDTM_PERP$")]


class M1Costs(StrictModel):
    qualification: Literal["TEST_ONLY"]
    fee_bps_taker: BasisPoints
    fee_bps_maker: BasisPoints
    slippage_bps: BasisPoints
    funding_notional: Literal["entry_price"]


class M1Source(StrictModel):
    schema_version: Literal["cpw_m1_fixture_source_v1"]
    classification: Literal["TEST_ONLY"]
    instrument: Symbol
    timeframe: Literal["15m", "1h"]
    venue: Literal["Binance USDT-M"]
    market_type: Literal["perpetual"]
    quote_and_margin_asset: Literal["USDT"]
    epoch_id: Identity
    epoch_window: Interval
    effective_window: Interval
    ohlcv_sha256: Sha
    funding_source: Literal["TEST_ONLY_SYNTHETIC_8H"]
    funding_sha256: Sha
    variant_manifest_sha256: Sha
    sweep_plan_id: Annotated[str, Field(pattern=r"^SWEEP-PLAN-[0-9]{4}$")]
    sweep_plan_sha256: Sha
    costs: M1Costs

    @model_validator(mode="after")
    def eligible_window(self):
        start, end = self.effective_window.start_ms, self.effective_window.end_ms
        if not self.epoch_window.start_ms <= start < end <= self.epoch_window.end_ms:
            raise ValueError("M1 effective window is outside contract epoch")
        if start % FUNDING_INTERVAL_MS or end % FUNDING_INTERVAL_MS:
            raise ValueError("M1 fixture requires complete 8h settlement intervals")
        if not 20 <= (end - start) // CADENCE[self.timeframe] <= 4096:
            raise ValueError("M1 fixture requires 20 to 4096 complete bars")
        return self

    @property
    def identity(self):
        return "M1-TEST-ONLY-" + content_hash(self.model_dump(mode="json")).split(":")[1]

    def require_partition(self, split):
        import pandas as pd

        start, end = (pd.Timestamp(value) for value in split.development_window.split("/"))
        window = self.effective_window
        if (split.development_data_ref != self.identity
                or start != pd.Timestamp(window.start_ms, unit="ms", tz="UTC")
                or end != pd.Timestamp(window.end_ms, unit="ms", tz="UTC")):
            raise ValueError("M1 exact development partition required")

    def require_spec(self, spec):
        instruments = spec["instruments"]
        timeframes = spec["timeframe_and_data"]
        if (instruments["symbols"] != [self.instrument]
                or instruments["market_type"] != self.market_type
                or instruments["venue_assumption"] != "Binance USDT-M perpetual"
                or timeframes["primary_timeframe"] != self.timeframe
                or timeframes["confirmation_timeframes"]
                or any(ref["timeframe"] not in (None, self.timeframe)
                       for ref in timeframes["host_data_refs"])):
            raise ValueError("M1 Strategy Spec instrument or clock substitution")


class M1HistoricalIntent(M1Intent):
    schema_version: Literal["cpw_m1_historical_intent_v1"]


class M1HistoricalCosts(M1Costs):
    qualification: Literal["HISTORICAL_EVIDENCE_REQUIRED"]
    fee_epoch: Interval
    fee_schedule_sha256: Sha
    slippage_model_sha256: Sha
    funding_notional_approval_sha256: Sha


class M1HistoricalSource(M1Source):
    """Immutable candidate identity. Evidence digests never confer read authority."""

    schema_version: Literal["cpw_m1_historical_source_v1"]
    classification: Literal["HISTORICAL_CANDIDATE"]
    funding_source: Literal["BINANCE_USDM_PUBLIC_FUNDING_HISTORY"]
    costs: M1HistoricalCosts
    provenance_sha256: Sha
    epoch_evidence_sha256: Sha
    terms_evidence_sha256: Sha
    in_sample: Interval
    out_of_sample: Interval
    gate_c_approval_sha256: Sha

    @model_validator(mode="after")
    def eligible_window(self):
        step = CADENCE[self.timeframe]
        start, end = self.effective_window.start_ms, self.effective_window.end_ms
        if (not self.epoch_window.start_ms <= start < end <= self.epoch_window.end_ms
                or not self.costs.fee_epoch.start_ms <= start < end <= self.costs.fee_epoch.end_ms
                or not start < self.in_sample.start_ms < self.in_sample.end_ms
                <= self.out_of_sample.start_ms < self.out_of_sample.end_ms == end
                or start % FUNDING_INTERVAL_MS or end % FUNDING_INTERVAL_MS
                or any(v % step for v in (self.in_sample.start_ms, self.in_sample.end_ms,
                                          self.out_of_sample.start_ms))
                or not 20 <= (end - start) // step <= 100_000):
            raise ValueError("M1 historical source requires a complete clock, epoch and frozen IS/OOS window")
        return self

    @property
    def identity(self):
        return "M1-HISTORICAL-" + content_hash(self.model_dump(mode="json")).split(":")[1]

    def require_protocol(self, protocol):
        step = CADENCE[self.timeframe]
        if (self.out_of_sample.start_ms - self.in_sample.end_ms
                < (protocol.purge_bars + protocol.embargo_bars) * step):
            raise ValueError("M1 historical source split violates frozen purge/embargo")


def exact_json(raw, *, root_type=dict):
    """Parse frozen metadata without ambiguous duplicate keys or nonfinite numbers."""
    def unique(items):
        result = {}
        for name, value in items:
            if name in result:
                raise ValueError("duplicate M1 metadata key")
            result[name] = value
        return result

    def reject_constant(_):
        raise ValueError("nonfinite M1 metadata")

    value = json.loads(raw, object_pairs_hook=unique, parse_constant=reject_constant)
    if type(value) is not root_type:
        raise ValueError(f"M1 JSON {root_type.__name__} root required")
    content_hash(value)
    return value
