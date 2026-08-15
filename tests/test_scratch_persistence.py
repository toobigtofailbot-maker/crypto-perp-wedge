import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from tools.canon_intake import scratch_persistence as persistence


REAL_RUN_ID = "RUN-20260804-H004R2A1"
CANONICAL_RP0007_RELATIVE_PATH = Path(
    "research/result_populations/RP-0007.result_population.json"
)
CANONICAL_RP0007_BYTE_LENGTH = 213_923
CANONICAL_RP0007_SHA256 = (
    "ff1104cebcb2775f3f64d2e5bec72b3aaaeeb4187740978e79a26a4819ee2308"
)


def _dispatch(
    *,
    scratch: str = "scratch/FIXTURE-RUN/dispatch/",
    provisional: str = "scratch/FIXTURE-RUN/dispatch/provisional_result.json",
) -> dict:
    return {
        "output_targets": {
            "scratch_run_directory": scratch,
            "provisional_result_paths": [provisional],
        }
    }


def _runner_output() -> dict:
    categories = ("successful", "failed", "invalid", "blocked", "insufficient", "withheld")
    rows = [
        {
            "row_id": f"RP-FIXTURE-ROW-{number:06d}",
            "variant_id": f"VAR-{number:06d}",
            "outcome_category": categories[(number - 1) % len(categories)],
            "score": number / 100,
        }
        for number in range(1, 82)
    ]
    counts = {category: 0 for category in categories}
    for row in rows:
        counts[row["outcome_category"]] += 1
    return {
        "ok": True,
        "aborted": False,
        "dry_run": True,
        "wrote": False,
        "output_path": None,
        "committed_denominator": 81,
        "outcome_category_counts": counts,
        "result_population": {
            "committed_denominator_snapshot": {
                "committed_denominator": 81,
                "result_row_count": 81,
                "outcome_counts_sum": 81,
            },
            "variant_result_rows": rows,
            "outcome_category_counts": counts,
        },
    }


def _assert_real_h004_boundary_preserved(
    repo_root: Path,
    *,
    expected_result_population: bytes | None = None,
) -> bytes:
    assert not (
        repo_root / f"research/queue/execution_events/{REAL_RUN_ID}.execution_events.jsonl"
    ).exists()
    assert not (repo_root / f"scratch/{REAL_RUN_ID}").exists()
    result_population_root = repo_root / "research/result_populations"
    result_population_path = repo_root / CANONICAL_RP0007_RELATIVE_PATH
    assert sorted(result_population_root.glob("RP-0007*")) == [
        result_population_path
    ]
    result_population = result_population_path.read_bytes()
    assert len(result_population) == CANONICAL_RP0007_BYTE_LENGTH
    assert (
        hashlib.sha256(result_population).hexdigest()
        == CANONICAL_RP0007_SHA256
    )
    if expected_result_population is not None:
        assert result_population == expected_result_population
    return result_population


@pytest.fixture(scope="session", autouse=True)
def real_h004_boundary_guard():
    repo_root = Path(__file__).resolve().parents[1]
    result_population_before = _assert_real_h004_boundary_preserved(repo_root)
    yield
    _assert_real_h004_boundary_preserved(
        repo_root,
        expected_result_population=result_population_before,
    )


def test_deterministic_serialization_roundtrips_complete_81_row_output():
    runner_output = _runner_output()

    first = persistence.serialize_provisional_result(runner_output)
    second = persistence.serialize_provisional_result(runner_output)

    assert first == second
    assert hashlib.sha256(first).digest() == hashlib.sha256(second).digest()
    assert json.loads(first) == runner_output
    decoded = json.loads(first)
    assert decoded["committed_denominator"] == 81
    rows = decoded["result_population"]["variant_result_rows"]
    assert len(rows) == 81
    assert sum(decoded["outcome_category_counts"].values()) == 81
    assert {row["outcome_category"] for row in rows} == {
        "successful",
        "failed",
        "invalid",
        "blocked",
        "insufficient",
        "withheld",
    }


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_json_is_rejected(value):
    with pytest.raises(persistence.ScratchPersistenceError, match="finite JSON"):
        persistence.serialize_provisional_result({"unsafe": value})


