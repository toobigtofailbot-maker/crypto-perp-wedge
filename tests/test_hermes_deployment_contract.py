from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HERMES_ROOT = REPO_ROOT / "tools" / "hermes"
HERMES_IMAGE = (
    "nousresearch/hermes-agent:v2026.8.13@"
    "sha256:68e15ae2a6d894d0ccbd9f8aacbbe13d4d28fa5dc9b6a303970b67bb2499b1a6"
)
SKILLS = {
    "repo-truth",
    "research-evidence-reader",
    "result-population-critic",
    "daily-research-brief",
    "weekly-science-review",
    "dependency-security-watch",
    "typed-project-proposal",
    "prepared-project-plan",
    "cpw-domain-tools",
}


def test_compose_pins_hermes_and_mounts_no_protected_project_family() -> None:
    compose = (HERMES_ROOT / "compose.yaml").read_text(encoding="utf-8")

    assert HERMES_IMAGE in compose
    assert "ports:" not in compose
    assert "research/queue" not in compose
    for forbidden in ("../../src", "../../lib", "../../configs", "../../secrets"):
        assert forbidden not in compose
    project_mounts = [line.strip() for line in compose.splitlines() if ":/project/" in line]
    assert project_mounts
    assert all(line.endswith(":ro") for line in project_mounts)
    assert compose.count(":/outbox:rw") == 1
    assert compose.count(":/opt/data:rw") == 1
    assert 'user: "10000:10000"' in compose
    assert 'entrypoint: ["/opt/hermes/hermes"]' in compose
    assert 'command: ["gateway", "run", "--no-supervise", "--external-supervisor"]' in compose
    assert "cap_add:" not in compose
    assert "cap_drop:\n      - ALL" in compose
    assert compose.count("no-new-privileges:true") == 2


def test_project_evidence_image_is_digest_pinned_nonroot_and_lock_driven() -> None:
    dockerfile = (HERMES_ROOT / "Dockerfile.project-evidence").read_text(encoding="utf-8")

    assert re.search(
        r"^FROM python:3\.11\.9-slim-bookworm@sha256:[0-9a-f]{64}$", dockerfile, re.MULTILINE
    )
    assert "COPY tools/__init__.py" not in dockerfile
    assert "pip install --no-cache-dir --requirement /app/requirements.lock.txt" in dockerfile
    assert "COPY tools/hermes/proposals /app/tools/hermes/proposals" in dockerfile
    assert "COPY tools/hermes/prepare /app/tools/hermes/prepare" in dockerfile
    assert "COPY tools/research_domain /app/tools/research_domain" in dockerfile
    assert "COPY tools/research_memory/__init__.py" in dockerfile
    assert "COPY tools/research_memory/fingerprint.py" in dockerfile
    for forbidden_memory in ("repository.py", "migrations.py", "repo_source.py", "run.py"):
        assert f"tools/research_memory/{forbidden_memory}" not in dockerfile
    for forbidden in (
        "tools/research_agents",
        "tools/research_runner",
        "tools/canon_intake",
        "COPY src",
        "COPY lib",
        "COPY configs",
    ):
        assert forbidden not in dockerfile
    assert "USER 65532:65532" in dockerfile
    assert 'ENTRYPOINT ["python", "-m", "tools.mcp.project_evidence.server"]' in dockerfile


def test_config_exposes_only_project_evidence_and_disables_escalation() -> None:
    config = (HERMES_ROOT / "config" / "config.yaml").read_text(encoding="utf-8")

    assert "_config_version: 12" in config
    assert 'provider: "openai-codex"' in config
    assert 'default: "${HERMES_MODEL}"' in config
    for disabled in (
        "terminal",
        "file",
        "code_execution",
        "memory",
        "skills",
        "cronjob",
        "delegation",
        "computer_use",
    ):
        assert f"    - {disabled}\n" in config
    assert "cli: [mcp-project-evidence]" in config
    assert "sampling:\n      enabled: false" in config
    assert "elicitation:\n      enabled: false" in config
    assert "supports_parallel_tool_calls: false" in config
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" not in config
    assert "API_KEY" not in config


def test_exact_nine_skills_are_readonly_fail_closed_and_sha_anchored() -> None:
    skill_paths = sorted((HERMES_ROOT / "skills").glob("*/SKILL.md"))

    assert {path.parent.name for path in skill_paths} == SKILLS
    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        description = re.search(r"^description: (.+)$", text, re.MULTILINE)
        assert description is not None and len(description.group(1)) <= 60
        assert "version: 1.0.0" in text
        assert "requires_toolsets: [mcp-project-evidence]" in text
        assert "repo SHA" in text or "Repo SHA" in text
        assert "UNKNOWN" in text
        assert "authority" in text.lower()
        assert "self-enable" in text or "enable tools" in text or "widen MCP/tool scope" in text


