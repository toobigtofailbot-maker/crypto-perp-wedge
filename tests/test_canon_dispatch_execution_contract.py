import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft7Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "research/schemas"
FIXTURES = (
    ROOT
    / "scratch/WP-CANON-DISPATCH-CONTROL-PLANE-DESIGN-LOCK-01/fixtures"
)
VALID = FIXTURES / "valid"
INVALID = FIXTURES / "invalid"
CANONICAL_RP0007_RELATIVE_PATH = Path(
    "research/result_populations/RP-0007.result_population.json"
)
CANONICAL_RP0007_BYTE_LENGTH = 213_923
CANONICAL_RP0007_SHA256 = (
    "ff1104cebcb2775f3f64d2e5bec72b3aaaeeb4187740978e79a26a4819ee2308"
)
ATTEMPT_OUTCOME_CATEGORIES = (
    "successful",
    "failed",
    "invalid",
    "excluded",
    "errored",
    "aborted",
    "filtered",
    "data_unavailable",
)
TERMINAL_ACCOUNTING_CATEGORIES = (
    *ATTEMPT_OUTCOME_CATEGORIES,
    "not_attempted",
)
TERMINAL_REASONS = {
    "run_completed": "completed_denominator_accounted",
    "run_failed_process_start": "runner_process_start_failed",
    "run_failed_midrun": "runner_failed_before_denominator_complete",
    "run_blocked": "fail_closed_stop_condition",
}
OUTCOME_REASONS = {
    "successful": "completed",
    "failed": "runner_failure",
    "invalid": "validation_failure",
    "excluded": "exclusion_rule",
    "errored": "execution_error",
    "aborted": "abort_condition",
    "filtered": "filter_rule",
    "data_unavailable": "data_missing",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def schema_validator(name: str) -> Draft7Validator:
    schema = load(SCHEMAS / name)
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())


def validator_for(document: dict) -> Draft7Validator:
    if document.get("schema_version") == "canon_dispatch_record_v1":
        return schema_validator("canon_dispatch_record.schema.json")
    return schema_validator("canon_execution_event.schema.json")


def error_locations(errors) -> str:
    rendered = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        rendered.append(f"{path}: {error.message}")
    return "\n".join(rendered)


def _utc_date(value: str) -> str:
    return (
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        .astimezone(timezone.utc)
        .strftime("%Y%m%d")
    )


def dispatch_semantic_errors(record: dict) -> list[str]:
    errors = []
    dispatch_id = record["dispatch_id"]
    run_id = record["run_binding"]["run_id"]
    queue_id = record["queue_binding"]["queue_item_id"]
    authorization = record["dispatch_authorization"]
    expected_dispatch_path = (
        f"research/queue/dispatch_records/{dispatch_id}.dispatch_record.json"
    )
    expected_stream_path = (
        f"research/queue/execution_events/{run_id}.execution_events.jsonl"
    )
    if record["dispatch_record_path"] != expected_dispatch_path:
        errors.append("dispatch ID/path mismatch")
    if dispatch_id.split("-")[1] != _utc_date(record["created_at"]):
        errors.append("dispatch ID/date mismatch")
    if record["queue_binding"]["path"] != (
        f"research/queue/admissions/{queue_id}.queue_item.json"
    ):
        errors.append("queue ID/path mismatch")
    if any(
        (
            authorization["authorized_queue_item_id"] != queue_id,
            authorization["authorized_dispatch_id"] != dispatch_id,
            authorization["authorized_run_id"] != run_id,
        )
    ):
        errors.append("Karl authorization identity mismatch")
    if record["run_binding"]["execution_event_stream_path"] != expected_stream_path:
        errors.append("run ID/stream path mismatch")
    if record["output_targets"]["execution_event_stream_path"] != expected_stream_path:
        errors.append("output/event stream target mismatch")
    denominator = record["denominator"]
    budget = record["budget"]
    if len(
        {
            denominator["planned"],
            denominator["variant_manifest_value"],
            denominator["sweep_plan_value"],
            budget["upper_bound"],
        }
    ) != 1:
        errors.append("dispatch denominator/budget mismatch")
    forbidden_progress_keys = {
        "progress",
        "terminal_state",
        "attempts_completed",
        "outcome_counts",
        "execution_status",
    }
    if forbidden_progress_keys.intersection(record):
        errors.append("dispatch contains mutable progress or terminal fields")
    return errors