def test_persists_only_the_exact_dispatch_bound_noncanonical_target(tmp_path):
    runner_output = _runner_output()
    dispatch = _dispatch()

    evidence = persistence.persist_provisional_result(
        repo_root=tmp_path,
        dispatch=dispatch,
        runner_output=runner_output,
    )

    target = tmp_path / dispatch["output_targets"]["provisional_result_paths"][0]
    raw = target.read_bytes()
    assert json.loads(raw) == runner_output
    assert evidence == {
        "provisional_result_path": "scratch/FIXTURE-RUN/dispatch/provisional_result.json",
        "byte_length": len(raw),
        "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "serialization": "utf8_sorted_compact_json_with_final_lf_v1",
        "non_authority": {
            "non_canonical_scratch_only": True,
            "not_result_population_authority": True,
            "not_evidence_or_decision_authority": True,
            "not_runtime_paper_live_or_capital_authority": True,
        },
    }
    assert [path for path in tmp_path.rglob("*") if path.is_file()] == [target]
    assert not (tmp_path / "research/result_populations").exists()


@pytest.mark.parametrize(
    ("scratch", "provisional"),
    [
        ("C:/outside/", "C:/outside/provisional_result.json"),
        ("/outside/", "/outside/provisional_result.json"),
        ("scratch/../outside/", "scratch/../outside/provisional_result.json"),
        ("scratch/FIXTURE-RUN/./dispatch/", "scratch/FIXTURE-RUN/./dispatch/result.json"),
        ("research/result_populations/", "research/result_populations/RP-0007.json"),
        ("scratch/FIXTURE-RUN/dispatch/", "scratch/FIXTURE-RUN/other/result.json"),
        ("scratch\\FIXTURE-RUN\\dispatch\\", "scratch/FIXTURE-RUN/dispatch/result.json"),
    ],
)
def test_unsafe_or_unbound_paths_are_rejected_without_writes(
    tmp_path,
    scratch,
    provisional,
):
    with pytest.raises(persistence.ScratchPersistenceError):
        persistence.persist_provisional_result(
            repo_root=tmp_path,
            dispatch=_dispatch(scratch=scratch, provisional=provisional),
            runner_output=_runner_output(),
        )
    assert list(tmp_path.iterdir()) == []


def test_multiple_provisional_targets_are_rejected(tmp_path):
    dispatch = _dispatch()
    dispatch["output_targets"]["provisional_result_paths"].append(
        "scratch/FIXTURE-RUN/dispatch/second.json"
    )
    with pytest.raises(persistence.ScratchPersistenceError, match="exactly one"):
        persistence.preflight_provisional_result_target(
            repo_root=tmp_path,
            dispatch=dispatch,
        )


def test_existing_final_is_never_overwritten(tmp_path):
    target = tmp_path / "scratch/FIXTURE-RUN/dispatch/provisional_result.json"
    target.parent.mkdir(parents=True)
    original = b"retained original bytes\n"
    target.write_bytes(original)

    with pytest.raises(persistence.ScratchPersistenceError, match="overwrite is forbidden"):
        persistence.persist_provisional_result(
            repo_root=tmp_path,
            dispatch=_dispatch(),
            runner_output=_runner_output(),
        )

    assert target.read_bytes() == original


def test_partial_write_failure_is_visible_and_not_reported_as_success(tmp_path, monkeypatch):
    def fail_after_partial_write(fd: int, raw: bytes) -> None:
        os.write(fd, raw[:17])
        raise OSError("synthetic partial write")

    monkeypatch.setattr(persistence, "_write_all", fail_after_partial_write)
    with pytest.raises(persistence.ScratchPersistenceError, match="durability verification"):
        persistence.persist_provisional_result(
            repo_root=tmp_path,
            dispatch=_dispatch(),
            runner_output=_runner_output(),
        )
    assert not (tmp_path / "scratch/FIXTURE-RUN/dispatch/provisional_result.json").exists()


def _make_directory_redirect(path: Path, destination: Path) -> None:
    destination.mkdir()
    try:
        if os.name == "nt":
            subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(path), str(destination)],
                check=True,
                capture_output=True,
            )
        else:
            path.symlink_to(destination, target_is_directory=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        pytest.skip(f"directory redirect unavailable: {exc}")


def test_symlink_or_reparse_parent_is_rejected_without_redirection(tmp_path):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    redirected = scratch / "FIXTURE-RUN"
    outside = tmp_path / "outside"
    _make_directory_redirect(redirected, outside)

    with pytest.raises(persistence.ScratchPersistenceError, match="symlink or reparse"):
        persistence.persist_provisional_result(
            repo_root=tmp_path,
            dispatch=_dispatch(),
            runner_output=_runner_output(),
        )
    assert list(outside.iterdir()) == []
