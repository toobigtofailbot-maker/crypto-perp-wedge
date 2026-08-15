"""Deterministic hypothesis identity for exact relational deduplication."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

FINGERPRINT_VERSION = "hypothesis-v1"
DEFAULT_INSTRUMENT_SCOPE = "BTCUSDT_BINANCE_USDTM_PERP"
_WHITESPACE = re.compile(r"\s+")


def _normalized_text(value: Any, *, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    normalized = _WHITESPACE.sub(" ", unicodedata.normalize("NFKC", value).strip()).lower()
    if not normalized:
        raise ValueError(f"{field} must not be empty")
    return normalized


def _normalized_optional_text(value: Any, *, field: str) -> str | None:
    if value is None:
        return None
    return _normalized_text(value, field=field)


def _normalized_features(values: Iterable[Any]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError("required_data_features must be an iterable of strings")
    return tuple(
        sorted({_normalized_text(value, field="required_data_features item") for value in values})
    )


@dataclass(frozen=True)
class HypothesisDefinition:
    """The structured, non-performance-bearing identity of a hypothesis.

    Normalization is intentionally conservative: case, Unicode form, repeated
    whitespace, feature ordering, and duplicate feature labels do not affect
    identity.  Punctuation and wording do, because semantic similarity is out
    of scope for this deterministic/relational package.
    """

    strategy_family: str
    mechanism: str
    primary_timeframe: str | None
    required_data_features: tuple[str, ...]
    free_parameter_count: int | None = None
    instrument_scope: str = DEFAULT_INSTRUMENT_SCOPE

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> HypothesisDefinition:
        count = value.get("free_parameter_count")
        if count is not None and (isinstance(count, bool) or not isinstance(count, int)):
            raise TypeError("free_parameter_count must be an integer or null")
        if count is not None and count < 0:
            raise ValueError("free_parameter_count must be non-negative")
        return cls(
            strategy_family=_normalized_text(value.get("strategy_family"), field="strategy_family"),
            mechanism=_normalized_text(value.get("mechanism"), field="mechanism"),
            primary_timeframe=_normalized_optional_text(
                value.get("primary_timeframe"), field="primary_timeframe"
            ),
            required_data_features=_normalized_features(value.get("required_data_features", ())),
            free_parameter_count=count,
            instrument_scope=_normalized_text(
                value.get("instrument_scope", DEFAULT_INSTRUMENT_SCOPE),
                field="instrument_scope",
            ).upper(),
        )

    def canonical_mapping(self) -> dict[str, Any]:
        return {
            "fingerprint_version": FINGERPRINT_VERSION,
            "free_parameter_count": self.free_parameter_count,
            "instrument_scope": self.instrument_scope,
            "mechanism": self.mechanism,
            "primary_timeframe": self.primary_timeframe,
            "required_data_features": list(self.required_data_features),
            "strategy_family": self.strategy_family,
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_mapping(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )


def fingerprint(definition: HypothesisDefinition | Mapping[str, Any]) -> str:
    normalized = (
        definition
        if isinstance(definition, HypothesisDefinition)
        else HypothesisDefinition.from_mapping(definition)
    )
    return hashlib.sha256(normalized.canonical_json().encode("utf-8")).hexdigest()
