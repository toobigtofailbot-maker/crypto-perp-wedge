import json
import subprocess
from pathlib import Path

import pytest

from tools.dev import diff_scope_summary as helper


REQUIRED_KEYS = {
    "tracked_changed_files",
    "staged_changed_files",
    "untracked_files",
    "numstat",
    "forbidden_matches",
    "authorized_canonical_result_population_writes",
    "authorized_path_writes",
    "allowed_file_violations",
    "trial_log",
    "exit_reason",
}

LINEAGE_SCOPE = "research-data-slice-lineage"
LINEAGE_PACKAGE = "WP-FT-01-TEST"
LINEAGE_REJECTION_REASON = (
    "research-data-slice-lineage scope requires an exact four-component "
    "research/data_slices/<dataset_family>/<artifact_filename> path with "
    "a lowercase dataset family and a .catalog_slice.json, "
    ".validation_report.json, or .derivation_report.json artifact"
)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")
    _write(repo / "README.md", "initial\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    return repo


def _run(args: list[str], capsys) -> tuple[int, str, str]:
    exit_code = helper.run(args)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_markdown_output_succeeds_inside_temp_git_repo(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, stderr = _run(["--repo-root", str(repo)], capsys)

    assert exit_code == 0
    assert stderr == ""
    assert "# Diff / Scope Summary" in stdout
    assert "## Tracked changed files" in stdout
    assert "Advisory only" in stdout


def test_json_output_includes_required_keys(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert set(payload) == REQUIRED_KEYS


def test_untracked_file_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "notes.md", "draft\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["untracked_files"] == ["notes.md"]


def test_tracked_changed_file_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "changed\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["tracked_changed_files"] == ["README.md"]


def test_staged_changed_file_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "staged\n")
    _git(repo, "add", "README.md")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["staged_changed_files"] == ["README.md"]


def test_forbidden_prefix_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "src" / "runtime.py", "changed\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["forbidden_matches"] == [{"path": "src/runtime.py", "prefix": "src/"}]


def test_check_forbidden_exits_nonzero_on_forbidden_match(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "research" / "note.md", "changed\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--check-forbidden"], capsys)

    assert exit_code == 1
    assert json.loads(stdout)["exit_reason"] == "forbidden path match"


def test_unauthorized_result_population_write_is_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--check-forbidden"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_new_result_population_write_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-canonical-result-population-write",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_canonical_result_population_writes"]["package"] == "WP-TEST"
    assert payload["authorized_canonical_result_population_writes"]["authorized"][0]["path"] == path


def test_authorized_schema_path_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["package"] == "WP-TEST"
    assert payload["authorized_path_writes"]["scope"] == "strategy-spec-schema"
    assert payload["authorized_path_writes"]["authorized"] == [
        {"path": path, "status": "authorized", "scope": "strategy-spec-schema"}
    ]


def test_online_ohlcv_schema_regression_authorized_path_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01",
            "--authorized-scope",
            "strategy-spec-schema",
            "--authorized-path",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["package"] == "WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01"


@pytest.mark.parametrize(
    "path",
    [
        "research/schemas/research_feature_table_manifest.schema.json",
        (
            "research/data_feature_availability/"
            "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
        ),
    ],
)
def test_research_data_feature_expansion_accepts_exact_changed_family_path(
    tmp_path, capsys, path
):
    repo = _repo(tmp_path)
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "CPW-RESEARCH-02-CONTINUATION-01",
            "--authorized-scope",
            "research-data-feature-expansion",
            "--authorized-path",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["authorized"] == [
        {
            "path": path,
            "status": "authorized",
            "scope": "research-data-feature-expansion",
        }
    ]


def test_research_data_feature_expansion_accepts_both_exact_paths_together(tmp_path, capsys):
    repo = _repo(tmp_path)
    paths = [
        "research/schemas/research_feature_table_manifest.schema.json",
        (
            "research/data_feature_availability/"
            "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
        ),
    ]
    for path in paths:
        _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "CPW-RESEARCH-02-CONTINUATION-01",
            "--authorized-scope",
            "research-data-feature-expansion",
            "--authorized-path",
            paths[0],
            "--authorized-path",
            paths[1],
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert [item["path"] for item in payload["authorized_path_writes"]["authorized"]] == paths


def test_research_data_feature_expansion_leaves_additional_research_path_forbidden(
    tmp_path, capsys
):
    repo = _repo(tmp_path)
    schema_path = "research/schemas/research_feature_table_manifest.schema.json"
    strategy_path = "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    _write(repo / schema_path, "{}\n")
    _write(repo / strategy_path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "CPW-RESEARCH-02-CONTINUATION-01",
            "--authorized-scope",
            "research-data-feature-expansion",
            "--authorized-path",
            schema_path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == schema_path
    assert payload["forbidden_matches"] == [{"path": strategy_path, "prefix": "research/"}]


@pytest.mark.parametrize(
    ("path", "prefix"),
    [
        ("research/result_populations/RP-9001.result_population.json", "research/"),
        ("lib/backtest.py", "lib/"),
    ],
)
def test_research_data_feature_expansion_rejects_exact_path_outside_families(
    tmp_path, capsys, path, prefix
):
    repo = _repo(tmp_path)
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "CPW-RESEARCH-02-CONTINUATION-01",
            "--authorized-scope",
            "research-data-feature-expansion",
            "--authorized-path",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "research-data-feature-expansion",
            "reason": (
                "research-data-feature-expansion scope requires an exact "
                "research/schemas/*.schema.json or "
                "research/data_feature_availability/*.json path"
            ),
        }
    ]
    assert payload["forbidden_matches"] == [{"path": path, "prefix": prefix}]


