import copy
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_candidate_registry import (
    CANDIDATE_LIFECYCLE_REGISTRY_SCHEMA_PATH,
    DEFAULT_CANDIDATE_REGISTRY_FIXTURE_DIR,
    REPO_ROOT,
    validate_candidate_registries,
)


VALID_FIXTURE_PATH = (
    DEFAULT_CANDIDATE_REGISTRY_FIXTURE_DIR / "valid_example.candidate_lifecycle_registry.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_schema(path: Path = CANDIDATE_LIFECYCLE_REGISTRY_SCHEMA_PATH) -> dict:
    return _load_json(path)


def _valid_registry() -> dict:
    return _load_json(VALID_FIXTURE_PATH)


def _write_registry(registry_dir: Path, payload: dict) -> Path:
    registry_dir.mkdir(parents=True, exist_ok=True)
    path = registry_dir / "fixture.candidate_lifecycle_registry.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _evidence_ref(artifact_type: str, artifact_id: str = "FIXTURE-EVIDENCE") -> dict:
    return {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "artifact_ref": artifact_id,
        "relationship": "decision_evidence",
        "authority_boundary": "evidence_link_only",
        "identity_hash": None,
        "notes": "Generated test fixture evidence.",
    }


def _event(
    *,
    event_id: str,
    candidate_id: str = "CANDIDATE-EXAMPLE-0001",
    event_sequence: int,
    event_type: str,
    timestamp_utc: str,
    from_status: str | None,
    to_status: str,
    related_evidence_links: list[dict] | None = None,
) -> dict:
    return {
        "event_id": event_id,
        "event_sequence": event_sequence,
        "candidate_id": candidate_id,
        "event_type": event_type,
        "timestamp_utc": timestamp_utc,
        "actor": "pytest fixture",
        "gate": "pytest gate",
        "from_status": from_status,
        "to_status": to_status,
        "reason": "Pytest fixture transition.",
        "related_evidence_links": related_evidence_links or [],
        "blocking_or_exception_refs": [],
        "non_authority_declaration": {
            "not_candidate_approval": True,
            "not_paper_live_authority": True,
            "not_runtime_authority": True,
            "not_promotion_authority": True,
            "not_trading_recommendation": True,
            "not_broker_exchange_authority": True,
            "not_capital_authority": True,
            "notes": "Pytest fixture event creates no authority.",
        },
    }


def _set_events(payload: dict, events: list[dict], candidate_status: str) -> None:
    payload["append_only_ledger"] = events
    candidate = payload["candidates"][0]
    candidate["candidate_status"] = candidate_status
    candidate["lifecycle_event_refs"] = [event["event_id"] for event in events]


def _rewrite_candidate_identity(payload: dict, candidate_id: str, event_prefix: str) -> None:
    candidate = payload["candidates"][0]
    old_candidate_id = candidate["candidate_id"]
    event_ids_by_old_id = {
        event["event_id"]: f"{event_prefix}-{event['event_sequence']:04d}"
        for event in payload["append_only_ledger"]
    }
    candidate["candidate_id"] = candidate_id
    candidate["lifecycle_event_refs"] = [
        event_ids_by_old_id[event_id] for event_id in candidate["lifecycle_event_refs"]
    ]
    for event in payload["append_only_ledger"]:
        event["candidate_id"] = candidate_id if event["candidate_id"] == old_candidate_id else event["candidate_id"]
        event["event_id"] = event_ids_by_old_id[event["event_id"]]


def test_candidate_lifecycle_registry_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_example_fixture_passes():
    errors = validate_candidate_registries()

    assert errors == []


def test_real_shaped_non_authoritative_registry_payload_passes(tmp_path):
    payload = _valid_registry()
    payload["registry_id"] = "CANDIDATE-REGISTRY-0001"
    payload["registry_status"] = "candidate_review"
    payload["validation_summary"]["fixture_only"] = False
    payload["validation_summary"]["real_candidate_registered"] = True
    payload["validation_summary"]["notes"] = "Temp real-shaped registry payload for validator coverage only."
    _rewrite_candidate_identity(payload, "CANDIDATE-0001", "CLE")
    payload["non_authority_declaration"]["notes"] = "Temp real-shaped registry creates no authority."
    payload["candidates"][0]["non_authority_declaration"]["notes"] = (
        "Temp real-shaped candidate record creates no approval or authority."
    )
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert errors == []


def test_real_unpopulated_registry_payload_passes(tmp_path):
    payload = _valid_registry()
    payload["registry_id"] = "CANDIDATE-REGISTRY-0002"
    payload["registry_status"] = "unpopulated"
    payload["candidates"] = []
    payload["append_only_ledger"] = []
    payload["validation_summary"]["fixture_only"] = False
    payload["validation_summary"]["real_candidate_registered"] = False
    payload["validation_summary"]["notes"] = "Temp empty real registry payload for validator coverage only."
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert errors == []


def test_fake_fixture_identifier_family_remains_allowed(tmp_path):
    payload = _valid_registry()
    payload["registry_id"] = "CANDIDATE-REGISTRY-FIXTURE-0001"
    payload["registry_status"] = "test_fixture"
    _rewrite_candidate_identity(payload, "CANDIDATE-FIXTURE-0001", "CLE-FIXTURE")
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert errors == []


def test_no_real_candidate_lifecycle_registry_artifact_committed():
    research_registry_dir = REPO_ROOT / "research" / "candidate_lifecycle_registry"
    committed_registry_artifacts = sorted(
        path
        for path in (REPO_ROOT / "research").rglob("*.candidate_lifecycle_registry.json")
        if "schemas" not in path.parts
    )

    assert not research_registry_dir.exists()
    assert committed_registry_artifacts == []


def test_invalid_state_rejected(tmp_path):
    payload = _valid_registry()
    payload["candidates"][0]["candidate_status"] = "paper_live_ready"
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert any("'paper_live_ready' is not one of" in error for error in errors)


def test_forbidden_transition_rejected(tmp_path):
    payload = _valid_registry()
    events = copy.deepcopy(payload["append_only_ledger"])
    events.append(
        _event(
            event_id="CLE-EXAMPLE-0003",
            event_sequence=3,
            event_type="promoted",
            timestamp_utc="2026-06-16T00:02:00Z",
            from_status="validated_research",
            to_status="promoted_live",
            related_evidence_links=[
                _evidence_ref("paper_shadow", "PAPER-SHADOW-EXAMPLE"),
                _evidence_ref("live_approval", "LIVE-APPROVAL-EXAMPLE"),
            ],
        )
    )
    _set_events(payload, events, "promoted_live")
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert any("forbidden transition validated_research->promoted_live" in error for error in errors)


def test_missing_rejection_evidence_link_rejected(tmp_path):
    payload = _valid_registry()
    events = copy.deepcopy(payload["append_only_ledger"])
    events.append(
        _event(
            event_id="CLE-EXAMPLE-0003",
            event_sequence=3,
            event_type="rejected",
            timestamp_utc="2026-06-16T00:02:00Z",
            from_status="validated_research",
            to_status="rejected",
            related_evidence_links=[],
        )
    )
    _set_events(payload, events, "rejected")
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert any("rejected event CLE-EXAMPLE-0003 requires evidence links" in error for error in errors)


def test_promotion_without_paper_live_evidence_rejected(tmp_path):
    payload = _valid_registry()
    events = [
        _event(
            event_id="CLE-EXAMPLE-0001",
            event_sequence=1,
            event_type="proposed",
            timestamp_utc="2026-06-16T00:00:00Z",
            from_status=None,
            to_status="proposed",
            related_evidence_links=[_evidence_ref("strategy_spec", "STRAT-SPEC-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0002",
            event_sequence=2,
            event_type="validated",
            timestamp_utc="2026-06-16T00:01:00Z",
            from_status="proposed",
            to_status="validated_research",
            related_evidence_links=[_evidence_ref("result_population", "RP-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0003",
            event_sequence=3,
            event_type="paper_candidate_approved",
            timestamp_utc="2026-06-16T00:02:00Z",
            from_status="validated_research",
            to_status="paper_candidate",
            related_evidence_links=[_evidence_ref("robustness_report", "ROBUSTNESS-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0004",
            event_sequence=4,
            event_type="paper_started",
            timestamp_utc="2026-06-16T00:03:00Z",
            from_status="paper_candidate",
            to_status="paper_running",
            related_evidence_links=[_evidence_ref("paper_shadow", "PAPER-SHADOW-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0005",
            event_sequence=5,
            event_type="promoted",
            timestamp_utc="2026-06-16T00:04:00Z",
            from_status="paper_running",
            to_status="promoted_live",
            related_evidence_links=[],
        ),
    ]
    _set_events(payload, events, "promoted_live")
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert any("requires paper_shadow evidence" in error for error in errors)
    assert any("requires live_approval evidence" in error for error in errors)


def test_terminal_rejected_and_promoted_conflict_rejected(tmp_path):
    payload = _valid_registry()
    events = [
        _event(
            event_id="CLE-EXAMPLE-0001",
            event_sequence=1,
            event_type="proposed",
            timestamp_utc="2026-06-16T00:00:00Z",
            from_status=None,
            to_status="proposed",
            related_evidence_links=[_evidence_ref("strategy_spec", "STRAT-SPEC-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0002",
            event_sequence=2,
            event_type="validated",
            timestamp_utc="2026-06-16T00:01:00Z",
            from_status="proposed",
            to_status="validated_research",
            related_evidence_links=[_evidence_ref("result_population", "RP-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0003",
            event_sequence=3,
            event_type="paper_candidate_approved",
            timestamp_utc="2026-06-16T00:02:00Z",
            from_status="validated_research",
            to_status="paper_candidate",
            related_evidence_links=[_evidence_ref("robustness_report", "ROBUSTNESS-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0004",
            event_sequence=4,
            event_type="paper_started",
            timestamp_utc="2026-06-16T00:03:00Z",
            from_status="paper_candidate",
            to_status="paper_running",
            related_evidence_links=[_evidence_ref("paper_shadow", "PAPER-SHADOW-EXAMPLE")],
        ),
        _event(
            event_id="CLE-EXAMPLE-0005",
            event_sequence=5,
            event_type="promoted",
            timestamp_utc="2026-06-16T00:04:00Z",
            from_status="paper_running",
            to_status="promoted_live",
            related_evidence_links=[
                _evidence_ref("paper_shadow", "PAPER-SHADOW-EXAMPLE"),
                _evidence_ref("live_approval", "LIVE-APPROVAL-EXAMPLE"),
            ],
        ),
        _event(
            event_id="CLE-EXAMPLE-0006",
            event_sequence=6,
            event_type="rejected",
            timestamp_utc="2026-06-16T00:05:00Z",
            from_status="promoted_live",
            to_status="rejected",
            related_evidence_links=[_evidence_ref("rejection_record", "REJECTION-EXAMPLE")],
        ),
    ]
    _set_events(payload, events, "promoted_live")
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert any("cannot be both rejected and promoted_live" in error for error in errors)


def test_forbidden_authority_flag_rejected(tmp_path):
    payload = _valid_registry()
    payload["non_authority_declaration"]["not_runtime_authority"] = False
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert any("True was expected" in error for error in errors)


def test_append_only_event_ordering_checked(tmp_path):
    payload = _valid_registry()
    payload["append_only_ledger"][1]["event_sequence"] = 3
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, payload)

    errors = validate_candidate_registries(registry_dir=registry_dir)

    assert any("expected 2" in error for error in errors)


def test_cli_module_invocation_works(tmp_path):
    registry_dir = tmp_path / "candidate_lifecycle_registry"
    _write_registry(registry_dir, _valid_registry())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.registry.validate_candidate_registry",
            "--registry-dir",
            str(registry_dir),
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: candidate lifecycle registry artifacts" in result.stdout