def test_domain_proposal_prepare_and_intake_expose_exactly_fourteen_mcp_tools() -> None:
    compose = (HERMES_ROOT / "compose.yaml").read_text(encoding="utf-8")
    config = (HERMES_ROOT / "config/config.yaml").read_text(encoding="utf-8")

    assert compose.count("./skills/typed-project-proposal:") == 1
    assert compose.count("./skills/prepared-project-plan:") == 1
    assert compose.count("./skills/cpw-domain-tools:") == 1
    included = re.findall(r"^        - ([a-z_]+)$", config, re.MULTILINE)
    assert included == [
        "project_evidence_manifest",
        "list_project_resources",
        "read_project_resource",
        "run_evidence_query",
        "lookup_research_memory",
        "check_dependency_security_watch",
        "submit_proposal",
        "submit_prepared_payload",
        "cpw_assess_research_capabilities",
        "cpw_formalize_strategy_draft",
        "cpw_build_preregistration_packet",
        "cpw_build_approval_requirement",
        "cpw_validate_trial_denominator",
        "cpw_build_bounded_research_intent",
    ]
    assert len(included) == 14


def test_domain_resource_mounts_are_exact_readonly_and_hermes_has_no_repo_mount() -> None:
    compose = (HERMES_ROOT / "compose.yaml").read_text(encoding="utf-8")
    for path in (
        "IND-CATALOG-0001.indicator_catalog.json",
        "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json",
        "STRAT-SPEC-0003.strategy_spec.json",
        "strategy_spec.schema.json",
    ):
        lines = [line.strip() for line in compose.splitlines() if path in line]
        assert len(lines) == 1
        assert lines[0].endswith(":ro")
    hermes_section = compose.split("  hermes:", 1)[1]
    assert ":/project/" not in hermes_section


def test_schedule_plan_contains_only_daily_weekly_and_watch_jobs() -> None:
    plan = json.loads((HERMES_ROOT / "schedule_plan.json").read_text(encoding="utf-8"))

    assert plan["timezone"] == "UTC"
    assert len(plan["jobs"]) == 3
    assert {job["skill"] for job in plan["jobs"]} == {
        "daily-research-brief",
        "weekly-science-review",
        "dependency-security-watch",
    }
    assert all(job["deliver"] == "local" for job in plan["jobs"])
    prompts = " ".join(job["prompt"] for job in plan["jobs"]).lower()
    assert "do not update dependencies" in prompts
    assert "execute trade" not in prompts


def test_readonly_postgres_role_contract_revokes_mutation_and_grants_select() -> None:
    sql = (HERMES_ROOT / "research_memory_readonly_role.sql").read_text(encoding="utf-8")

    assert "default_transaction_read_only = on" in sql
    assert "NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS" in sql
    assert "REVOKE CREATE ON SCHEMA research_memory" in sql
    assert "REVOKE ALL PRIVILEGES ON ALL TABLES" in sql
    assert "REVOKE ALL PRIVILEGES ON ALL SEQUENCES" in sql
    assert "GRANT SELECT ON TABLE" in sql
    for table in (
        "hypothesis_items",
        "memory_records",
        "memory_aliases",
        "evidence_references",
    ):
        assert f"research_memory.{table}" in sql


def test_start_script_enforces_separate_home_and_exact_repo_identity() -> None:
    script = (HERMES_ROOT / "start.ps1").read_text(encoding="utf-8")

    assert "HermesProjectHome must be separate from the repository" in script
    assert "must not be a symlink or junction" in script
    assert "git -C $repoRoot rev-parse HEAD" in script
    assert "$env:PROJECT_REPO_SHA = $repoSha" in script
    assert "docker compose -f $compose config --quiet" in script
    assert "Docker is required for the isolated Hermes deployment" in script
    assert "ResearchMemoryReadOnlyDsn" in script
    assert "Write-Output $ResearchMemoryReadOnlyDsn" not in script


def test_docker_compose_contract_if_docker_is_available() -> None:
    docker = shutil.which("docker")
    if docker is None:
        pytest.skip("physical Docker/Compose validation requires the deployment host")
    docker_path = Path(docker)
    standalone_compose = docker_path.with_name("docker-compose.exe")
    command = [str(standalone_compose)] if standalone_compose.is_file() else [docker, "compose"]
    result = subprocess.run(
        [*command, "-f", str(HERMES_ROOT / "compose.yaml"), "config", "--quiet"],
        cwd=REPO_ROOT,
        env={
            "PATH": str(docker_path.parent),
            "HERMES_PROJECT_HOME": str(REPO_ROOT.parent / "test-hermes-home"),
            "HERMES_PROPOSAL_OUTBOX_HOST": str(REPO_ROOT / "scratch/hermes_proposal_outbox"),
            "HERMES_MODEL": "test/model",
            "PROJECT_REPO_SHA": "0" * 40,
            "PROJECT_REPO_BRANCH": "test",
            "RESEARCH_MEMORY_READONLY_DSN": "",
        },
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