def test_research_data_feature_expansion_does_not_authorize_omitted_family_path(
    tmp_path, capsys
):
    repo = _repo(tmp_path)
    schema_path = "research/schemas/research_feature_table_manifest.schema.json"
    availability_path = (
        "research/data_feature_availability/"
        "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
    )
    _write(repo / schema_path, "{}\n")
    _write(repo / availability_path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "CPW-RESEARCH-02-CONTINUATION-01",
            "--authorized-scope",
            "research-data-feature-expansion",
            "--authorized-path",
            schema_path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == schema_path
    assert payload["forbidden_matches"] == [
        {"path": availability_path, "prefix": "research/"}
    ]


@pytest.mark.parametrize(
    "path",
    [
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/"
            "binance_usdtm_btcusdt_30m_20200101_20260411.catalog_slice.json"
        ),
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/"
            "binance_usdtm_btcusdt_30m_20200101_20260411.validation_report.json"
        ),
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/"
            "binance_usdtm_btcusdt_30m_20200101_20260411.derivation_report.json"
        ),
        (
            "research/data_slices/binance_usdtm_btcusdt_1h/"
            "binance_usdtm_btcusdt_1h_20200101_20260411.catalog_slice.json"
        ),
    ],
)
def test_research_data_slice_lineage_accepts_exact_changed_lineage_path(
    tmp_path, capsys, path
):
    repo = _repo(tmp_path)
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            LINEAGE_PACKAGE,
            "--authorized-scope",
            LINEAGE_SCOPE,
            "--authorized-path",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["authorized"] == [
        {"path": path, "status": "authorized", "scope": LINEAGE_SCOPE}
    ]


def test_research_data_slice_lineage_accepts_multiple_exact_paths_independently(
    tmp_path, capsys
):
    repo = _repo(tmp_path)
    paths = [
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/"
            "binance_usdtm_btcusdt_30m_20200101_20260411.catalog_slice.json"
        ),
        (
            "research/data_slices/binance_usdtm_btcusdt_1h/"
            "binance_usdtm_btcusdt_1h_20200101_20260411.validation_report.json"
        ),
    ]
    for path in paths:
        _write(repo / path, "{}\n")

    args = [
        "--repo-root",
        str(repo),
        "--json",
        "--check-forbidden",
        "--authorized-package",
        LINEAGE_PACKAGE,
        "--authorized-scope",
        LINEAGE_SCOPE,
    ]
    for path in paths:
        args.extend(["--authorized-path", path])

    exit_code, stdout, _ = _run(args, capsys)

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert [
        item["path"] for item in payload["authorized_path_writes"]["authorized"]
    ] == paths


