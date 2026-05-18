import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from tools.research_automation.local_parameter_sweep import (
    DEFAULT_MAX_POINT_COUNT,
    ParameterSweepSpec,
    run_local_parameter_sweep,
)


IMPLEMENTATION_ID = "wp_12u_auto_20_local_json_sweep_spec_loader_v1"
PACKAGE_LABEL = "WP-12u / AUTO-20"
SUPPORTED_SPEC_VERSION = "wp12t-design-v1"
SUPPORTED_MATERIALIZATION_KIND = "local_parameter_sweep_spec"
REQUIRED_BOUNDARY_MARKERS = (
    "additive_to_in_memory_parameter_sweep_spec",
    "not_canonical_research_artifact",
    "not_tools_registry_validated",
    "not_query_layer_exposed",
    "no_runtime_or_downstream_authority",
)

_TOP_LEVEL_FIELDS = {
    "spec_version",
    "materialization_kind",
    "locality",
    "boundary_markers",
    "parameter_sweep_spec",
}
_LOCALITY_FIELDS = {
    "local_only",
    "research_only",
    "non_authoritative",
    "creates_committed_evidence",
}
_SPEC_FIELDS = {
    "sweep_id",
    "candidate_id",
    "evaluation_purpose",
    "data_refs",
    "timeframe",
    "evaluation_window",
    "base_parameters",
    "sweep_parameters",
    "pipeline_version",
    "static_metadata",
}
_REQUIRED_SPEC_FIELDS = _SPEC_FIELDS - {"static_metadata"}


@dataclass(frozen=True)
class LocalJsonSweepSpecLoadResult:
    spec_file: Path
    spec: ParameterSweepSpec | None
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


@dataclass(frozen=True)
class LocalJsonParameterSweepRunResult:
    load_result: LocalJsonSweepSpecLoadResult
    sweep_result: Any | None
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


def _failure_load_result(spec_file: Path, failure_reasons: tuple[str, ...]) -> LocalJsonSweepSpecLoadResult:
    return LocalJsonSweepSpecLoadResult(
        spec_file=spec_file,
        spec=None,
        failure_reasons=failure_reasons,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=False,
    )


def _duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _json_serializable(value: Any) -> bool:
    try:
        _stable_json(value)
    except (TypeError, ValueError):
        return False
    return True


