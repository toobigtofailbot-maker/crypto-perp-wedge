"""Manual, default-OFF factory consumer; Prefect never owns scientific authority."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import prefect
from prefect import flow
from prefect.runner.storage import LocalStorage
from prefect.states import Failed
from psycopg.conninfo import conninfo_to_dict

from tools.lab_pipeline import runner_adapter as adapter
from tools.research_autonomy.contract_builder import contract_from_payload
from tools.research_autonomy.envelope import content_hash
from tools.research_autonomy.handoff import load_handoff
from tools.research_autonomy.store import ResearchAuthorityStore
from tools.research_factory.evidence import bound_json, safe_file, verify_fold_manifest
from tools.research_factory.manual_loop import manual_research_loop
from tools.research_factory.mapper import (
    SOURCE_CATALOG,
    committed_json,
    file_hash,
    prepare_wave,
    write_once,
)
from tools.research_storage.workspace import resolve_workspace_path

FLOW_NAME = "cpw-research-factory-manual"
DEPLOYMENT_NAME = "cpw-research-factory-manual-v1"
WORK_POOL_NAME = "cpw-research-local-process"
CLAIM_NAMESPACE = "prefect/research-factory/claims"
ENTRYPOINT = "tools/prefect_integration/research_factory_consumer.py:research_factory_consumer"
REQUEST_KEYS = {
    "schema_version",
    "handoff",
    "repo_sha",
    "campaign_id",
    "search_id",
    "contract_hash",
    "handoff_content_sha256",
    "scientific_trial_ids",
    "created_at_utc",
    "preparation_root",
    "output_root",
    "ohlcv_input",
    "d4_catalog_slice",
    "d2_import_report",
    "fold_manifest",
    "execute_approval",
}
HASH = re.compile(r"sha256:[0-9a-f]{64}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")


def _repo_root():
    return Path(__file__).resolve().parents[2]


def _path(root, relative, *, prefix=None):
    # Validate spelling before resolution, including every Windows reparse ancestor.
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("unsafe path")
    parts = relative.split("/")
    if any(
        (p != ".cpw" or i != 0)
        and (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", p) or p.endswith("."))
        for i, p in enumerate(parts)
    ):
        raise ValueError("unsafe path")
    if prefix and not relative.startswith(prefix + "/"):
        raise ValueError("wrong path namespace")
    cursor = root
    for part in parts:
        cursor /= part
        if cursor.exists() or cursor.is_symlink():
            attrs = cursor.lstat()
            if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
                raise ValueError("path indirection")
    return cursor


def _binding(root, value, *, prefix=None):
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise ValueError("closed binding required")
    if not isinstance(value["sha256"], str) or not HASH.fullmatch(value["sha256"]):
        raise ValueError("exact file hash required")
    if not any(
        value["path"].startswith(namespace + "/")
        for namespace in (".cpw/active", "scratch", "research/data_slices", "data/processed/d4a")
    ):
        raise ValueError("input outside permitted research namespaces")
    path = _path(root, value["path"], prefix=prefix)
    safe_file(root, value["path"])
    if file_hash(path) != value["sha256"]:
        raise ValueError("input bytes changed")
    return path


def _head(root):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def _verify_consumer_source(root):
    if root.resolve(strict=True) != _repo_root().resolve(strict=True):
        raise ValueError("installed worktree required")
    relative = Path(__file__).relative_to(root).as_posix()
    committed = subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=root)
    if committed != Path(__file__).read_bytes():
        raise ValueError("consumer differs from committed source")


def _store():
    # A process-local connection is never a Prefect parameter, result or exception text.
    dsn = os.environ.get("CPW_RESEARCH_FACTORY_AUTHORITY_DSN", "")
    info = conninfo_to_dict(dsn)
    if info.get("host") not in {"127.0.0.1", "localhost", "::1"} or info.get(
        "hostaddr", "127.0.0.1"
    ) not in {"127.0.0.1", "::1"}:
        raise ValueError("loopback authority required")
    store = ResearchAuthorityStore(dsn)
    with store._transaction() as conn:
        row = conn.execute(
            "SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        if (
            row["current_user"] != "cpw_research_authority_writer"
            or row["rolsuper"]
            or row["rolbypassrls"]
        ):
            raise ValueError("scoped authority writer required")
    return store


def _result(status="blocked", reason="research_blocked", report=None):
    result = {
        "operational_status": status,
        "non_authoritative": True,
        "factory_enabled": False,
        "stage5b_enabled": False,
        "disposition": "research_blocked",
        "withholding_reasons": [reason],
        "runner_calls": 0,
    }
    if report is not None:
        for key in (
            "disposition",
            "withholding_reasons",
            "runner_calls",
            "scientific_denominator",
            "terminal_commitments",
        ):
            if key in report:
                result[key] = report[key]
    json.dumps(result, allow_nan=False)
    return result


def _summarize(report):
    disposition = report["disposition"]
    status = (
        "blocked"
        if disposition
        in {"research_blocked", "research_insufficient_evidence", "research_duplicate"}
        else "failed"
        if disposition in {"research_failed", "research_terminated"}
        else "recovered"
        if report.get("recovered")
        else "completed"
    )
    return _result(status, report=report)


def _approval(root, request, prepared, contract):
    route = adapter._execution_binding(
        canonical_15m=True,
        deterministic_seed=contract.seed,
        **{
            name: request[key]["path"]
            for name, key in (
                ("ohlcv_input_path", "ohlcv_input"),
                ("d4_catalog_slice_path", "d4_catalog_slice"),
                ("d2_import_report_path", "d2_import_report"),
            )
        },
    )
    catalog = committed_json(root, SOURCE_CATALOG, contract.repo_sha)
    import_ref = SOURCE_CATALOG.replace(".catalog_slice.json", ".import_report.json")
    import_bytes = subprocess.check_output(
        ["git", "show", f"{contract.repo_sha}:{import_ref}"], cwd=root
    )
    if (
        route["data_slice_identity"] != contract.data_identity
        or catalog["catalog_version"] != contract.data_version
        or route["ohlcv_input_sha256"] != "sha256:" + catalog["normalized"]["sha256"]
        or route["d4_catalog_slice_sha256"] != file_hash(root / SOURCE_CATALOG)
        or route["d2_import_report_sha256"] != "sha256:" + hashlib.sha256(import_bytes).hexdigest()
    ):
        raise ValueError("execution differs from frozen scientific data")
    adapter._require_execute_approval(
        approval_path=root / request["execute_approval"]["path"],
        **{
            f"prepared_{name}_path": prepared["paths"][key]
            for name, key in (
                ("strategy_spec", "spec"),
                ("variant_manifest", "vm"),
                ("sweep_plan", "sweep"),
            )
        },
        bridge_preparation_run_id=prepared["preparation_id"],
        product_pipeline_run_id=prepared["pipeline_id"],
        output_root=adapter._validate_product_output_root(root / request["output_root"]),
        execution=route,
    )
    return route


def run_manual_factory_request(
    manifest_path, manifest_sha256, *, human_invocation=False, store=None, repo_root=None
):
    """Direct test seam. A durable claim denies dispatch, never authorizes it."""
    if human_invocation is not True:
        return _result(reason="factory_default_OFF")
    root = Path(repo_root or _repo_root()).absolute()
    dispatch_started = False
    try:
        attrs = root.lstat()
        if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
            raise ValueError("unsafe repository")
        manifest = _binding(
            root, {"path": manifest_path, "sha256": manifest_sha256}, prefix=".cpw/active"
        )
        if manifest.stat().st_size > 65536:
            raise ValueError("bounded request required")
        request = json.loads(manifest.read_text(encoding="utf-8"))
        if (
            not isinstance(request, dict)
            or set(request) != REQUEST_KEYS
            or request["schema_version"] != "cpw_prefect_factory_request_v1"
        ):
            raise ValueError("closed request required")
        if not SHA.fullmatch(request["repo_sha"]) or _head(root) != request["repo_sha"]:
            raise ValueError("source mismatch")
        if subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=no"], cwd=root
        ).strip():
            raise ValueError("clean immutable source required")
        _verify_consumer_source(root)
        adapter._parse_utc_like_timestamp(request["created_at_utc"])
        for key in (
            "handoff",
            "ohlcv_input",
            "d4_catalog_slice",
            "d2_import_report",
            "fold_manifest",
            "execute_approval",
        ):
            _binding(
                root,
                request[key],
                prefix=".cpw/active/research-autonomy" if key == "handoff" else None,
            )
        handoff = load_handoff(root / request["handoff"]["path"], repo_root=root)
        contract = contract_from_payload(handoff.frozen_contract.model_dump(mode="json"))
        trials = [
            p.scientific_trial_id
            for p in handoff.proposal_records
            if p.status == "ACCEPTED_FOR_SCIENTIFIC_EXECUTION"
        ]
        if (
            not trials
            or len(trials) != len(set(trials))
            or request["scientific_trial_ids"] != trials
        ):
            raise ValueError("exact accepted trial identities required")
        for key, value in (
            ("handoff_content_sha256", handoff.content_sha256),
            ("contract_hash", handoff.contract_hash),
            ("search_id", handoff.search_id),
            ("campaign_id", handoff.campaign_id),
            ("repo_sha", handoff.repo_sha),
        ):
            if request[key] != value:
                raise ValueError("scientific identity mismatch")
        preparation = _path(root, request["preparation_root"], prefix="scratch")
        output = _path(root, request["output_root"], prefix="scratch")
        adapter._validate_product_output_root(output)
        store = store or _store()
        with store._transaction() as connection:
            store._search_active(connection, contract)
        # A search-wide claim deliberately denies later waves too; no continuation authority.
        key = content_hash(
            {"campaign_id": handoff.campaign_id, "search_id": handoff.search_id}
        ).split(":")[1]
        claim = resolve_workspace_path(
            repo_root=root,
            storage_class="active",
            namespace=CLAIM_NAMESPACE,
            artifact_path=key + ".json",
        )
        _path(root, claim.relative_to(root).as_posix(), prefix=".cpw/active")
        if subprocess.run(
            ["git", "check-ignore", "-q", claim.relative_to(root).as_posix()], cwd=root, check=False
        ).returncode:
            raise ValueError("claim must be ignored")
        prior = None
        if claim.exists():
            prior = json.loads(safe_file(root, claim.relative_to(root).as_posix()).read_text())
            if (
                prior["manifest_sha256"] != manifest_sha256
                or prior["manifest_path"] != manifest_path
            ):
                return _result(reason="investigate_conflicting_claim")
        rows = [store.load_trial_result(trial, repo_root=root) for trial in trials]
        if any(rows):
            if not all(rows):
                return _result(reason="investigate_partial_terminal_commitment")
            payloads = [json.loads(row["evidence_payload"]) for row in rows]
            binding = payloads[0]["mapping_binding"]
            if any(
                p["mapping_binding"] != binding
                or p["fold_manifest_binding"] != request["fold_manifest"]
                or p["approval_sha256"] != request["execute_approval"]["sha256"]
                for p in payloads
            ):
                raise ValueError("terminal request mismatch")
            _, prepared = bound_json(root, binding)
            identity = content_hash(
                {
                    "contract_hash": contract.contract_hash,
                    "wave": handoff.content_sha256,
                    "mapping": prepared["mapping"],
                    "created_at_utc": request["created_at_utc"],
                }
            )
            expected_mapping = preparation / identity.split(":")[1] / "mapping.json"
            if (
                root / binding["path"] != expected_mapping
                or prepared["handoff_sha256"] != handoff.content_sha256
            ):
                raise ValueError("original preparation identity mismatch")
            # Resolve the original retained checkpoint; never regenerate the wave.
            checkpoint = safe_file(
                root,
                str(Path(binding["path"]).parent / "evidence_completed_checkpoint.json").replace(
                    "\\", "/"
                ),
                scratch=True,
            )
            checkpoint_payload = json.loads(checkpoint.read_text())
            if (
                checkpoint_payload["mapping_binding"] != binding
                or checkpoint_payload["approval_sha256"] != request["execute_approval"]["sha256"]
                or content_hash(checkpoint_payload["contract"]) != content_hash(contract.to_dict())
            ):
                raise ValueError("original checkpoint mismatch")
            for payload in payloads:
                for field in (
                    "summary_binding",
                    "fold_binding",
                    "robustness_binding",
                    "fold_manifest_binding",
                    "purge_bars",
                    "embargo_bars",
                ):
                    if checkpoint_payload[field] != payload[field]:
                        raise ValueError("checkpoint evidence mismatch")
            if (
                checkpoint_payload["mapping_sha256"] != binding["sha256"]
                or checkpoint_payload["state"] != "physical_execution_may_have_started"
            ):
                raise ValueError("checkpoint state mismatch")
            if checkpoint_payload["execution"] != _approval(root, request, prepared, contract):
                raise ValueError("checkpoint input mismatch")
            return _summarize(
                manual_research_loop(
                    store=store,
                    handoff=handoff,
                    repo_root=root,
                    preparation_root=preparation,
                    output_root=output,
                    created_at_utc=request["created_at_utc"],
                    human_invocation=True,
                )
            )
        if prior:
            return _result(reason="investigate_possible_physical_execution_before_rerun")
        prepared = prepare_wave(
            store=store,
            handoff=handoff,
            contract=contract,
            repo_root=root,
            output_root=preparation,
            created_at_utc=request["created_at_utc"],
        )
        _approval(root, request, prepared, contract)
        protocol = store.load_scientific_protocol(handoff.search_id)
        verify_fold_manifest(
            root,
            request["fold_manifest"],
            prepared,
            contract,
            purge_bars=protocol["purge_bars"],
            embargo_bars=protocol["embargo_bars"],
        )
        # Existing factory rechecks exact authority immediately before physical dispatch.
        claim_payload = {
            "manifest_path": manifest_path,
            "manifest_sha256": manifest_sha256,
            "state": "may_have_run",
            "scientific_trial_ids": trials,
        }
        claim.parent.mkdir(parents=True, exist_ok=True)
        _path(root, claim.relative_to(root).as_posix(), prefix=".cpw/active")
        try:
            write_once(claim, claim_payload, exclusive=True)
        except FileExistsError:
            return _result(reason="investigate_concurrent_claim")
        # A claim cannot freeze inputs; recheck their exact bytes before delegating.
        _binding(root, {"path": manifest_path, "sha256": manifest_sha256}, prefix=".cpw/active")
        for field in (
            "handoff",
            "ohlcv_input",
            "d4_catalog_slice",
            "d2_import_report",
            "fold_manifest",
            "execute_approval",
        ):
            _binding(root, request[field])
        dispatch_started = True
        report = manual_research_loop(
            store=store,
            handoff=handoff,
            repo_root=root,
            preparation_root=preparation,
            output_root=output,
            created_at_utc=request["created_at_utc"],
            human_invocation=True,
            execute_approval_path=request["execute_approval"]["path"],
            ohlcv_input_path=request["ohlcv_input"]["path"],
            d4_catalog_slice_path=request["d4_catalog_slice"]["path"],
            d2_import_report_path=request["d2_import_report"]["path"],
            fold_manifest_binding=request["fold_manifest"],
        )
        return _summarize(report)
    except Exception:  # noqa: BLE001 -- redact credential-bearing infrastructure failures
        # Preserve ambiguous claims and all CPW evidence; avoid credential-bearing errors.
        result = _result(reason="investigate_unverifiable_request_or_execution")
        if dispatch_started:
            result["runner_calls"] = None
        return result


def _local_prefect():
    url = urlsplit(os.environ.get("PREFECT_API_URL", ""))
    if (
        prefect.__version__ != "3.8.6"
        or url.scheme != "http"
        or url.hostname not in {"127.0.0.1", "localhost", "::1"}
        or url.username
        or url.password
        or url.query
        or url.fragment
        or os.environ.get("PREFECT_API_KEY")
    ):
        raise ValueError("pinned loopback self-hosted Prefect required")


@flow(name=FLOW_NAME, retries=0, persist_result=False)
def research_factory_consumer(
    manifest_path: str, manifest_sha256: str, human_invocation: bool = False
):
    _local_prefect()
    result = run_manual_factory_request(
        manifest_path, manifest_sha256, human_invocation=human_invocation
    )
    if result["operational_status"] in {"blocked", "failed"}:
        # Prefect Failed-state data must be an exception, not an operational map.
        return Failed(message=json.dumps(result, sort_keys=True, allow_nan=False))
    return result


def register_research_factory_deployment(*, repo_root, version):
    _local_prefect()
    root = Path(repo_root).resolve(strict=True)
    if (
        root != _repo_root().resolve(strict=True)
        or not SHA.fullmatch(version)
        or _head(root) != version
    ):
        raise ValueError("exact installed worktree source required")
    if subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=root
    ).strip():
        raise ValueError("clean source required")
    _verify_consumer_source(root)
    sourced = type(research_factory_consumer).from_source(
        source=LocalStorage(str(root)), entrypoint=ENTRYPOINT
    )
    return sourced.deploy(
        name=DEPLOYMENT_NAME,
        work_pool_name=WORK_POOL_NAME,
        version=version,
        build=False,
        push=False,
        schedules=[],
        triggers=[],
        concurrency_limit=1,
        print_next_steps=False,
    )