def test_research_data_slice_lineage_leaves_omitted_changed_sibling_forbidden(
    tmp_path, capsys
):
    repo = _repo(tmp_path)
    authorized_path = (
        "research/data_slices/binance_usdtm_btcusdt_30m/"
        "slice.catalog_slice.json"
    )
    omitted_path = (
        "research/data_slices/binance_usdtm_btcusdt_30m/"
        "slice.validation_report.json"
    )
    _write(repo / authorized_path, "{}\n")
    _write(repo / omitted_path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            LINEAGE_PACKAGE,
            "--authorized-scope",
            LINEAGE_SCOPE,
            "--authorized-path",
            authorized_path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == authorized_path
    assert payload["forbidden_matches"] == [
        {"path": omitted_path, "prefix": "research/"}
    ]


@pytest.mark.parametrize(
    ("path", "forbidden_prefix"),
    [
        ("research/data_slices/binance_usdtm_btcusdt_30m/arbitrary.json", "research/"),
        ("research/data_slices/binance_usdtm_btcusdt_30m/data.csv", "research/"),
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/"
            "foo.bar.catalog_slice.json",
            "research/",
        ),
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/"
            "NONLOWER.catalog_slice.json",
            "research/",
        ),
        ("research/data_slices/binance.usdtm/foo.catalog_slice.json", "research/"),
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/nested/"
            "x.catalog_slice.json",
            "research/",
        ),
        (
            "research/data_slices/binance_usdtm_btcusdt_30m/"
            "foo.catalog_slice.json.bak",
            "research/",
        ),
        ("research/result_populations/RP-9001.result_population.json", "research/"),
        ("research/schemas/research_feature_table_manifest.schema.json", "research/"),
        ("lib/backtest.py", "lib/"),
        ("tools/research_runner/run_offline_sweep.py", None),
    ],
)
def test_research_data_slice_lineage_rejects_out_of_grammar_exact_changed_path(
    tmp_path, capsys, path, forbidden_prefix
):
    repo = _repo(tmp_path)
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            LINEAGE_PACKAGE,
            "--authorized-scope",
            LINEAGE_SCOPE,
            "--authorized-path",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"] == []
    assert payload["authorized_path_writes"]["rejected"] == [
        {"path": path, "scope": LINEAGE_SCOPE, "reason": LINEAGE_REJECTION_REASON}
    ]
    expected_forbidden = (
        [{"path": path, "prefix": forbidden_prefix}] if forbidden_prefix else []
    )
    assert payload["forbidden_matches"] == expected_forbidden


@pytest.mark.parametrize(
    "path",
    [
        "research/data_slices/./x.catalog_slice.json",
        "research/data_slices/../x.catalog_slice.json",
        "research/data_slices/Binance_usdtm/x.catalog_slice.json",
        "research/data_slices//x.catalog_slice.json",
        "research/data_slices/binance usdtm/x.catalog_slice.json",
        "research/data_slices/binance+usdtm/x.catalog_slice.json",
        "research/data_slices/binance:usdtm/x.catalog_slice.json",
        "research/data_slices/binance%usdtm/x.catalog_slice.json",
        "research/data_slices/binance_usdtm/Foo.catalog_slice.json",
        "research/data_slices/binance_usdtm/foo bar.catalog_slice.json",
        "research/data_slices/binance_usdtm/foo+bar.catalog_slice.json",
        "research/data_slices/binance_usdtm/foo:bar.catalog_slice.json",
        "research/data_slices/binance_usdtm/foo%bar.catalog_slice.json",
        "research/data_slices/binance_usdtm/../x.catalog_slice.json",
    ],
)
def test_research_data_slice_lineage_component_grammar_rejects_invalid_path(path):
    assert helper._authorized_path_scope_rejection(path, LINEAGE_SCOPE) == (
        LINEAGE_REJECTION_REASON
    )


