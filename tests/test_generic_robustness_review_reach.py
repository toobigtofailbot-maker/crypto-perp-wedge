from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "scratch"
    / "WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01"
    / "generic_review_contract.json"
)
FAMILY_SUMMARY_PATH = (
    REPO_ROOT
    / "scratch"
    / "WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01"
    / "family_fixture_summary.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _examples() -> dict[str, dict]:
    payload = _load(CONTRACT_PATH)
    return {item["example_id"]: item for item in payload["examples"]}


def test_contract_examples_have_exclusive_created_no_packet_or_blocked_state() -> None:
    for example in _examples().values():
        created = example["candidate_review_packet_created"]
        no_packet = example["no_candidate_review_packet_reason"]
        blocked = example["blocked_review_reason"]

        assert not (no_packet and blocked)
        if created:
            assert no_packet is None
            assert blocked is None
        elif blocked is not None:
            assert no_packet is None
        else:
            assert no_packet is not None


def test_funding_no_go_produces_no_candidate_review_packet_reason() -> None:
    funding = _examples()["funding_rate_positioning_fade_no_go"]

    assert funding["strategy_family_label"] == "funding_rate_positioning_fade"
    assert funding["candidate_review_packet_created"] is False
    assert funding["blocked_review_reason"] is None
    assert funding["no_candidate_review_packet_reason"]["code"] == (
        "NO_GO_PRIMARY_RISK_SCREEN_FAILED"
    )
    assert "NO_GO_DRAWDOWN_SCREEN_FAILED" in funding[
        "candidate_review_eligibility_reason_codes"
    ]
    assert funding["denominator_manifest"]["planned"] == 36
    assert funding["denominator_manifest"]["completed"] == 36
    assert funding["denominator_manifest"]["denominator_preserved"] is True


def test_blocked_family_uses_blocked_review_reason_not_no_go() -> None:
    blocked = _examples()["donchian_oos_gate_blocked"]

    assert blocked["strategy_family_label"] == "donchian_breakout"
    assert blocked["candidate_review_packet_created"] is False
    assert blocked["no_candidate_review_packet_reason"] is None
    assert blocked["blocked_review_reason"]["code"] == "BLOCKED_OOS_GATE_UNAVAILABLE"
    assert "BLOCKED_RESULT_POPULATION_UNAVAILABLE" in blocked[
        "candidate_review_eligibility_reason_codes"
    ]


def test_unavailable_psr_dsr_mintrl_are_withheld_not_fabricated() -> None:
    funding = _examples()["funding_rate_positioning_fade_no_go"]

    assert funding["robustness_status"]["fabricated_inputs"] is False
    assert funding["robustness_status"]["withheld_stats"] == ["PSR", "DSR", "MinTRL"]
    assert {
        "UNAVAILABLE_PSR_MISSING_RETURN_SERIES",
        "UNAVAILABLE_DSR_MISSING_TRIAL_CONTEXT",
        "UNAVAILABLE_MINTRL_MISSING_METHOD_CONTRACT",
    }.issubset(set(funding["unavailable_stat_reason_codes"]))


def test_generic_metadata_supports_non_sma_families() -> None:
    summary = _load(FAMILY_SUMMARY_PATH)
    labels = {item["strategy_family_label"] for item in summary["families_observed"]}

    assert {"funding_rate_positioning_fade", "donchian_breakout", "sma_crossover"}.issubset(
        labels
    )
    assert summary["family_neutral_assertions"]["family_label_is_metadata_not_dispatch"] is True


def test_contract_creates_no_candidate_lifecycle_or_runtime_authority() -> None:
    payload = _load(CONTRACT_PATH)
    summary = _load(FAMILY_SUMMARY_PATH)

    assert payload["authority_boundary"]["candidate_lifecycle_write"] is False
    assert payload["authority_boundary"]["paper_live_runtime_authority"] is False
    assert payload["authority_boundary"]["ranking_or_recommendation_authority"] is False
    assert summary["family_neutral_assertions"]["candidate_lifecycle_write_created"] is False
    assert summary["family_neutral_assertions"]["paper_live_runtime_authority_created"] is False
