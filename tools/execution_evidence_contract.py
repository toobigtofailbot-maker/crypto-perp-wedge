"""Engine-neutral scientific execution and evidence content contracts.

The contracts in this module describe content only.  They perform no execution,
approval, persistence, canonical crossing, or runtime operation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections import Counter
from typing import Any, Mapping, TypedDict


RUN_REQUEST_SCHEMA_VERSION = "cpw_run_request_v1"
RESULT_ENVELOPE_SCHEMA_VERSION = "cpw_result_envelope_v1"
CANONICALIZATION = "cpw_engine_neutral_json_v1"
HASH_ALGORITHM = "sha256"

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_NON_AUTHORITY = {
    "authorizes_execution": False,
    "authorizes_approval": False,
    "authorizes_canonical_write": False,
    "authorizes_crossing": False,
    "authorizes_candidate_lifecycle": False,
    "authorizes_paper_live_runtime": False,
    "authorizes_capital": False,
}
_PARENT_NAMES = {"strategy_spec", "variant_manifest", "sweep_plan"}
_PARENT_FIELDS = {"id", "content_sha256"}
_DATA_IDENTITY_FIELDS = {"catalog_ref", "slice_identity", "timeframe", "stream"}
_DETERMINISM_FIELDS = {"seed"}
_ASSUMPTION_FIELDS = {
    "backtest_assumption_summary",
    "sizing_metadata",
    "data_availability_claim",
}
_RUN_REQUEST_FIELDS = {
    "schema_version",
    "parent_identities",
    "declared_variant_ids",
    "committed_denominator",
    "data_identity",
    "determinism",
    "scientific_assumptions",
    "request_content_sha256",
    "non_authority",
}
_ROW_SCIENTIFIC_FIELDS = {
    "variant_id",
    "assignment_hash",
    "outcome_category",
    "attempted",
    "metrics",
    "non_success",
    "error",
    "data_coverage",
    "lineage",
}
_ROW_FIELDS = _ROW_SCIENTIFIC_FIELDS | {"row_content_sha256"}
_SCIENTIFIC_RESULT_FIELDS = {
    "committed_denominator",
    "outcome_category_counts",
    "variant_result_rows",
}
_OUTCOME_CATEGORIES = {
    "successful",
    "failed",
    "invalid",
    "excluded",
    "errored",
    "aborted",
    "filtered",
    "data_unavailable",
    "not_attempted",
}
_PROVENANCE_FIELDS = {
    "engine_id",
    "engine_version",
    "adapter_id",
    "repo_commit",
    "environment_summary",
    "dependency_summary",
    "source_ref",
    "source_raw_sha256",
}
_COMPATIBILITY_FIELDS = {
    "result_population_id",
    "input_identity_hash",
    "result_population_identity_hash",
    "replay_normalization_contract_version",
    "replay_normalized_stable_hash",
}
_RESULT_ENVELOPE_FIELDS = {
    "schema_version",
    "request_content_sha256",
    "scientific_result",
    "evidence_content_sha256",
    "execution_provenance",
    "compatibility_evidence",
    "non_authority",
}


class RunRequest(TypedDict):
    schema_version: str
    parent_identities: dict[str, dict[str, str]]
    declared_variant_ids: list[str]
    committed_denominator: int
    data_identity: dict[str, str]
    determinism: dict[str, int | None]
    scientific_assumptions: dict[str, Any]
    request_content_sha256: str
    non_authority: dict[str, bool]


class ResultEnvelope(TypedDict):
    schema_version: str
    request_content_sha256: str
    scientific_result: dict[str, Any]
    evidence_content_sha256: str
    execution_provenance: dict[str, Any]
    compatibility_evidence: dict[str, Any] | None
    non_authority: dict[str, bool]


def _validate_json_value(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path}: non-finite floats are not supported")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path}: object keys must be strings")
            _validate_json_value(item, f"{path}.{key}")
        return
    raise ValueError(f"{path}: unsupported JSON value type: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON-compatible content using the CANON-01 byte contract."""

    _validate_json_value(value)
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"content is not canonically JSON serializable: {exc}") from exc


def content_sha256(value: Any) -> str:
    return f"{HASH_ALGORITHM}:{hashlib.sha256(canonical_json_bytes(value)).hexdigest()}"