def test_research_data_slice_lineage_normalized_backslash_path_uses_same_grammar():
    raw_path = (
        "research\\data_slices\\binance_usdtm_btcusdt_30m\\"
        "slice.catalog_slice.json"
    )
    normalized_path = helper._normalize_path(raw_path)

    assert normalized_path == (
        "research/data_slices/binance_usdtm_btcusdt_30m/"
        "slice.catalog_slice.json"
    )
    assert helper._authorized_path_scope_rejection(normalized_path, LINEAGE_SCOPE) is None


def test_research_data_slice_lineage_authorized_path_must_be_changed(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = (
        "research/data_slices/binance_usdtm_btcusdt_30m/"
        "slice.catalog_slice.json"
    )

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            LINEAGE_PACKAGE,
            "--authorized-scope",
            LINEAGE_SCOPE,
            "--authorized-path",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"] == []
    assert payload["authorized_path_writes"]["rejected"] == [
        {"path": path, "scope": LINEAGE_SCOPE, "reason": "path not changed"}
    ]
    assert payload["forbidden_matches"] == []


def test_unauthorized_schema_path_remains_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--check-forbidden"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_scope_requires_exact_changed_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    changed_path = "research/schemas/strategy_spec.schema.json"
    authorized_path = "research/schemas/candidate_registry.schema.json"
    _write(repo / changed_path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            authorized_path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {"path": authorized_path, "scope": "strategy-spec-schema", "reason": "path not changed"}
    ]
    assert payload["forbidden_matches"] == [{"path": changed_path, "prefix": "research/"}]


def test_authorized_schema_path_does_not_allow_different_schema_file(tmp_path, capsys):
    repo = _repo(tmp_path)
    authorized_path = "research/schemas/strategy_spec.schema.json"
    other_schema_path = "research/schemas/result_population.schema.json"
    _write(repo / authorized_path, "{}\n")
    _write(repo / other_schema_path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            authorized_path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == authorized_path
    assert payload["forbidden_matches"] == [{"path": other_schema_path, "prefix": "research/"}]


def test_authorized_schema_scope_does_not_allow_lib_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "lib/backtest.py"
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "strategy-spec-schema",
            "reason": "scope requires an exact research/schemas/*.schema.json path",
        }
    ]
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "lib/"}]


def test_authorized_compiler_path_records_evidence(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "tools/research_runner/spec_signal_compiler.py"
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "research-compiler",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["authorized_path_writes"]["authorized"] == [
        {"path": path, "status": "authorized", "scope": "research-compiler"}
    ]


def test_compiler_scope_rejects_noncompiler_exact_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "research-compiler",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "research-compiler",
            "reason": "compiler scope is limited to tools/research_runner/spec_signal_compiler.py",
        }
    ]
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_strategy_spec_path_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-prereg",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["authorized"] == [
        {"path": path, "status": "authorized", "scope": "strategy-spec-prereg"}
    ]


