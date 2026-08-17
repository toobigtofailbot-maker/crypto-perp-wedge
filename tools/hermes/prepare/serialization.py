"""Hermes-local canonical bytes for inert H2.5 payload commitments."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel


class CanonicalSerializationError(ValueError):
    """Raised when a value cannot have one safe Hermes byte identity."""


def _validate_json_value(value: Any, *, depth: int = 0) -> None:
    if depth > 30:
        raise CanonicalSerializationError("canonical JSON nesting exceeds 30 levels")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalSerializationError("non-finite floating-point values are forbidden")
        return
    if value is None or isinstance(value, (str, int, bool)):
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise CanonicalSerializationError("canonical JSON object keys must be strings")
            _validate_json_value(child, depth=depth + 1)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            _validate_json_value(child, depth=depth + 1)
        return
    raise CanonicalSerializationError(
        f"unsupported canonical JSON value type: {type(value).__name__}"
    )


def canonical_json_bytes(value: BaseModel | Mapping[str, Any]) -> bytes:
    """Return compact sorted UTF-8 JSON with exactly one trailing LF.

    For values accepted by ``repo_canonical_json_v1`` the value bytes match that
    helper, with the H2.5 whole-object contract's required final LF added.  This
    local serializer also handles the validated finite confidence floats already
    present in H2 proposals; NaN and infinities remain forbidden.  Keeping it
    local avoids importing canonical-write or KDAUTH authority modules.
    """

    document: Any
    if isinstance(value, BaseModel):
        document = value.model_dump(mode="json")
    else:
        document = dict(value)
    _validate_json_value(document)
    encoded = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return encoded + b"\n"


def canonical_sha256(value: BaseModel | Mapping[str, Any]) -> str:
    """Hash only the exact canonical bytes of one validated object."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