def _is_valid_name(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        return False
    if "." in value:
        return False
    if "/" in value or "\\" in value:
        return False
    return True


def _validate_field_set(
    value: Mapping[str, Any],
    *,
    label: str,
    required_fields: set[str],
    allowed_fields: set[str],
    failures: list[str],
) -> None:
    missing = sorted(required_fields - set(value))
    extra = sorted(set(value) - allowed_fields)
    for field_name in missing:
        failures.append(f"{label}.{field_name} is required")
    for field_name in extra:
        failures.append(f"{label}.{field_name} is not supported")


def _validate_string(value: Any, label: str, failures: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        failures.append(f"{label} must be a non-empty string")


def _validate_keyed_mapping(
    value: Any,
    label: str,
    failures: list[str],
    *,
    string_values: bool = False,
) -> None:
    if not isinstance(value, Mapping):
        failures.append(f"{label} must be a mapping")
        return
    for key, item in value.items():
        if not _is_valid_name(key):
            failures.append(f"{label} keys must be non-empty unambiguous strings")
        if string_values:
            if not isinstance(item, str) or not item.strip():
                failures.append(f"{label}.{key} must be a non-empty string")
        elif not _json_serializable(item):
            failures.append(f"{label}.{key} must be JSON-serializable")


def _validate_locality(value: Any, failures: list[str]) -> None:
    if not isinstance(value, Mapping):
        failures.append("locality must be a mapping")
        return
    _validate_field_set(
        value,
        label="locality",
        required_fields=_LOCALITY_FIELDS,
        allowed_fields=_LOCALITY_FIELDS,
        failures=failures,
    )
    expected = {
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
    }
    for field_name, expected_value in expected.items():
        if value.get(field_name) is not expected_value:
            failures.append(f"locality.{field_name} must be {str(expected_value).lower()}")


def _validate_boundary_markers(value: Any, failures: list[str]) -> None:
    if isinstance(value, str) or not isinstance(value, list):
        failures.append("boundary_markers must be an array")
        return
    if any(not isinstance(marker, str) or not marker.strip() for marker in value):
        failures.append("boundary_markers must contain non-empty strings")
        return
    markers = set(value)
    for marker in REQUIRED_BOUNDARY_MARKERS:
        if marker not in markers:
            failures.append(f"boundary_markers missing {marker}")


def _convert_parameter_sweep_spec(value: Any) -> tuple[ParameterSweepSpec | None, tuple[str, ...]]:
    failures: list[str] = []
    if not isinstance(value, Mapping):
        return None, ("parameter_sweep_spec must be a mapping",)

    _validate_field_set(
        value,
        label="parameter_sweep_spec",
        required_fields=_REQUIRED_SPEC_FIELDS,
        allowed_fields=_SPEC_FIELDS,
        failures=failures,
    )
    for field_name in ("sweep_id", "candidate_id", "evaluation_purpose", "timeframe", "pipeline_version"):
        if field_name in value:
            _validate_string(value[field_name], f"parameter_sweep_spec.{field_name}", failures)

    raw_data_refs = value.get("data_refs")
    if isinstance(raw_data_refs, str) or not isinstance(raw_data_refs, list):
        failures.append("parameter_sweep_spec.data_refs must be an array of non-empty strings")
        data_refs: tuple[str, ...] = ()
    elif not raw_data_refs or any(not isinstance(item, str) or not item.strip() for item in raw_data_refs):
        failures.append("parameter_sweep_spec.data_refs must contain non-empty strings")
        data_refs = tuple(item for item in raw_data_refs if isinstance(item, str))
    else:
        data_refs = tuple(raw_data_refs)

    evaluation_window = value.get("evaluation_window")
    _validate_keyed_mapping(evaluation_window, "evaluation_window", failures, string_values=True)
    if isinstance(evaluation_window, Mapping):
        for field_name in ("start", "end"):
            item = evaluation_window.get(field_name)
            if not isinstance(item, str) or not item.strip():
                failures.append(f"evaluation_window.{field_name} must be a non-empty string")

    base_parameters = value.get("base_parameters")
    _validate_keyed_mapping(base_parameters, "base_parameters", failures)
    base_names = set(base_parameters) if isinstance(base_parameters, Mapping) else set()

    raw_sweep_parameters = value.get("sweep_parameters")
    sweep_parameters: dict[str, tuple[Any, ...]] = {}
    if not isinstance(raw_sweep_parameters, Mapping):
        failures.append("sweep_parameters must be a mapping")
    elif not raw_sweep_parameters:
        failures.append("sweep_parameters must contain at least one axis")
    else:
        for name, raw_values in raw_sweep_parameters.items():
            if not _is_valid_name(name):
                failures.append("sweep_parameters keys must be non-empty unambiguous strings")
            if name in base_names:
                failures.append(f"sweep_parameters.{name} overlaps base_parameters")
            if not isinstance(raw_values, list):
                failures.append(f"sweep_parameters.{name} must be an array")
                continue
            if not raw_values:
                failures.append(f"sweep_parameters.{name} must contain at least one value")
                continue
            serialized_values: set[str] = set()
            for item in raw_values:
                if not _json_serializable(item):
                    failures.append(f"sweep_parameters.{name} values must be JSON-serializable")
                    continue
                serialized = _stable_json(item)
                if serialized in serialized_values:
                    failures.append(f"sweep_parameters.{name} contains duplicate values")
                serialized_values.add(serialized)
            sweep_parameters[str(name)] = tuple(raw_values)

    static_metadata = value.get("static_metadata", {})
    _validate_keyed_mapping(static_metadata, "static_metadata", failures, string_values=True)

    if failures:
        return None, tuple(failures)

    return (
        ParameterSweepSpec(
            sweep_id=value["sweep_id"],
            candidate_id=value["candidate_id"],
            evaluation_purpose=value["evaluation_purpose"],
            data_refs=data_refs,
            timeframe=value["timeframe"],
            evaluation_window=dict(evaluation_window),
            base_parameters=dict(base_parameters),
            sweep_parameters=sweep_parameters,
            pipeline_version=value["pipeline_version"],
            static_metadata=dict(static_metadata),
        ),
        (),
    )


def load_local_json_sweep_spec(spec_file: str | Path) -> LocalJsonSweepSpecLoadResult:
    spec_path = spec_file if isinstance(spec_file, Path) else Path(spec_file)
    if not spec_path.exists():
        return _failure_load_result(spec_path, ("spec_file does not exist",))
    if spec_path.is_dir():
        return _failure_load_result(spec_path, ("spec_file must be a file",))

    try:
        payload = json.loads(
            spec_path.read_text(encoding="utf-8"),
            object_pairs_hook=_duplicate_rejecting_object,
        )
    except json.JSONDecodeError as exc:
        return _failure_load_result(spec_path, (f"invalid JSON: {exc.msg}",))
    except ValueError as exc:
        return _failure_load_result(spec_path, (str(exc),))
    except OSError as exc:
        return _failure_load_result(spec_path, (f"spec_file could not be read: {exc}",))

    failures: list[str] = []
    if not isinstance(payload, Mapping):
        return _failure_load_result(spec_path, ("top-level JSON must be an object",))

    _validate_field_set(
        payload,
        label="top_level",
        required_fields=_TOP_LEVEL_FIELDS,
        allowed_fields=_TOP_LEVEL_FIELDS,
        failures=failures,
    )
    if payload.get("spec_version") != SUPPORTED_SPEC_VERSION:
        failures.append("unsupported spec_version")
    if payload.get("materialization_kind") != SUPPORTED_MATERIALIZATION_KIND:
        failures.append("unsupported materialization_kind")
    _validate_locality(payload.get("locality"), failures)
    _validate_boundary_markers(payload.get("boundary_markers"), failures)

    spec: ParameterSweepSpec | None = None
    if not failures:
        spec, spec_failures = _convert_parameter_sweep_spec(payload.get("parameter_sweep_spec"))
        failures.extend(spec_failures)

    if failures:
        return _failure_load_result(spec_path, tuple(failures))

    return LocalJsonSweepSpecLoadResult(
        spec_file=spec_path,
        spec=spec,
        failure_reasons=(),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=True,
    )


def run_local_json_parameter_sweep(
    spec_file: str | Path,
    output_root: str | Path,
    registry_output_root: str | Path,
    *,
    max_point_count: int = DEFAULT_MAX_POINT_COUNT,
) -> LocalJsonParameterSweepRunResult:
    load_result = load_local_json_sweep_spec(spec_file)
    if load_result.spec is None:
        return LocalJsonParameterSweepRunResult(
            load_result=load_result,
            sweep_result=None,
            failure_reasons=load_result.failure_reasons,
            local_only=True,
            research_only=True,
            non_authoritative=True,
            creates_committed_evidence=False,
            protected_boundary_preserved=False,
        )

    sweep_result = run_local_parameter_sweep(
        load_result.spec,
        output_root,
        registry_output_root,
        max_point_count=max_point_count,
    )
    return LocalJsonParameterSweepRunResult(
        load_result=load_result,
        sweep_result=sweep_result,
        failure_reasons=tuple(getattr(sweep_result, "failure_reasons", ())),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=bool(getattr(sweep_result, "protected_boundary_preserved", False)),
    )
