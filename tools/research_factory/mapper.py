"""Map an exact durable Governor wave into one bounded 15m scratch population."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from tools.research_autonomy.contract_builder import contract_from_payload
from tools.research_autonomy.handoff import replay_handoff, validate_handoff
from tools.research_autonomy.m1_source import M1_MAPPING, M1_ROOT, M1_VERSION, M1Source
from tools.research_runner import run_offline_sweep as runner
from tools.research_search.contract import sha256_payload

PARAMETERS = {"center_lookback_bars", "vol_lookback_bars", "trend_lookback_bars"}
SOURCE_SPEC = "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json"
SOURCE_VM = "research/variant_manifests/VM-0003.variant_manifest.json"
SOURCE_SWEEP = "research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json"
SOURCE_CATALOG = "research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
# Versioned opt-in route for a reviewed original (Hermes-parent) canonical Spec/VM/Sweep.
ORIGINAL_SCHEMA = "research_factory_mapping_original_v1"
ORIGINAL_ROOTS = (
    "research/strategy_specs/",
    "research/variant_manifests/",
    "research/sweep_plans/",
    "research/data_slices/",
)


class MappingBlocked(ValueError):
    """Unsupported or unverifiable mapping; never reinterpret a proposal."""


def file_hash(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def committed_json(root, path, repo_sha, *, original=False):
    # VM/Sweep are immutable templates, outside the kernel evidence-anchor surface.
    # Verify their exact committed bytes locally rather than widening that API.
    if original:
        if not path.startswith(ORIGINAL_ROOTS) or ".." in Path(path).parts or "\\" in path:
            raise MappingBlocked("unsupported committed canonical artifact")
    elif path not in {SOURCE_SPEC, SOURCE_VM, SOURCE_SWEEP, SOURCE_CATALOG}:
        raise MappingBlocked("unsupported committed template")
    import stat

    cursor = root.resolve(strict=True)
    for part in Path(path).parts:
        cursor /= part
        attrs = cursor.lstat()
        if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
            raise MappingBlocked("template indirection denied")
    raw = cursor.read_bytes()
    committed = subprocess.run(
        ["git", "show", f"{repo_sha}:{path}"], cwd=root, capture_output=True, check=True
    ).stdout
    if committed != raw:
        raise MappingBlocked("template differs from exact committed bytes")
    return json.loads(raw)


def _get(value, dotted):
    for key in dotted.split("."):
        value = value[key]
    return value


def write_once(path, payload, *, exclusive=False):
    """Publish exact immutable scratch bytes without overwriting a racing writer."""
    encoded = (json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if exclusive:
                raise
            if path.read_bytes() != encoded:
                raise MappingBlocked("conflicting immutable scratch bytes")
    finally:
        os.unlink(temporary)
    return path


def _committed_paths(root, repo_sha, prefix, suffix):
    listed = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", repo_sha, "--", prefix],
        cwd=root,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.splitlines()
    return [p for p in listed if p.endswith(suffix)]


def _original_sources(root, frozen, original):
    """Resolve the exact reviewed canonical Spec/VM/Sweep/catalog bound by the frozen contract."""
    from .original_source import OriginalBlocked, verify

    try:
        verify(root, frozen, original)
    except OriginalBlocked as exc:
        raise MappingBlocked(str(exc)) from None
    sha = frozen.repo_sha
    spec_path = f"research/strategy_specs/{frozen.strategy_spec_id}.strategy_spec.json"
    spec = committed_json(root, spec_path, sha, original=True)
    if (
        spec.get("strategy_spec_id") != frozen.strategy_spec_id
        or file_hash(root / spec_path) != frozen.strategy_spec_hash
    ):
        raise MappingBlocked("blocked_unsupported_mapping: exact reviewed canonical spec bytes required")
    vm_id = spec["pre_registration_support"]["variant_manifest_ref"]
    vm_path = f"research/variant_manifests/{vm_id}.variant_manifest.json"
    vm = committed_json(root, vm_path, sha, original=True)
    if (
        vm["variant_manifest_id"] != vm_id
        or vm["parent_strategy_spec"]["strategy_spec_id"] != frozen.strategy_spec_id
    ):
        raise MappingBlocked("blocked_unsupported_mapping: Variant Manifest does not bind the spec")
    sweeps = [
        p
        for p in _committed_paths(root, sha, "research/sweep_plans/", ".sweep_plan.json")
        if committed_json(root, p, sha, original=True)["parent_variant_manifest"]["variant_manifest_id"]
        == vm_id
    ]
    catalogs = [
        p
        for p in _committed_paths(root, sha, "research/data_slices/", ".catalog_slice.json")
        if committed_json(root, p, sha, original=True).get("slice_identity", {}).get("data_slice_identity")
        == frozen.data_identity
    ]
    if len(sweeps) != 1 or len(catalogs) != 1:
        raise MappingBlocked(
            "blocked_unsupported_mapping: exactly one Sweep Plan and data catalog required"
        )
    return spec_path, vm_path, sweeps[0], catalogs[0]


def prepare_wave(
    *,
    store,
    handoff,
    contract,
    repo_root: Path,
    output_root: Path,
    created_at_utc: str,
    original=None,
    m1_source=None,
):
    """Validate authority before emitting legal planning artifacts, never approval.

    ``original`` (default None) selects the versioned original-parent route; the legacy
    STRAT-SPEC-0003 branch and its output bytes are unchanged.
    """
    root = repo_root.resolve(strict=True)
    handoff = validate_handoff(handoff)
    frozen = contract_from_payload(contract.to_dict())
    if frozen.contract_hash != handoff.contract_hash:
        raise MappingBlocked("contract/handoff mismatch")
    governor = replay_handoff(handoff, store=store, repo_root=root)
    if (frozen.data_version == M1_VERSION) != (m1_source is not None) or (
        m1_source is not None and original is not None
    ):
        raise MappingBlocked("explicit M1 mapping required; routes cannot be combined")
    m1 = m1_source is not None
    if m1:
        try:
            source = M1Source.model_validate_json(m1_source.model_dump_json())
            if source.identity != frozen.data_identity:
                raise ValueError("M1 frozen source identity mismatch")
            source.require_partition(frozen.split_protocol)
            spec_path = f"research/strategy_specs/{frozen.strategy_spec_id}.strategy_spec.json"
            if not re.fullmatch(r"STRAT-SPEC-[0-9]{4}", frozen.strategy_spec_id):
                raise ValueError("M1 exact committed strategy spec ID required")
            spec = committed_json(root, spec_path, frozen.repo_sha, original=True)
            source.require_spec(spec)
            vm_id = spec["pre_registration_support"]["variant_manifest_ref"]
            if not re.fullmatch(r"VM-[0-9]{4}", vm_id):
                raise ValueError("M1 exact committed VM ID required")
            vm_path = f"research/variant_manifests/{vm_id}.variant_manifest.json"
            vm = committed_json(root, vm_path, frozen.repo_sha, original=True)
            sweep_path = f"research/sweep_plans/{source.sweep_plan_id}.sweep_plan.json"
            sources = (spec_path, vm_path, sweep_path)
            sweep = committed_json(root, sources[2], frozen.repo_sha, original=True)
            if (file_hash(root / spec_path) != frozen.strategy_spec_hash
                    or file_hash(root / vm_path) != source.variant_manifest_sha256
                    or file_hash(root / sweep_path) != source.sweep_plan_sha256
                    or sweep["sweep_plan_id"] != source.sweep_plan_id
                    or vm["parent_strategy_spec"]["strategy_spec_id"] != frozen.strategy_spec_id
                    or sweep["parent_variant_manifest"]["variant_manifest_id"] != vm_id
                    or sweep["data_and_timeframe_assumptions"]["primary_timeframe"] != source.timeframe
                    or sweep["realism_assumptions"]["fee_side_assumption"] != "taker_entry_taker_exit"):
                raise ValueError("M1 exact parent chain, clock and fee convention required")
        except (AttributeError, KeyError, OSError, TypeError, ValueError, subprocess.CalledProcessError) as exc:
            raise MappingBlocked("blocked_unsupported_mapping: M1 fixture parent or source binding") from exc
    else:
        if original is None:
            sources = (SOURCE_SPEC, SOURCE_VM, SOURCE_SWEEP, SOURCE_CATALOG)
        else:
            sources = _original_sources(root, frozen, original)
        spec, vm, sweep, catalog = (
            committed_json(root, path, frozen.repo_sha, original=original is not None)
            for path in sources
        )
        if original is None and (
            frozen.family_id != "sma_stddev_mean_reversion_v1"
            or frozen.strategy_spec_id != "STRAT-SPEC-0003"
            or frozen.strategy_spec_hash != file_hash(root / SOURCE_SPEC)
        ):
            raise MappingBlocked("blocked_unsupported_mapping: exact supported spec bytes required")
        if (
            spec["timeframe_and_data"]["primary_timeframe"] != "15m"
            or sweep["data_and_timeframe_assumptions"]["primary_timeframe"] != "15m"
            or frozen.split_protocol.development_data_ref != frozen.data_identity
        ):
            raise MappingBlocked("blocked_unsupported_mapping: 15m development data binding required")
        # The adapter consumes this entire catalog slice. A narrower development
        # partition would expose undeclared bars; require the exact frozen interval.
        import pandas as pd

        try:
            start, end = [
                pd.Timestamp(value) for value in frozen.split_protocol.development_window.split("/")
            ]
            expected_start = pd.Timestamp(catalog["range"]["start_utc"])
            expected_end = pd.Timestamp(catalog["range"]["end_utc"]) + pd.Timedelta(minutes=15)
            if (
                start != expected_start
                or end != expected_end
                or frozen.data_identity != catalog["slice_identity"]["data_slice_identity"]
                or frozen.data_version != catalog["catalog_version"]
            ):
                raise ValueError("development partition mismatch")
        except (TypeError, ValueError, KeyError) as exc:
            raise MappingBlocked(
                "blocked_unsupported_mapping: exact catalog development partition required"
            ) from exc
    # v1 VM grammar excludes adaptive search. This slice supports frozen random only.
    if (
        frozen.proposer.backend != "random"
        or frozen.conditional_rules
        or frozen.relational_constraints
        or frozen.forbidden_regions
    ):
        raise MappingBlocked(
            "blocked_unsupported_mapping: unsupported proposer or conditional rules"
        )
    declared = {p["name"]: p for p in spec["free_parameters"]["parameters"]}
    # The original route uses the reviewed spec's own axes, never the 0003 template domains.
    parameters = set(declared) if original is not None or m1 else PARAMETERS
    if set(declared) != parameters or {p.name for p in frozen.parameter_space} != parameters:
        raise MappingBlocked("blocked_unsupported_mapping: parameter surface mismatch")
    for domain in frozen.parameter_space:
        allowed = declared[domain.name]["allowed_values"]
        if (
            domain.kind != "int"
            or type(domain.low) is not int
            or type(domain.high) is not int
            or type(domain.step) is not int
            or domain.step <= 0
            or domain.low not in allowed
            or domain.high not in allowed
            or any(
                value not in allowed for value in range(domain.low, domain.high + 1, domain.step)
            )
        ):
            raise MappingBlocked("blocked_unsupported_mapping: unsupported numeric domain")
    records = [p.model_dump(mode="json") for p in handoff.proposal_records]
    accepted = sorted(
        (r for r in records if r["status"] == "ACCEPTED_FOR_SCIENTIFIC_EXECUTION"),
        key=lambda r: r["proposal_sequence"],
    )
    if not accepted:
        raise MappingBlocked("blocked_empty: zero legal trials")
    mapping = []
    for r in accepted:
        params = r["params"]
        if (
            set(params) != parameters
            or any(
                type(v) is not int or v not in declared[k]["allowed_values"]
                for k, v in params.items()
            )
            or r["params_fingerprint"] != sha256_payload(params)
            or not r["scientific_trial_id"]
        ):
            raise MappingBlocked("blocked_unsupported_mapping: parameter identity mismatch")
        for key in ("campaign_id", "search_id", "contract_hash", "data_identity", "repo_sha"):
            if r[key] != getattr(frozen, key):
                raise MappingBlocked("proposal frozen identity mismatch")
        sequence = r["proposal_sequence"]
        if not 0 <= sequence <= 999998:
            raise MappingBlocked("variant ID grammar exhausted")
        mapping.append(
            {
                k: r[k]
                for k in (
                    "campaign_id",
                    "search_id",
                    "contract_hash",
                    "proposal_id",
                    "scientific_trial_id",
                    "params_fingerprint",
                )
            }
            | {"variant_id": f"VAR-{sequence + 1:06d}", "parameter_values": params}
        )
    if len({m["scientific_trial_id"] for m in mapping}) != len(mapping):
        raise MappingBlocked("duplicate scientific trial identity")
    destination = output_root.absolute()
    relative = destination.relative_to(root)
    if relative.parts[0] != "scratch" or ".." in relative.parts:
        raise MappingBlocked("single isolated scratch namespace required")
    if m1 and not (relative.as_posix() + "/").startswith(M1_ROOT):
        raise MappingBlocked("M1 output must stay in its TEST_ONLY scratch namespace")
    cursor = root
    import stat

    for part in relative.parts:
        cursor /= part
        if cursor.exists():
            attrs = cursor.lstat()
            if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
                raise MappingBlocked("scratch indirection denied")
    identity = sha256_payload(
        {
            "contract_hash": frozen.contract_hash,
            "wave": handoff.content_sha256,
            "mapping": mapping,
            "created_at_utc": created_at_utc,
        }
    )
    number = 9000 + int(identity[-8:], 16) % 1000
    ids = (f"STRAT-SPEC-{number:04d}", f"VM-{number:04d}", f"SWEEP-PLAN-{number:04d}")
    namespace = destination / identity.removeprefix("sha256:")
    paths = [
        namespace / (ident + suffix)
        for ident, suffix in zip(
            ids, (".strategy_spec.json", ".variant_manifest.json", ".sweep_plan.json")
        )
    ]
    spec["strategy_spec_id"] = ids[0]
    spec["title"] = (f"TEST_ONLY M1 {source.instrument} {source.timeframe} Governor population"
                     if m1 else "Noncanonical frozen Governor 15m population")
    spec["lineage"] = {
        "parent_refs": [
            {
                "ref_type": "prior_strategy_spec",
                "ref_id": frozen.strategy_spec_id,
                "ref_path": sources[0],
                "ref_hash": frozen.strategy_spec_hash,
            }
        ],
        "supersedes": [],
        "amendment_of": None,
    }
    spec["provenance"]["unresolved_claims"] = []
    spec["review"]["reviewer"] = None
    spec["review"]["reviewed_at"] = None
    spec["review"]["review_notes"] = [
        "Schema planning posture only; manual mapper is not the formalizer bridge or human approval."
    ]
    spec["pre_registration_support"]["variant_manifest_ref"] = ids[1]
    # Historical internal scope is not reproducible from this schema. Do not
    # manufacture a new scope: the exact external bytes and parent hashes bind it.
    spec["hash_pinning"].update(canonical_spec_hash=None, hash_status="not_computed")
    if original is not None:
        from .original_source import ROUTE_PREFIX, verify

        proof = verify(root, frozen, original)
        source_path = namespace / "original_source.json"
        write_once(source_path, {"evidence": original, "contract_hash": frozen.contract_hash,
                                 "parent": proof["original_parent"]})
        spec["provenance"]["source_refs"].append(
            ROUTE_PREFIX + source_path.relative_to(root).as_posix() + "#" + file_hash(source_path))
    spec_hash = runner._sha256_prefixed(spec)
    n = len(mapping)
    vm["variant_manifest_id"] = ids[1]
    vm["parent_strategy_spec"].update(
        strategy_spec_id=ids[0],
        strategy_spec_hash=spec_hash,
        strategy_spec_ref=paths[0].relative_to(root).as_posix(),
    )
    pop = vm["population_governance"]
    pop["population_cap"].update(max_variants=n, cap_basis="constrained_random")
    pop["declared_population"].update(
        committed_population_count=n, declared_variant_count=n, included_variant_count=n
    )
    pop["trial_budget"].update(
        planned_trial_count=n, trial_budget_denominator=n, denominator_count=n
    )
    pop["multiple_testing_accounting"].update(
        search_family_id=frozen.family_id, search_family_method="constrained_random"
    )
    for axis in vm["parameter_axes"]:
        domain = next(p for p in frozen.parameter_space if p.name == axis["parameter_name"])
        axis["allowed_values"] = list(range(domain.low, domain.high + 1, domain.step))
        axis["range"].update(min=domain.low, max=domain.high, step=domain.step)
        axis["generator_method"] = "constrained_random"
        axis["notes"] = "Exact frozen Governor domain; no template-selected variants."
    template = copy.deepcopy(vm["variant_assignments"][0])
    vm["variant_assignments"] = []
    for i, m in enumerate(mapping, 1):
        row = copy.deepcopy(template)
        row.update(
            variant_id=m["variant_id"],
            parameter_values=m["parameter_values"],
            parameter_value_hash=m["params_fingerprint"],
        )
        row["lineage"] = {"generated_by_rule": "frozen-governor-wave", "generation_order": i}
        vm["variant_assignments"].append(row)
    notes = ["Scratch-only frozen Governor population; schema posture is not human approval."]
    vm["lineage"].update(
        parent_refs=[
            {
                "ref_type": "strategy_spec",
                "ref_id": ids[0],
                "ref_path": paths[0].relative_to(root).as_posix(),
                "ref_hash": spec_hash,
            }
        ],
        source_refs=[],
        created_at=created_at_utc,
        updated_at=created_at_utc,
        audit_notes=notes,
        hash_refs=[spec_hash, identity],
    )
    vm["review"].update(reviewer=None, reviewed_at=None, review_notes=notes)
    vm["manifest_hash_pinning"]["frozen_at"] = created_at_utc
    vm_hash = runner._sha256_prefixed(
        {k: _get(vm, k) for k in vm["manifest_hash_pinning"]["hash_scope"]}
    )
    vm["manifest_hash_pinning"]["manifest_hash"] = vm_hash
    sweep["sweep_plan_id"] = ids[2]
    sweep["parent_variant_manifest"].update(
        variant_manifest_id=ids[1],
        manifest_hash=vm_hash,
        manifest_population_count=n,
        manifest_committed_population_count=n,
        manifest_population_cap=n,
    )
    sweep["test_selection"]["selected_variant_ids"] = [m["variant_id"] for m in mapping]
    sweep["trial_accounting"].update(
        committed_population_count=n,
        selected_variant_count=n,
        multiple_testing_denominator=n,
        not_attempted_variant_count=n,
    )
    sweep["lineage"].update(
        parent_manifest_ref={
            "ref_type": "variant_manifest",
            "ref_id": ids[1],
            "ref_path": paths[1].relative_to(root).as_posix(),
            "ref_hash": vm_hash,
        },
        parent_strategy_spec_ref={
            "ref_type": "strategy_spec",
            "ref_id": ids[0],
            "ref_path": paths[0].relative_to(root).as_posix(),
            "ref_hash": spec_hash,
        },
        search_family_id=frozen.family_id,
        source_refs=[],
        created_at=created_at_utc,
        updated_at=created_at_utc,
        audit_notes=notes,
    )
    sweep["review"].update(reviewer=None, reviewed_at=None, review_notes=notes)
    # Validate in a disposable staging directory before publishing prepared files.
    with tempfile.TemporaryDirectory(
        dir=root / "scratch" if (root / "scratch").exists() else root
    ) as stage:
        staged = [Path(stage) / p.name for p in paths]
        for path, payload in zip(staged, (spec, vm, sweep)):
            path.write_text(json.dumps(payload, allow_nan=False))
        runner._validate_parent_inputs(*staged)
    for path, payload in zip(paths, (spec, vm, sweep)):
        write_once(path, payload)
    metadata = {
        "schema_version": "research_factory_mapping_v1",
        "mapping": mapping,
        "handoff_sha256": handoff.content_sha256,
        "contract_hash": frozen.contract_hash,
        "repo_sha": frozen.repo_sha,
        "source_spec_sha256": frozen.strategy_spec_hash,
        "preparation_id": "FACTORY-PREP-" + identity[-16:],
        "pipeline_id": "FACTORY-RUN-" + identity[-16:],
        "noncanonical": True,
        "runner_authority": False,
        "approval_authority": False,
        "paths": {
            k: p.relative_to(root).as_posix() for k, p in zip(("spec", "vm", "sweep"), paths)
        },
        "hashes": {k: file_hash(p) for k, p in zip(("spec", "vm", "sweep"), paths)},
        "proposal_counts": {
            "accepted": n,
            "rejected": sum(r["status"].startswith("REJECTED") for r in records),
            "duplicate": sum("DUPLICATE" in r["status"] for r in records),
            "total": len(records),
        },
        "scientific_denominator": n,
        "search_denominator": governor.scientific_denominator,
    }
    if original is not None:
        metadata.update(
            schema_version=ORIGINAL_SCHEMA,
            original_parent=proof["original_parent"],
            original_evidence=dict(original),
            source_proof_sha256=file_hash(source_path),
            source_paths=dict(zip(("spec", "vm", "sweep", "catalog"), sources)),
        )
    if m1:
        metadata.update(
            schema_version=M1_MAPPING,
            m1_source=source.model_dump(mode="json"),
            source_paths=dict(zip(("spec", "vm", "sweep"), sources)),
        )
    write_once(namespace / "mapping.json", metadata)
    return metadata
