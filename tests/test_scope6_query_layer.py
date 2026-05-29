import json
from pathlib import Path

import pytest

import tools.research_query.query_layer as query_layer
from tools.research_query.query_layer import init_duckdb, list_views, run_named_view


SCOPE6_VIEWS = {
    "v_r2s_approval_records",
    "v_shadow_evidence_retention",
    "v_s2p_approval_records",
    "v_scope6_candidate_packaging_overview",
    "v_s2p_shadow_evidence_links",
    "v_integrity_r2s_approval_candidate_refs",
    "v_integrity_shadow_evidence_candidate_refs",
    "v_integrity_s2p_approval_candidate_refs",
    "v_integrity_r2s_rec5_candidate_consistency",
    "v_integrity_s2p_shadow_evidence_refs",
    "v_integrity_s2p_shadow_evidence_candidate_consistency",
    "v_integrity_scope6_authority_flags",
    "v_integrity_scope6_preservation_flags",
}

SCOPE6_INTEGRITY_VIEWS = {
    view_name
    for view_name in SCOPE6_VIEWS
    if view_name.startswith(
        (
            "v_integrity_scope6",
            "v_integrity_r2s",
            "v_integrity_s2p",
            "v_integrity_shadow_evidence",
        )
    )
}


def _artifact_ref(label: str = "REP-9000") -> dict:
    return {
        "artifact_id_or_label": label,
        "artifact_path": f"research/fixtures/{label}.json",
    }


def _r2s_payload(approval_record_id: str = "R2S-AR-0001", candidate_id: str = "H-001") -> dict:
    return {
        "schema_version": "v1",
        "record_type": "research_to_shadow_approval_record",
        "approval_record_id": approval_record_id,
        "candidate_id": candidate_id,
        "strategy_or_candidate_family": "momentum",
        "evidence_snapshot_references": [_artifact_ref("REP-0001")],
        "d2_006_gate_pass_evidence_reference_or_attestation": _artifact_ref("D2-006-attestation"),
        "rec5_exact_segment_evidence": {
            "candidate_id": candidate_id,
            "outcome_kind": "research_oos",
            "pipeline_version": "pre_wp_5b",
            "expectation_source_type": "d2_006_gates",
            "evidence_references": [_artifact_ref("REC-0001")],
            "no_pooled_or_cross_segment_inference_below_floor": True,
        },
        "no_cross_segment_inference_below_rec5_floor": True,
        "approver_identity": "human-reviewer",
        "approval_timestamp_utc": "2026-05-29T12:00:00Z",
        "decision_outcome": "approved",
        "preservation_confirmation": {
            "permanent_human_gates_preserved": True,
            "d2_006_preserved": True,
            "d2_007_preserved": True,
            "rec5_preserved": True,
            "phase9_preserved": True,
        },
        "transition_machinery_statement": (
            "This record is required before any future research-to-shadow transition, but it does not "
            "implement transition machinery or authorize transition execution."
        ),
        "authority_flags": {
            "candidate_readiness_authority": False,
            "transition_authority": False,
            "promotion_authority": False,
            "gate_execution_authority": False,
            "runtime_authority": False,
            "tier4_authority": False,
        },
    }


def _shadow_evidence_payload(shadow_evidence_id: str = "SER-0001", candidate_id: str = "H-001") -> dict:
    return {
        "schema_version": "v1",
        "record_type": "shadow_evidence_retention",
        "shadow_evidence_id": shadow_evidence_id,
        "candidate_id": candidate_id,
        "shadow_window": {
            "start_utc": "2026-05-01T00:00:00Z",
            "end_utc": "2026-05-15T00:00:00Z",
            "calendar_days_observed": 14,
        },
        "d2_007_thresholds": {
            "minimum_shadow_window_calendar_days": 14,
            "pnl_deviation_max": 0.1,
            "trade_count_deviation_max": 0.05,
        },
        "parity_result": {
            "observed_pnl_deviation": 0.03,
            "observed_trade_count_deviation": 0.02,
            "parity_result_evidence_reference_or_attestation": _artifact_ref("parity-attestation"),
        },
        "shadow_observation_lineage": [_artifact_ref("shadow-lineage")],
        "disclosure": {
            "interruptions": [],
            "invalid_observations": [],
            "missing_data": [],
            "observation_resets": [],
        },
        "evidence_retention_reference": _artifact_ref("retained-evidence"),
        "mismatch_diagnostics": {
            "decision_support_only": True,
            "ranking_authority": False,
            "scoring_authority": False,
            "recommendation_authority": False,
            "transition_logic_authority": False,
            "diagnostic_references": [],
        },
        "authority_flags": {
            "candidate_readiness_authority": False,
            "transition_authority": False,
            "ranking_authority": False,
            "scoring_authority": False,
            "recommendation_authority": False,
            "gate_execution_authority": False,
            "runtime_authority": False,
            "tier4_authority": False,
        },
    }