def terminal_semantic_errors(event: dict) -> list[str]:
    terminal = event["run_terminal"]
    state = terminal["terminal_state"]
    accounting = terminal["denominator_accounting"]
    budget = terminal["budget"]
    counts = accounting["outcome_counts"]
    errors = []
    if terminal["terminal_reason_code"] != TERMINAL_REASONS.get(state):
        errors.append("terminal state/reason mismatch")
    population_sum = sum(counts[name] for name in TERMINAL_ACCOUNTING_CATEGORIES)
    attempted_sum = population_sum - counts["not_attempted"]
    if population_sum != accounting["population_accounted_total"]:
        errors.append("outcome counts/population total mismatch")
    if accounting["population_accounted_total"] != accounting["planned"]:
        errors.append("terminal denominator is not completely accounted")
    if attempted_sum != accounting["attempts_recorded"]:
        errors.append("attempt outcome count mismatch")
    if counts["not_attempted"] != accounting["not_attempted"]:
        errors.append("not-attempted count mismatch")
    if budget["actual"] != accounting["attempts_recorded"]:
        errors.append("budget actual/attempt count mismatch")
    if budget["upper_bound"] != accounting["planned"]:
        errors.append("budget upper bound/planned denominator mismatch")
    if budget["actual"] > budget["upper_bound"]:
        errors.append("budget actual exceeds upper bound")
    if state == "run_completed" and not (
        terminal["process_started"]
        and accounting["attempts_recorded"] == accounting["planned"]
        and accounting["not_attempted"] == 0
    ):
        errors.append("completed denominator mismatch")
    if state == "run_failed_process_start" and not (
        terminal["process_started"] is False
        and accounting["attempts_recorded"] == 0
        and accounting["not_attempted"] == accounting["planned"]
    ):
        errors.append("process-start failure accounting mismatch")
    if state == "run_failed_midrun" and not (
        terminal["process_started"]
        and accounting["attempts_recorded"] < accounting["planned"]
        and accounting["not_attempted"] > 0
    ):
        errors.append("midrun partial denominator mismatch")
    return errors


def event_semantic_errors(event: dict) -> list[str]:
    errors = []
    run_id = event["bindings"]["run_id"]
    sequence = event["sequence_number"]
    expected_event_id = f"EXEC-EVENT-{run_id}-{sequence:06d}"
    expected_stream = f"research/queue/execution_events/{run_id}.execution_events.jsonl"
    if event["event_id"] != expected_event_id:
        errors.append("event ID/run/sequence mismatch")
    if event["stream_path"] != expected_stream:
        errors.append("run ID/stream path mismatch")
    if event["event_type"] == "attempt_outcome":
        outcome = event["attempt_outcome"]
        if outcome["reason_code"] != OUTCOME_REASONS[outcome["outcome_category"]]:
            errors.append("attempt outcome/reason mismatch")
    if event["event_type"] == "run_terminal":
        errors.extend(terminal_semantic_errors(event))
    return errors