def test_authorized_strategy_spec_scope_does_not_allow_result_population(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-prereg",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "strategy-spec-prereg",
            "reason": "strategy-spec scope is limited to research/strategy_specs/STRAT-SPEC-<digits>.strategy_spec.json",
        }
    ]
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_mode_does_not_allow_runtime_or_lib_changes(tmp_path, capsys):
    repo = _repo(tmp_path)
    rp_path = "research/result_populations/RP-9001.result_population.json"
    lib_path = "lib/backtest.py"
    _write(repo / rp_path, "{}\n")
    _write(repo / lib_path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-canonical-result-population-write",
            rp_path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": lib_path, "prefix": "lib/"}]


def test_authorized_mode_does_not_allow_existing_result_population_mutation(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")
    _git(repo, "add", path)
    _git(repo, "commit", "-m", "add rp")
    _write(repo / path, '{"changed": true}\n')

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-canonical-result-population-write",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]
    assert payload["authorized_canonical_result_population_writes"]["rejected"] == [
        {"path": path, "reason": "path exists in HEAD; existing RP mutation is not authorized"}
    ]


def test_mixed_authorized_rp_plus_unauthorized_protected_file_fails(tmp_path, capsys):
    repo = _repo(tmp_path)
    rp_path = "research/result_populations/RP-9001.result_population.json"
    runtime_path = "src/runtime/paper_trader.py"
    _write(repo / rp_path, "{}\n")
    _write(repo / runtime_path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-canonical-result-population-write",
            rp_path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_canonical_result_population_writes"]["authorized"][0]["path"] == rp_path
    assert payload["forbidden_matches"] == [{"path": runtime_path, "prefix": "src/"}]


def test_mixed_authorized_schema_plus_unauthorized_research_file_fails(tmp_path, capsys):
    repo = _repo(tmp_path)
    schema_path = "research/schemas/strategy_spec.schema.json"
    note_path = "research/notes/unapproved.md"
    _write(repo / schema_path, "{}\n")
    _write(repo / note_path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            schema_path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == schema_path
    assert payload["forbidden_matches"] == [{"path": note_path, "prefix": "research/"}]


@pytest.mark.parametrize(
    "path",
    [
        "research/queue/dispatch_authorizations/KDAUTH-H004-R2-9001.dispatch_authorization.json",
        "research/queue/dispatch_authorization_audit/dispatch_authorization_events.jsonl",
        (
            "research/queue/dispatch_authorization_reservations/"
            "KDAUTH-XING-20260805-TEST0001.crossing_reservation.jsonl"
        ),
        "research/queue/dispatch_records/DSP-20260804-H004R2A1.dispatch_record.json",
        "tests/test_dispatch_authorization.py",
        "docs/project_status.md",
    ],
)
def test_dispatch_authorization_crossing_scope_accepts_only_exact_changed_paths(
    tmp_path, capsys, path
):
    repo = _repo(tmp_path)
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "dispatch-authorization-crossing",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["authorized"] == [
        {
            "path": path,
            "status": "authorized",
            "scope": "dispatch-authorization-crossing",
        }
    ]


@pytest.mark.parametrize(
    "path",
    [
        "research/queue/unrelated/UNRELATED-20260805.json",
        "tests/test_dispatch_writer.py",
        "docs/status_entries/WP-TEST.md",
    ],
)
def test_dispatch_authorization_crossing_scope_rejects_paths_outside_bounded_families(
    tmp_path, capsys, path
):
    repo = _repo(tmp_path)
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "dispatch-authorization-crossing",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"] == []
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "dispatch-authorization-crossing",
            "reason": (
                "dispatch-authorization-crossing scope is limited to the canonical dispatch record, "
                "authorization, lifecycle audit, crossing reservation, dispatch-authorization "
                "regression test, and project-status path families"
            ),
        }
    ]


def test_dispatch_authorization_crossing_scope_does_not_authorize_omitted_canonical_path(
    tmp_path, capsys
):
    repo = _repo(tmp_path)
    authorized_path = (
        "research/queue/dispatch_authorizations/"
        "KDAUTH-H004-R2-9001.dispatch_authorization.json"
    )
    omitted_path = (
        "research/queue/dispatch_authorization_reservations/"
        "KDAUTH-XING-20260805-TEST0001.crossing_reservation.jsonl"
    )
    _write(repo / authorized_path, "{}\n")
    _write(repo / omitted_path, "event\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            authorized_path,
            "--authorized-scope",
            "dispatch-authorization-crossing",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == authorized_path
    assert payload["forbidden_matches"] == [{"path": omitted_path, "prefix": "research/"}]


def test_dispatch_authorization_crossing_scope_alone_authorizes_nothing(tmp_path, capsys):
    repo = _repo(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        helper.run(
            [
                "--repo-root",
                str(repo),
                "--authorized-scope",
                "dispatch-authorization-crossing",
            ]
        )
    stderr = capsys.readouterr().err

    assert exc_info.value.code == 2
    assert "--authorized-scope requires --authorized-path" in stderr


def test_unsupported_authorized_scope_remains_fail_closed(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "docs/project_status.md"
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "not-a-supported-scope",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["exit_reason"] == "authorized path rejected"
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "not-a-supported-scope",
            "reason": "unsupported authorized scope: not-a-supported-scope",
        }
    ]


def test_committed_base_to_head_detects_clean_committed_change(tmp_path, capsys):
    repo = _repo(tmp_path)
    base_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _write(repo / "notes.md", "committed\n")
    _git(repo, "add", "notes.md")
    _git(repo, "commit", "-m", "committed change")
    head_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert _git(repo, "status", "--short").stdout == ""

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--base-ref",
            base_ref,
            "--head-ref",
            head_ref,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["tracked_changed_files"] == ["notes.md"]
    assert payload["staged_changed_files"] == []
    assert payload["untracked_files"] == []
    assert payload["numstat"]["mode"] == "committed_base_to_head"
    assert payload["numstat"]["base_ref"] == base_ref
    assert payload["numstat"]["head_ref"] == head_ref
    assert payload["numstat"]["committed"][0]["path"] == "notes.md"


def test_committed_base_to_head_authorizes_dispatch_crossing_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    base_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    path = "research/queue/dispatch_authorizations/KDAUTH-H004-R2-9001.dispatch_authorization.json"
    _write(repo / path, "{}\n")
    _git(repo, "add", path)
    _git(repo, "commit", "-m", "add dispatch authorization")
    head_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--base-ref",
            base_ref,
            "--head-ref",
            head_ref,
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "dispatch-authorization-crossing",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == path


def test_committed_base_to_head_authorizes_actual_next_dispatch_crossing_set(
    tmp_path, capsys
):
    repo = _repo(tmp_path)
    base_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    paths = [
        "research/queue/dispatch_records/DSP-20260804-H004R2A1.dispatch_record.json",
        "research/queue/dispatch_authorization_audit/dispatch_authorization_events.jsonl",
        "docs/project_status.md",
    ]
    for path in paths:
        _write(repo / path, "changed\n")
    _git(repo, "add", *paths)
    _git(repo, "commit", "-m", "add actual next dispatch crossing set")
    head_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert _git(repo, "status", "--short").stdout == ""

    args = [
        "--repo-root",
        str(repo),
        "--json",
        "--check-forbidden",
        "--base-ref",
        base_ref,
        "--head-ref",
        head_ref,
        "--authorized-package",
        "WP-CANON-H004-DISPATCH-RECORD-01",
        "--authorized-scope",
        "dispatch-authorization-crossing",
    ]
    for path in paths:
        args.extend(["--authorized-path", path])

    exit_code, stdout, _ = _run(args, capsys)

    payload = json.loads(stdout)
    assert exit_code == 0
    assert set(payload["tracked_changed_files"]) == set(paths)
    assert payload["staged_changed_files"] == []
    assert payload["untracked_files"] == []
    assert payload["numstat"]["mode"] == "committed_base_to_head"
    assert payload["forbidden_matches"] == []
    assert {
        item["path"] for item in payload["authorized_path_writes"]["authorized"]
    } == set(paths)
    assert payload["authorized_path_writes"]["rejected"] == []


@pytest.mark.parametrize(
    "path",
    [
        "research/queue/unrelated/UNRELATED-20260805.json",
        "tests/test_dispatch_writer.py",
        "docs/status_entries/WP-TEST.md",
    ],
)
def test_committed_base_to_head_rejects_out_of_family_paths(tmp_path, capsys, path):
    repo = _repo(tmp_path)
    base_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _write(repo / path, "changed\n")
    _git(repo, "add", path)
    _git(repo, "commit", "-m", "add out-of-family path")
    head_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--base-ref",
            base_ref,
            "--head-ref",
            head_ref,
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "dispatch-authorization-crossing",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["numstat"]["mode"] == "committed_base_to_head"
    assert payload["authorized_path_writes"]["authorized"] == []
    assert payload["authorized_path_writes"]["rejected"][0]["path"] == path
    assert "canonical dispatch record" in payload["authorized_path_writes"]["rejected"][0][
        "reason"
    ]


def test_committed_base_to_head_rejects_authorized_path_not_in_selected_diff(tmp_path, capsys):
    repo = _repo(tmp_path)
    base_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _write(repo / "notes.md", "committed\n")
    _git(repo, "add", "notes.md")
    _git(repo, "commit", "-m", "committed change")
    head_ref = _git(repo, "rev-parse", "HEAD").stdout.strip()
    path = "research/queue/dispatch_authorizations/KDAUTH-H004-R2-9001.dispatch_authorization.json"
    _write(repo / path, "untracked and excluded from committed comparison\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--base-ref",
            base_ref,
            "--head-ref",
            head_ref,
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "dispatch-authorization-crossing",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["untracked_files"] == []
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "dispatch-authorization-crossing",
            "reason": "path not changed",
        }
    ]


@pytest.mark.parametrize("flag", ["--base-ref", "--head-ref"])
def test_committed_comparison_requires_both_endpoints(tmp_path, capsys, flag):
    repo = _repo(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        helper.run(["--repo-root", str(repo), flag, "HEAD"])
    stderr = capsys.readouterr().err

    assert exc_info.value.code == 2
    assert "requires" in stderr


@pytest.mark.parametrize(
    ("base_ref", "head_ref"),
    [("missing-base", "HEAD"), ("HEAD", "missing-head")],
)
def test_committed_comparison_invalid_ref_fails_closed(
    tmp_path, capsys, base_ref, head_ref
):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--base-ref",
            base_ref,
            "--head-ref",
            head_ref,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["exit_reason"] == "git command failed"
    assert payload["numstat"]["errors"]


def test_authorized_path_requires_scope(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    with pytest.raises(SystemExit) as exc_info:
        helper.run(["--repo-root", str(repo), "--authorized-path", path])
    stderr = capsys.readouterr().err

    assert exc_info.value.code == 2
    assert "--authorized-path requires --authorized-scope" in stderr


def test_authorized_path_requires_package(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    with pytest.raises(SystemExit) as exc_info:
        helper.run(
            [
                "--repo-root",
                str(repo),
                "--authorized-path",
                path,
                "--authorized-scope",
                "strategy-spec-schema",
            ]
        )
    stderr = capsys.readouterr().err

    assert exc_info.value.code == 2
    assert "--authorized-path requires --authorized-package" in stderr


def test_allowed_file_reports_violations(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "allowed.md", "allowed\n")
    _write(repo / "outside.md", "outside\n")

    exit_code, stdout, _ = _run(
        ["--repo-root", str(repo), "--json", "--allowed-file", "allowed.md"],
        capsys,
    )

    assert exit_code == 0
    assert json.loads(stdout)["allowed_file_violations"] == ["outside.md"]


def test_trial_log_check_reports_empty_clean_state_when_untouched(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--trial-log"], capsys)

    assert exit_code == 0
    trial_log = json.loads(stdout)["trial_log"]
    assert trial_log["checked"] is True
    assert trial_log["touched"] is False
    assert trial_log["working_tree"] == []
    assert trial_log["staged"] == []
    assert trial_log["errors"] == []


def test_helper_does_not_mutate_files_or_git_state(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "changed\n")
    _write(repo / "untracked.md", "new\n")
    before_status = _git(repo, "status", "--short").stdout
    before_readme = (repo / "README.md").read_text(encoding="utf-8")

    exit_code, _, _ = _run(["--repo-root", str(repo)], capsys)

    after_status = _git(repo, "status", "--short").stdout
    after_readme = (repo / "README.md").read_text(encoding="utf-8")
    assert exit_code == 0
    assert after_status == before_status
    assert after_readme == before_readme


def test_default_mode_remains_working_tree_and_staged(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "working tree change\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["tracked_changed_files"] == ["README.md"]
    assert payload["numstat"]["mode"] == "working_tree_and_staged"
    assert payload["numstat"]["committed"] == []