def _require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be an object")
    return value


def _require_closed(mapping: Mapping[str, Any], fields: set[str], path: str) -> None:
    keys = set(mapping)
    if keys != fields:
        missing = sorted(fields - keys)
        unknown = sorted(keys - fields)
        raise ValueError(f"{path} fields mismatch; missing={missing}, unknown={unknown}")


def _require_non_empty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path} must be a non-empty string")
    return value


def _require_hash(value: Any, path: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{path} must match sha256:<64 lowercase hex>")


def _require_int(value: Any, path: str, *, minimum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{path} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{path} must be >= {minimum}")
    return value


def _request_identity_payload(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: request[key]
        for key in (
            "schema_version",
            "parent_identities",
            "declared_variant_ids",
            "committed_denominator",
            "data_identity",
            "determinism",
            "scientific_assumptions",
        )
    }


def build_run_request(
    *,
    parent_identities: Mapping[str, Any],
    declared_variant_ids: list[str],
    committed_denominator: int,
    data_identity: Mapping[str, Any],
    determinism: Mapping[str, Any],
    scientific_assumptions: Mapping[str, Any],
) -> RunRequest:
    request: RunRequest = {
        "schema_version": RUN_REQUEST_SCHEMA_VERSION,
        "parent_identities": copy.deepcopy(dict(parent_identities)),
        "declared_variant_ids": copy.deepcopy(declared_variant_ids),
        "committed_denominator": committed_denominator,
        "data_identity": copy.deepcopy(dict(data_identity)),
        "determinism": copy.deepcopy(dict(determinism)),
        "scientific_assumptions": copy.deepcopy(dict(scientific_assumptions)),
        "request_content_sha256": "",
        "non_authority": dict(_NON_AUTHORITY),
    }
    request["request_content_sha256"] = content_sha256(_request_identity_payload(request))
    validate_run_request(request)
    return request


def validate_run_request(request: Mapping[str, Any]) -> None:
    request = _require_mapping(request, "RunRequest")
    _require_closed(request, _RUN_REQUEST_FIELDS, "RunRequest")
    canonical_json_bytes(dict(request))
    if request["schema_version"] != RUN_REQUEST_SCHEMA_VERSION:
        raise ValueError("RunRequest.schema_version is unsupported")

    parents = _require_mapping(request["parent_identities"], "parent_identities")
    _require_closed(parents, _PARENT_NAMES, "parent_identities")
    for name in sorted(_PARENT_NAMES):
        parent = _require_mapping(parents[name], f"parent_identities.{name}")
        _require_closed(parent, _PARENT_FIELDS, f"parent_identities.{name}")
        _require_non_empty_string(parent["id"], f"parent_identities.{name}.id")
        _require_hash(parent["content_sha256"], f"parent_identities.{name}.content_sha256")

    variant_ids = request["declared_variant_ids"]
    if not isinstance(variant_ids, list) or not variant_ids:
        raise ValueError("declared_variant_ids must be a non-empty list")
    for index, variant_id in enumerate(variant_ids):
        _require_non_empty_string(variant_id, f"declared_variant_ids[{index}]")
    if len(set(variant_ids)) != len(variant_ids):
        raise ValueError("declared_variant_ids must be unique")
    denominator = _require_int(request["committed_denominator"], "committed_denominator", minimum=1)
    if denominator != len(variant_ids):
        raise ValueError("committed_denominator must equal declared_variant_ids length")

    data_identity = _require_mapping(request["data_identity"], "data_identity")
    _require_closed(data_identity, _DATA_IDENTITY_FIELDS, "data_identity")
    for field in sorted(_DATA_IDENTITY_FIELDS):
        _require_non_empty_string(data_identity[field], f"data_identity.{field}")

    determinism = _require_mapping(request["determinism"], "determinism")
    _require_closed(determinism, _DETERMINISM_FIELDS, "determinism")
    if determinism["seed"] is not None:
        _require_int(determinism["seed"], "determinism.seed")

    assumptions = _require_mapping(request["scientific_assumptions"], "scientific_assumptions")
    _require_closed(assumptions, _ASSUMPTION_FIELDS, "scientific_assumptions")
    canonical_json_bytes(assumptions["backtest_assumption_summary"])
    canonical_json_bytes(assumptions["sizing_metadata"])
    canonical_json_bytes(assumptions["data_availability_claim"])

    non_authority = _require_mapping(request["non_authority"], "non_authority")
    if dict(non_authority) != _NON_AUTHORITY:
        raise ValueError("non_authority must contain exactly the fixed false authority flags")
    _require_hash(request["request_content_sha256"], "request_content_sha256")
    expected = content_sha256(_request_identity_payload(request))
    if request["request_content_sha256"] != expected:
        raise ValueError("request_content_sha256 mismatch")


def _row_identity_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: row[key] for key in sorted(_ROW_SCIENTIFIC_FIELDS)}


def _build_row(row: Mapping[str, Any], index: int) -> dict[str, Any]:
    row = _require_mapping(row, f"variant_result_rows[{index}]")
    keys = set(row)
    if keys not in (_ROW_SCIENTIFIC_FIELDS, _ROW_FIELDS):
        missing = sorted(_ROW_SCIENTIFIC_FIELDS - keys)
        unknown = sorted(keys - _ROW_FIELDS)
        raise ValueError(
            f"variant_result_rows[{index}] fields mismatch; missing={missing}, unknown={unknown}"
        )
    built = copy.deepcopy({key: row[key] for key in _ROW_SCIENTIFIC_FIELDS})
    built["row_content_sha256"] = content_sha256(_row_identity_payload(built))
    return built


def _evidence_identity_payload(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": envelope["schema_version"],
        "request_content_sha256": envelope["request_content_sha256"],
        "scientific_result": envelope["scientific_result"],
    }


def build_result_envelope(
    *,
    request_content_sha256: str,
    committed_denominator: int,
    outcome_category_counts: Mapping[str, int],
    variant_result_rows: list[Mapping[str, Any]],
    execution_provenance: Mapping[str, Any],
    compatibility_evidence: Mapping[str, Any] | None = None,
) -> ResultEnvelope:
    rows = [_build_row(row, index) for index, row in enumerate(variant_result_rows)]
    envelope: ResultEnvelope = {
        "schema_version": RESULT_ENVELOPE_SCHEMA_VERSION,
        "request_content_sha256": request_content_sha256,
        "scientific_result": {
            "committed_denominator": committed_denominator,
            "outcome_category_counts": copy.deepcopy(dict(outcome_category_counts)),
            "variant_result_rows": rows,
        },
        "evidence_content_sha256": "",
        "execution_provenance": copy.deepcopy(dict(execution_provenance)),
        "compatibility_evidence": (
            copy.deepcopy(dict(compatibility_evidence))
            if compatibility_evidence is not None
            else None
        ),
        "non_authority": dict(_NON_AUTHORITY),
    }
    envelope["evidence_content_sha256"] = content_sha256(_evidence_identity_payload(envelope))
    validate_result_envelope(envelope)
    return envelope


def validate_result_envelope(envelope: Mapping[str, Any]) -> None:
    envelope = _require_mapping(envelope, "ResultEnvelope")
    _require_closed(envelope, _RESULT_ENVELOPE_FIELDS, "ResultEnvelope")
    canonical_json_bytes(dict(envelope))
    if envelope["schema_version"] != RESULT_ENVELOPE_SCHEMA_VERSION:
        raise ValueError("ResultEnvelope.schema_version is unsupported")
    _require_hash(envelope["request_content_sha256"], "request_content_sha256")

    result = _require_mapping(envelope["scientific_result"], "scientific_result")
    _require_closed(result, _SCIENTIFIC_RESULT_FIELDS, "scientific_result")
    denominator = _require_int(
        result["committed_denominator"], "scientific_result.committed_denominator", minimum=1
    )
    rows = result["variant_result_rows"]
    if not isinstance(rows, list):
        raise ValueError("scientific_result.variant_result_rows must be a list")
    if denominator != len(rows):
        raise ValueError("scientific_result committed_denominator must equal row count")

    variant_ids: list[str] = []
    actual_counts: Counter[str] = Counter()
    for index, row_value in enumerate(rows):
        row = _require_mapping(row_value, f"variant_result_rows[{index}]")
        _require_closed(row, _ROW_FIELDS, f"variant_result_rows[{index}]")
        variant_ids.append(_require_non_empty_string(row["variant_id"], f"variant_result_rows[{index}].variant_id"))
        _require_hash(row["assignment_hash"], f"variant_result_rows[{index}].assignment_hash", nullable=True)
        outcome = _require_non_empty_string(row["outcome_category"], f"variant_result_rows[{index}].outcome_category")
        if outcome not in _OUTCOME_CATEGORIES:
            raise ValueError(f"variant_result_rows[{index}].outcome_category is unsupported")
        actual_counts[outcome] += 1
        if not isinstance(row["attempted"], bool):
            raise ValueError(f"variant_result_rows[{index}].attempted must be boolean")
        for field in ("metrics", "non_success", "error", "data_coverage", "lineage"):
            _require_mapping(row[field], f"variant_result_rows[{index}].{field}")
            canonical_json_bytes(row[field])
        _require_hash(row["row_content_sha256"], f"variant_result_rows[{index}].row_content_sha256")
        expected_row_hash = content_sha256(_row_identity_payload(row))
        if row["row_content_sha256"] != expected_row_hash:
            raise ValueError(f"variant_result_rows[{index}].row_content_sha256 mismatch")
    if len(set(variant_ids)) != len(variant_ids):
        raise ValueError("variant_result_rows variant_id values must be unique")

    counts = _require_mapping(result["outcome_category_counts"], "outcome_category_counts")
    _require_closed(counts, _OUTCOME_CATEGORIES, "outcome_category_counts")
    normalized_counts: dict[str, int] = {}
    for category, count in counts.items():
        _require_non_empty_string(category, "outcome_category_counts key")
        normalized_counts[category] = _require_int(
            count, f"outcome_category_counts.{category}", minimum=0
        )
    expected_counts = {category: actual_counts.get(category, 0) for category in _OUTCOME_CATEGORIES}
    if sum(normalized_counts.values()) != denominator or normalized_counts != expected_counts:
        raise ValueError("outcome_category_counts must exactly reconcile to rows and denominator")

    provenance = _require_mapping(envelope["execution_provenance"], "execution_provenance")
    _require_closed(provenance, _PROVENANCE_FIELDS, "execution_provenance")
    _require_non_empty_string(provenance["engine_id"], "execution_provenance.engine_id")
    if provenance["adapter_id"] is not None:
        _require_non_empty_string(provenance["adapter_id"], "execution_provenance.adapter_id")
    if provenance["source_raw_sha256"] is not None:
        _require_hash(provenance["source_raw_sha256"], "execution_provenance.source_raw_sha256")
    canonical_json_bytes(dict(provenance))

    compatibility = envelope["compatibility_evidence"]
    if compatibility is not None:
        compatibility = _require_mapping(compatibility, "compatibility_evidence")
        _require_closed(compatibility, _COMPATIBILITY_FIELDS, "compatibility_evidence")
        _require_non_empty_string(
            compatibility["result_population_id"], "compatibility_evidence.result_population_id"
        )
        _require_mapping(compatibility["input_identity_hash"], "compatibility_evidence.input_identity_hash")
        _require_mapping(
            compatibility["result_population_identity_hash"],
            "compatibility_evidence.result_population_identity_hash",
        )
        _require_non_empty_string(
            compatibility["replay_normalization_contract_version"],
            "compatibility_evidence.replay_normalization_contract_version",
        )
        if compatibility["replay_normalized_stable_hash"] is not None:
            _require_hash(
                compatibility["replay_normalized_stable_hash"],
                "compatibility_evidence.replay_normalized_stable_hash",
            )
        canonical_json_bytes(dict(compatibility))

    non_authority = _require_mapping(envelope["non_authority"], "non_authority")
    if dict(non_authority) != _NON_AUTHORITY:
        raise ValueError("non_authority must contain exactly the fixed false authority flags")
    _require_hash(envelope["evidence_content_sha256"], "evidence_content_sha256")
    expected = content_sha256(_evidence_identity_payload(envelope))
    if envelope["evidence_content_sha256"] != expected:
        raise ValueError("evidence_content_sha256 mismatch")