def _s2p_payload(
    approval_record_id: str = "S2P-AR-0001",
    candidate_id: str = "H-001",
    shadow_evidence_id: str = "SER-0001",
) -> dict:
    return {
        "schema_version": "v1",
        "record_type": "shadow_to_paper_approval_record",
        "approval_record_id": approval_record_id,
        "candidate_id": candidate_id,
        "shadow_window_evidence_reference": {
            "shadow_evidence_id": shadow_evidence_id,
            "artifact_path": f"research/shadow_evidence_retention/{shadow_evidence_id}.shadow_evidence_retention.json",
        },
        "d2_007_parity_result_reference_or_attestation": _artifact_ref("d2-007-attestation"),
        "interruption_or_invalid_observation_disclosure_reference": _artifact_ref("disclosure-attestation"),
        "paper_runtime_protection_confirmation": True,
        "approver_identity": "human-reviewer",
        "approval_timestamp_utc": "2026-05-29T12:00:00Z",
        "decision_outcome": "approved",
        "preservation_confirmation": {
            "permanent_human_gates_preserved": True,
            "d2_007_preserved": True,
            "phase1_paper_runtime_protection_preserved": True,
            "tier4_boundaries_preserved": True,
        },
        "transition_machinery_statement": (
            "This record is required before any future shadow-to-paper transition, but it does not "
            "implement transition machinery, invoke paper runtime, or authorize transition execution."
        ),
        "authority_flags": {
            "candidate_readiness_authority": False,
            "transition_authority": False,
            "promotion_authority": False,
            "gate_execution_authority": False,
            "paper_runtime_authority": False,
            "runtime_authority": False,
            "tier4_authority": False,
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _patch_scope6_dirs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(query_layer, "R2S_APPROVAL_RECORDS_DIR", tmp_path / "research" / "r2s_approval_records")
    monkeypatch.setattr(
        query_layer,
        "SHADOW_EVIDENCE_RETENTION_DIR",
        tmp_path / "research" / "shadow_evidence_retention",
    )
    monkeypatch.setattr(query_layer, "S2P_APPROVAL_RECORDS_DIR", tmp_path / "research" / "s2p_approval_records")


def _scope6_conn(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    _patch_scope6_dirs(monkeypatch, tmp_path)
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_scope6_init_succeeds_when_directories_are_absent(monkeypatch, tmp_path):
    _patch_scope6_dirs(monkeypatch, tmp_path)

    connection = init_duckdb()
    try:
        assert set(list_views(connection)) >= SCOPE6_VIEWS
    finally:
        connection.close()


def test_scope6_views_are_listed_in_current_repo_state():
    connection = init_duckdb()
    try:
        assert SCOPE6_VIEWS <= set(list_views(connection))
    finally:
        connection.close()


def test_scope6_zero_instance_views_are_empty_except_inventory():
    connection = init_duckdb()
    try:
        for view_name in SCOPE6_VIEWS - {"v_scope6_candidate_packaging_overview"}:
            assert run_named_view(connection, view_name) == []

        inventory_rows = run_named_view(connection, "v_scope6_candidate_packaging_overview")
        assert inventory_rows
        assert all(row["r2s_approval_record_count"] == 0 for row in inventory_rows)
        assert all(row["shadow_evidence_retention_count"] == 0 for row in inventory_rows)
        assert all(row["s2p_approval_record_count"] == 0 for row in inventory_rows)
    finally:
        connection.close()


def test_scope6_integrity_views_are_empty_in_current_repo_state():
    connection = init_duckdb()
    try:
        for view_name in SCOPE6_INTEGRITY_VIEWS:
            assert run_named_view(connection, view_name) == []
    finally:
        connection.close()


def test_scope6_base_views_load_valid_temp_fixtures(monkeypatch, tmp_path):
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        _r2s_payload(),
    )
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        _shadow_evidence_payload(),
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        _s2p_payload(),
    )

    for connection in _scope6_conn(monkeypatch, tmp_path):
        r2s_rows = run_named_view(connection, "v_r2s_approval_records")
        shadow_rows = run_named_view(connection, "v_shadow_evidence_retention")
        s2p_rows = run_named_view(connection, "v_s2p_approval_records")

        assert r2s_rows[0]["approval_record_id"] == "R2S-AR-0001"
        assert r2s_rows[0]["rec5_candidate_id"] == "H-001"
        assert shadow_rows[0]["shadow_evidence_id"] == "SER-0001"
        assert shadow_rows[0]["calendar_days_observed"] == 14
        assert s2p_rows[0]["approval_record_id"] == "S2P-AR-0001"
        assert s2p_rows[0]["referenced_shadow_evidence_id"] == "SER-0001"


def test_s2p_shadow_evidence_links_join_referenced_shadow_evidence(monkeypatch, tmp_path):
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        _shadow_evidence_payload(),
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        _s2p_payload(),
    )

    for connection in _scope6_conn(monkeypatch, tmp_path):
        rows = run_named_view(connection, "v_s2p_shadow_evidence_links")

        assert rows == [
            {
                "s2p_approval_record_id": "S2P-AR-0001",
                "s2p_candidate_id": "H-001",
                "referenced_shadow_evidence_id": "SER-0001",
                "shadow_evidence_id": "SER-0001",
                "shadow_evidence_candidate_id": "H-001",
                "candidate_id_match": True,
            }
        ]