def stream_semantic_errors(dispatch: dict, events: list[dict]) -> list[str]:
    errors = []
    if not events:
        return ["execution stream is empty"]
    expected_binding = {
        "dispatch_id": dispatch["dispatch_id"],
        "dispatch_record_path": dispatch["dispatch_record_path"],
        "dispatch_record_sha256": "sha256:"
        + hashlib.sha256((VALID / "dispatch_record.json").read_bytes()).hexdigest(),
        "run_id": dispatch["run_binding"]["run_id"],
        "queue_item_id": dispatch["queue_binding"]["queue_item_id"],
    }
    for event in events:
        errors.extend(event_semantic_errors(event))
        if event["bindings"] != expected_binding:
            errors.append("event binding differs from immutable dispatch")
    sequences = [event["sequence_number"] for event in events]
    if sequences != list(range(1, len(events) + 1)):
        errors.append("event sequence is not contiguous and monotonic")
    event_ids = [event["event_id"] for event in events]
    if len(event_ids) != len(set(event_ids)):
        errors.append("event ID collision")
    if events[0]["event_type"] != "run_start":
        errors.append("run_start must be first")
    terminals = [event for event in events if event["event_type"] == "run_terminal"]
    if len(terminals) != 1 or events[-1].get("event_type") != "run_terminal":
        errors.append("stream must end with exactly one terminal event")
        return errors
    attempts = [event for event in events if event["event_type"] == "attempt_outcome"]
    terminal = terminals[0]["run_terminal"]
    start = events[0]["run_start"]
    if [event["attempt_outcome"]["attempt_number"] for event in attempts] != list(
        range(1, len(attempts) + 1)
    ):
        errors.append("attempt numbers are not contiguous")
    variant_ids = [event["attempt_outcome"]["variant_id"] for event in attempts]
    if len(variant_ids) != len(set(variant_ids)):
        errors.append("variant attempt identity reused")
    if len(attempts) != terminal["denominator_accounting"]["attempts_recorded"]:
        errors.append("stream attempt count/terminal mismatch")
    if start["planned_denominator"] != dispatch["denominator"]["planned"]:
        errors.append("start/dispatch denominator mismatch")
    if start["budget"]["upper_bound"] != dispatch["budget"]["upper_bound"]:
        errors.append("start/dispatch budget mismatch")
    if start["runner_process_started"] != terminal["process_started"]:
        errors.append("start/terminal process-start truth mismatch")
    return errors


def mutate(base: dict, mutation: dict) -> None:
    parts = mutation["path"].split(".")
    parent = base
    for part in parts[:-1]:
        parent = parent[part]
    leaf = parts[-1]
    if mutation["operation"] == "remove":
        parent.pop(leaf)
    else:
        parent[leaf] = mutation["value"]


def materialize_case(path: Path) -> tuple[dict, dict]:
    case = load(path)
    document = load(FIXTURES / case["base"])
    for mutation in case["mutations"]:
        mutate(document, mutation)
    return case, document


def clone_attempt(template: dict, attempt_number: int, sequence: int) -> dict:
    event = copy.deepcopy(template)
    event["sequence_number"] = sequence
    event["event_id"] = f"EXEC-EVENT-{event['bindings']['run_id']}-{sequence:06d}"
    event["attempt_outcome"]["attempt_number"] = attempt_number
    event["attempt_outcome"]["variant_id"] = f"H004R2-VARIANT-{attempt_number:03d}"
    return event


def build_stream(terminal_name: str) -> list[dict]:
    start = load(VALID / "run_start.json")
    success = load(VALID / "attempt_successful.json")
    failed = load(VALID / "attempt_failed.json")
    errored = load(VALID / "attempt_errored.json")
    terminal = load(VALID / terminal_name)
    state = terminal["run_terminal"]["terminal_state"]
    if state == "run_failed_process_start":
        start["run_start"]["runner_process_started"] = False
        return [start, terminal]
    attempts_recorded = terminal["run_terminal"]["denominator_accounting"][
        "attempts_recorded"
    ]
    failed_count = terminal["run_terminal"]["denominator_accounting"][
        "outcome_counts"
    ]["failed"]
    errored_count = terminal["run_terminal"]["denominator_accounting"][
        "outcome_counts"
    ]["errored"]
    templates = [success] * (attempts_recorded - failed_count - errored_count)
    templates += [failed] * failed_count + [errored] * errored_count
    attempts = [
        clone_attempt(template, attempt_number, attempt_number + 1)
        for attempt_number, template in enumerate(templates, 1)
    ]
    return [start, *attempts, terminal]


