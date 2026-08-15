from pathlib import Path

from tools.research_memory.repo_source import load_repo_memory_seeds

FIXTURE_REPO = Path(__file__).parent / "fixtures" / "research_memory" / "repo"


def test_fixture_corpus_builds_deterministic_content_addressed_seeds() -> None:
    first = load_repo_memory_seeds(FIXTURE_REPO)
    second = load_repo_memory_seeds(FIXTURE_REPO)

    assert first == second
    assert [seed.source_key for seed in first] == ["H-901", "H-902"]
    negative = first[0]
    assert negative.classification == "NO-GO"
    assert negative.negative_reason is not None
    assert any(ref.evidence_role == "decision_record" for ref in negative.evidence)
    assert any(ref.evidence_role == "experiment_report" for ref in negative.evidence)
    assert all(len(ref.artifact_content_sha256) == 64 for ref in negative.evidence)
    assert not any("result_population" in ref.artifact_path for ref in negative.evidence)


def test_current_repo_seed_has_evidence_for_every_indexed_conclusion() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    seeds = load_repo_memory_seeds(repo_root)

    assert seeds
    for seed in seeds:
        if seed.classification == "PENDING":
            continue
        assert any(ref.supports_conclusion for ref in seed.evidence), seed.source_key
        assert any(ref.evidence_role == "decision_record" for ref in seed.evidence), seed.source_key