def test_scope6_candidate_packaging_overview_is_inventory_only(monkeypatch, tmp_path):
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        _r2s_payload(),
    )

    for connection in _scope6_conn(monkeypatch, tmp_path):
        cursor = connection.execute("SELECT * FROM v_scope6_candidate_packaging_overview LIMIT 0")
        columns = {description[0] for description in cursor.description}
        h001_row = connection.execute(
            """
            SELECT *
            FROM v_scope6_candidate_packaging_overview
            WHERE candidate_id = 'H-001'
            """
        ).fetchone()

        assert h001_row is not None
        assert not any("readiness" in column for column in columns)
        assert not any("transition" in column for column in columns)
        assert not any("rank" in column or "score" in column for column in columns)


def test_invalid_candidate_refs_surface_in_scope6_integrity_views(monkeypatch, tmp_path):
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        _r2s_payload(candidate_id="H-999"),
    )
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        _shadow_evidence_payload(candidate_id="H-999"),
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        _s2p_payload(candidate_id="H-999"),
    )

    for connection in _scope6_conn(monkeypatch, tmp_path):
        assert run_named_view(connection, "v_integrity_r2s_approval_candidate_refs")
        assert run_named_view(connection, "v_integrity_shadow_evidence_candidate_refs")
        assert run_named_view(connection, "v_integrity_s2p_approval_candidate_refs")


def test_r2s_rec5_candidate_mismatch_surfaces_in_integrity_view(monkeypatch, tmp_path):
    payload = _r2s_payload(candidate_id="H-001")
    payload["rec5_exact_segment_evidence"]["candidate_id"] = "H-002"
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        payload,
    )

    for connection in _scope6_conn(monkeypatch, tmp_path):
        rows = run_named_view(connection, "v_integrity_r2s_rec5_candidate_consistency")

        assert rows[0]["issue_type"] == "r2s_rec5_candidate_mismatch"
        assert rows[0]["candidate_id"] == "H-001"
        assert rows[0]["rec5_candidate_id"] == "H-002"


def test_s2p_missing_or_mismatched_shadow_evidence_refs_surface(monkeypatch, tmp_path):
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        _s2p_payload(approval_record_id="S2P-AR-0001", candidate_id="H-001", shadow_evidence_id="SER-9999"),
    )
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0002.shadow_evidence_retention.json",
        _shadow_evidence_payload(shadow_evidence_id="SER-0002", candidate_id="H-002"),
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0002.s2p_approval_record.json",
        _s2p_payload(approval_record_id="S2P-AR-0002", candidate_id="H-001", shadow_evidence_id="SER-0002"),
    )

    for connection in _scope6_conn(monkeypatch, tmp_path):
        missing_rows = run_named_view(connection, "v_integrity_s2p_shadow_evidence_refs")
        mismatch_rows = run_named_view(connection, "v_integrity_s2p_shadow_evidence_candidate_consistency")

        assert missing_rows[0]["referenced_shadow_evidence_id"] == "SER-9999"
        assert mismatch_rows[0]["referenced_shadow_evidence_id"] == "SER-0002"
        assert mismatch_rows[0]["shadow_evidence_candidate_id"] == "H-002"


def test_invalid_authority_or_preservation_flags_surface(monkeypatch, tmp_path):
    r2s_payload = _r2s_payload()
    r2s_payload["authority_flags"]["transition_authority"] = True
    shadow_payload = _shadow_evidence_payload()
    shadow_payload["d2_007_thresholds"]["minimum_shadow_window_calendar_days"] = 13
    s2p_payload = _s2p_payload()
    s2p_payload["paper_runtime_protection_confirmation"] = False

    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        r2s_payload,
    )
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        shadow_payload,
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        s2p_payload,
    )

    for connection in _scope6_conn(monkeypatch, tmp_path):
        authority_rows = run_named_view(connection, "v_integrity_scope6_authority_flags")
        preservation_rows = run_named_view(connection, "v_integrity_scope6_preservation_flags")

        assert any(row["source_field"] == "authority_flags.transition_authority" for row in authority_rows)
        assert any(
            row["source_field"] == "d2_007_thresholds.minimum_shadow_window_calendar_days"
            for row in preservation_rows
        )
        assert any(row["source_field"] == "paper_runtime_protection_confirmation" for row in preservation_rows)


def test_scope6_query_layer_does_not_create_committed_scope6_artifact_directories():
    connection = init_duckdb()
    try:
        for view_name in SCOPE6_VIEWS:
            run_named_view(connection, view_name)
    finally:
        connection.close()

    assert not query_layer.R2S_APPROVAL_RECORDS_DIR.exists()
    assert not query_layer.SHADOW_EVIDENCE_RETENTION_DIR.exists()
    assert not query_layer.S2P_APPROVAL_RECORDS_DIR.exists()