def test_schemas_are_valid_draft7_contracts():
    for name in (
        "canon_dispatch_record.schema.json",
        "canon_execution_event.schema.json",
    ):
        schema = load(SCHEMAS / name)
        Draft7Validator.check_schema(schema)
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["additionalProperties"] is False


@pytest.mark.parametrize("path", sorted(VALID.glob("*.json")), ids=lambda p: p.stem)
def test_valid_fixtures_pass_schema_and_semantics(path):
    document = load(path)
    errors = list(validator_for(document).iter_errors(document))
    assert not errors, error_locations(errors)
    if document["schema_version"] == "canon_dispatch_record_v1":
        assert dispatch_semantic_errors(document) == []
    else:
        assert event_semantic_errors(document) == []


@pytest.mark.parametrize(
    "terminal_name",
    [
        "terminal_completed.json",
        "terminal_process_start_failure.json",
        "terminal_midrun_failure.json",
        "terminal_blocked.json",
    ],
)
def test_representative_streams_are_ordered_append_only_and_terminal_once(
    terminal_name,
):
    dispatch = load(VALID / "dispatch_record.json")
    events = build_stream(terminal_name)
    assert all(
        not list(schema_validator("canon_execution_event.schema.json").iter_errors(event))
        for event in events
    )
    assert stream_semantic_errors(dispatch, events) == []


@pytest.mark.parametrize("path", sorted(INVALID.glob("*.case.json")), ids=lambda p: p.stem)
def test_invalid_fixtures_fail_for_intended_reason(path):
    case, document = materialize_case(path)
    schema_errors = list(validator_for(document).iter_errors(document))
    semantic_errors = []
    if not schema_errors:
        if document["schema_version"] == "canon_dispatch_record_v1":
            semantic_errors = dispatch_semantic_errors(document)
        else:
            semantic_errors = event_semantic_errors(document)
    assert schema_errors or semantic_errors, case["expected_reason"]
    rendered = (error_locations(schema_errors) + "\n" + "\n".join(semantic_errors)).lower()
    expected_markers = {
        "bad_hash": ("raw_sha256", "does not match"),
        "missing_queue_binding": ("queue_binding", "required"),
        "free_form_executable_command": ("command", "additional properties"),
        "unknown_event_state": ("event_type", "run_paused"),
        "unknown_terminal_state": ("terminal_state", "success"),
        "not_attempted_attempt_outcome": ("outcome_category", "not_attempted"),
        "go_readiness_vocabulary": ("readiness", "additional properties"),
        "completed_denominator_mismatch": ("completed denominator mismatch",),
        "midrun_claiming_full_completion": ("midrun partial denominator mismatch",),
        "retry_allowance_inconsistent": ("retry_allowance",),
        "mutable_progress_in_dispatch": ("progress", "additional properties"),
        "canonical_rp_authority_claim": (
            "canonical_result_population_write_forbidden",
            "true was expected",
        ),
    }
    case_name = path.name.removesuffix(".case.json")
    assert all(marker in rendered for marker in expected_markers[case_name]), rendered


def test_terminal_vocabulary_and_event_specific_payloads_are_closed():
    schema = load(SCHEMAS / "canon_execution_event.schema.json")
    attempt_enum = schema["definitions"]["attempt_outcome"]["properties"][
        "outcome_category"
    ]["enum"]
    assert attempt_enum == list(ATTEMPT_OUTCOME_CATEGORIES)
    terminal_enum = schema["definitions"]["run_terminal"]["properties"][
        "terminal_state"
    ]["enum"]
    assert terminal_enum == [
        "run_completed",
        "run_failed_process_start",
        "run_failed_midrun",
        "run_blocked",
    ]
    start = load(VALID / "run_start.json")
    start["attempt_outcome"] = load(VALID / "attempt_successful.json")[
        "attempt_outcome"
    ]
    assert list(schema_validator("canon_execution_event.schema.json").iter_errors(start))


