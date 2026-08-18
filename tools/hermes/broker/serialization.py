"""BROKER-1-local canonical identity for executable actions and approval claims."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel

MAX_CANONICAL_BYTES = 1_000_000
MAX_CANONICAL_DEPTH = 30
MAX_CONTAINER_ITEMS = 10_000


class BrokerCanonicalizationError(ValueError):
    """Raised when an object has no permitted BROKER-1 canonical identity."""


def _validate(value: Any, *, depth: int = 0) -> None:
    if depth > MAX_CANONICAL_DEPTH:
        raise BrokerCanonicalizationError("canonical JSON nesting exceeds 30 levels")
    if isinstance(value, float):
        raise BrokerCanonicalizationError("floating-point values are forbidden")
    if value is None or isinstance(value, (str, int, bool)):
        return
    if isinstance(value, Mapping):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise BrokerCanonicalizationError("canonical object has too many items")
        for key, child in value.items():
            if not isinstance(key, str):
                raise BrokerCanonicalizationError("canonical object keys must be strings")
            _validate(child, depth=depth + 1)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise BrokerCanonicalizationError("canonical sequence has too many items")
        for child in value:
            _validate(child, depth=depth + 1)
        return
    raise BrokerCanonicalizationError(f"unsupported canonical type: {type(value).__name__}")


def broker_canonical_json_bytes(value: BaseModel | Mapping[str, Any]) -> bytes:
    """Return broker_canonical_json_v1 bytes with exactly one trailing LF."""

    document: Any = value.model_dump(mode="json") if isinstance(value, BaseModel) else dict(value)
    _validate(document)
    encoded = (
        json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise BrokerCanonicalizationError("canonical object exceeds the byte limit")
    return encoded


def broker_sha256(value: BaseModel | Mapping[str, Any]) -> str:
    return hashlib.sha256(broker_canonical_json_bytes(value)).hexdigest()


def scope_digest(scope: BaseModel) -> str:
    return broker_sha256(scope)