def test_denominator_budget_and_no_retry_rules_fail_closed():
    completed = load(VALID / "terminal_completed.json")
    completed["run_terminal"]["budget"]["actual"] = 82
    completed["run_terminal"]["denominator_accounting"]["attempts_recorded"] = 82
    assert "budget actual exceeds upper bound" in terminal_semantic_errors(completed)

    dispatch = load(VALID / "dispatch_record.json")
    dispatch["budget"]["upper_bound"] = 82
    assert "dispatch denominator/budget mismatch" in dispatch_semantic_errors(dispatch)

    attempt = load(VALID / "attempt_successful.json")
    attempt["attempt_outcome"]["outcome_category"] = "not_attempted"
    schema_errors = list(
        schema_validator("canon_execution_event.schema.json").iter_errors(attempt)
    )
    assert schema_errors
    assert any(error.absolute_path[-1] == "outcome_category" for error in schema_errors)


def test_valid_fixtures_contain_no_positive_authority_vocabulary():
    forbidden_values = {"go", "no-go", "ready", "readiness", "promote", "promotion"}

    def values(node):
        if isinstance(node, dict):
            for child in node.values():
                yield from values(child)
        elif isinstance(node, list):
            for child in node:
                yield from values(child)
        elif isinstance(node, str):
            yield node.lower()

    for path in VALID.glob("*.json"):
        assert forbidden_values.isdisjoint(values(load(path)))


def test_production_dispatch_boundary_preserves_canonical_rp_and_has_no_fixture():
    dispatch_root = ROOT / "research/queue/dispatch_records"
    execution_root = ROOT / "research/queue/execution_events"
    result_population_root = ROOT / "research/result_populations"
    result_population_path = ROOT / CANONICAL_RP0007_RELATIVE_PATH
    assert sorted(result_population_root.glob("RP-0007*")) == [
        result_population_path
    ]
    result_population_before = result_population_path.read_bytes()
    assert len(result_population_before) == CANONICAL_RP0007_BYTE_LENGTH
    assert (
        hashlib.sha256(result_population_before).hexdigest()
        == CANONICAL_RP0007_SHA256
    )
    dispatch_paths = sorted(dispatch_root.glob("*.json"))
    assert [path.name for path in dispatch_paths] == [
        "DSP-20260804-H004R2A1.dispatch_record.json"
    ]
    dispatch_raw = dispatch_paths[0].read_bytes()
    assert len(dispatch_raw) == 6215
    assert hashlib.sha256(dispatch_raw).hexdigest() == (
        "8b6804ac5fb45fb3d4274acf9e97e8aa8707728b0bf9857932300692854d7d3c"
    )
    assert json.loads(dispatch_raw)["dispatch_id"] == "DSP-20260804-H004R2A1"
    assert not list(execution_root.glob("*.jsonl"))
    assert not list(FIXTURES.rglob("RP-*.result_population.json"))
    assert sorted(result_population_root.glob("RP-0007*")) == [
        result_population_path
    ]
    result_population_after = result_population_path.read_bytes()
    assert result_population_after == result_population_before
    assert len(result_population_after) == CANONICAL_RP0007_BYTE_LENGTH
    assert (
        hashlib.sha256(result_population_after).hexdigest()
        == CANONICAL_RP0007_SHA256
    )


def test_h004_queue_gate_q_and_admission_record_bytes_are_preserved():
    expected = {
        "research/queue/admissions/QI-20260717-H004R2B1.queue_item.json":
            "47ba045b4ac89588e1865c280b080f0922cef6bb1e7d4e7880090ba07a44d967",
        "research/queue/gate_q_approvals/GATE-Q-H004-R2-04B-0001.gate_q_approval.json":
            "8645018c04a565761d72047b5225fbfd5694e342f5180407f0c8b111ba310fed",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    audit = ROOT / "research/queue/admission_audit/queue_admissions.jsonl"
    first_line = audit.read_bytes().splitlines(keepends=True)[0]
    assert hashlib.sha256(first_line).hexdigest() == (
        "e668475f7d9f0d3d3c425a173aa1eb593814d824d4590c794887bde21368d3e2"
    )
