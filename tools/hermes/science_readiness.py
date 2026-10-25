"""Manual, default-OFF 02D external science-readiness receipts; no scientific execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from tools.hermes import discovery_intent as di
from tools.hermes import discovery_intent_consumer as dc
from tools.hermes import intent_strategy_spec_handoff as hs
from tools.mcp.project_evidence.models import ProjectEvidenceError, RepoIdentity
from tools.mcp.project_evidence.resources import EvidenceResourceCatalog
from tools.research_runner.spec_signal_compiler import SpecSignalCompilerError, compile_signal

SCHEMA = "cpw_hermes_science_readiness_batch_v1"
PREREG_MISSING = ["verified pipeline_run_id", "native pipeline request", "verified pipeline formalized object",
                  "actual historical availability/lineage context"]
CONTRACT_REASONS = {
    "NEEDS_CANONICAL_ADMISSION": "external drafts are not exact committed canonical Strategy Spec evidence",
    "NEEDS_ENVELOPE_OR_DURABLE_STATE": "no verified approved envelope or durable budget/holdout/contamination lineage",
    "NEEDS_VALID_REQUEST": "no verified BoundedSearchRequest with exact data, parameter and scientific-policy bindings",
}


def _check_paths(*paths: Path) -> None:
    for path in paths:
        if ".." in path.parts:
            raise hs.HandoffError("path traversal is not allowed")
        absolute = path.absolute()
        for cursor in (absolute, *absolute.parents):
            if cursor.exists() and dc._is_link(cursor):
                raise hs.HandoffError("path traverses a symlink or junction")


def _synthetic(spec: dict[str, Any]) -> dict[str, Any]:
    """One fixed bounded compiler probe, never a backtest or data-coverage check."""
    import pandas as pd

    params = {p["name"]: p["default"] for p in spec["free_parameters"]["parameters"]}
    frequency = {"15m": "15min", "30m": "30min", "1h": "h", "4h": "4h", "1d": "D"}
    timeframe = spec["timeframe_and_data"]["primary_timeframe"]
    index = pd.date_range("2000-01-01", periods=128, freq=frequency[timeframe], tz="UTC")
    close = [100.0 + (n % 23) for n in range(128)]
    frame = pd.DataFrame({"open": close, "high": [v + 1 for v in close],
                          "low": [v - 1 for v in close], "close": close, "volume": 1000.0}, index=index)
    # Host fields are fabricated explicitly; their presence establishes no historical availability.
    for ref in spec["timeframe_and_data"].get("host_data_refs", []):
        if ref.get("stream") != "indicator_catalog" and ref["field"] not in frame:
            frame[ref["field"]] = 0.0001
    result: dict[str, Any] = {
        "label": "SYNTHETIC_TECHNICAL_ONLY", "tool": "tools.research_runner.spec_signal_compiler.compile_signal",
        "bars": 128, "assignment": params, "fixture_version": "fixed_ohlcv_host_fields_v1",
        "fixture_sha256": di.canonical_sha256({"index": list(map(str, index)), "columns": frame.to_dict("list")}),
        "static_compiler_feasibility": "NOT_INDEPENDENTLY_ESTABLISHED_BY_A_STATIC_API",
        "limitation": "one synthetic default assignment only; no costs, historical coverage, OOS or edge proof",
    }
    try:
        signal = compile_signal(spec, {"parameter_values": params}, frame)
    except (SpecSignalCompilerError, ValueError, KeyError, TypeError) as exc:
        result.update(status="BLOCKED", reason=str(exc))
    else:
        result.update(status="PASSED", signal_sha256=di.canonical_sha256(signal.tolist()), rows=len(signal))
    return result


class ScienceReadiness:
    def __init__(self, root: Path = REPO_ROOT) -> None:
        self.root = root
        self.identity = RepoIdentity.resolve(root)
        self.handoff = hs.IntentStrategySpecHandoff(root, self.identity)
        self.catalog = EvidenceResourceCatalog(root, self.identity)
        self.git = di.GitHead(root)

    def _head(self) -> None:
        if RepoIdentity.resolve(self.root).repo_sha != self.identity.repo_sha:
            raise hs.HandoffError("current HEAD changed during readiness verification")

    def build_files(self, built_dir: Path, prepared_dir: Path, responses_dir: Path) -> dict[str, bytes]:
        self._head()
        _check_paths(built_dir, prepared_dir, responses_dir)
        built = hs.verify_built(built_dir)
        built_files = hs._read_tree(built_dir)
        manifest, prepared = self.handoff.load_prepared(prepared_dir)
        source = hs._strict_json(prepared[f"source/{dc.SUMMARY_FILE}"])
        if (len({i["idea_id"] for i in source["ideas"]}) != len(source["ideas"])
                or sum(len(ids) for ids in source["counts"].values()) != len(source["ideas"])
                or source["counts"] != {s: [i["idea_id"] for i in source["ideas"] if i["status"] == s]
                                        for s in (dc.BUILT, dc.LEAD, dc.BLOCKED_EVIDENCE, dc.BLOCKED_MEMORY, dc.BLOCKED_NATIVE)}):
            raise hs.HandoffError("02B population identities or counts disagree")
        if built["repo_sha"] != self.identity.repo_sha or source["source_packet"]["repo_sha"] != self.identity.repo_sha:
            raise hs.HandoffError("02B/02C provenance is historical/stale; never rebound")
        if self.handoff.build_files(prepared_dir, responses_dir) != built_files:
            raise hs.HandoffError("02C replay did not reproduce exact built bytes or population")
        # 02C replays formalization; independently re-resolve retained 02B native evidence too.
        for idea in source["ideas"]:
            if idea["native_intent"] is None:
                continue  # upstream evidence failures remain recorded blocked ideas
            for anchor in idea["evidence_anchors"]:
                evidence = self.catalog.read(anchor["resource_uri"])["evidence"]
                _check_paths(self.root / evidence["path"])
                if (anchor["repo_sha"] != self.identity.repo_sha or anchor["repo_path"] != evidence["path"]
                        or anchor["artifact_sha256"] != evidence["artifact_sha256"]
                        or self.git.blob_sha256(evidence["path"]) != evidence["artifact_sha256"]):
                    raise hs.HandoffError("retained evidence differs from current HEAD")
        files: dict[str, bytes] = {}
        ideas = []
        for entry, upstream in zip(built["ideas"], source["ideas"], strict=True):
            receipt = hs._strict_json(built_files[entry["receipt"]])
            index = upstream["index"]
            if (entry["index"], entry["idea_id"]) != (index, upstream["idea_id"]):
                raise hs.HandoffError("source idea order or identity differs")
            request = (hs._strict_json(prepared[receipt["request"]["file"]])
                       if receipt["request"] else None)
            native = receipt["native_formalization"]
            model_draft = (receipt["model_response"] or {}).get("reasoned_draft")
            formalized = native["research_object"] if native else None
            checks = []
            for draft in entry["drafts"]:
                spec = hs._strict_json(built_files[draft["file"]])
                checks.append({
                    "draft": draft, "schema": "PASSED_NONCANONICAL_DRAFT_ONLY",
                    "family_id": native["family_id"], "adapter_metadata": native["adapter_metadata"],
                    "parameter_review": {
                        "status": "REQUIRES_REVIEW_NO_SEMANTIC_EQUIVALENCE_ASSERTED",
                        "intent_bounds": request["bound_intent"]["proposed_parameter_bounds"],
                        "model_bounds": model_draft["parameter_bounds"],
                        "formalized_bounds": formalized["parameter_bounds"],
                        "model_to_formalized_changed": model_draft["parameter_bounds"] != formalized["parameter_bounds"],
                        "spec_parameters": spec["free_parameters"],
                        "next_action": "review all adapter changes, fixed mechanics and emitted parameter domains",
                    },
                    "compiler": _synthetic(spec),
                    "historical_data": {"status": "NOT_READY", "catalog_assessment": native["capability_assessment"],
                                        "missing": "exact data bytes/hashes, feature-parent lineage and requested window coverage",
                                        "next_action": "read-only exact-window data and lineage investigation"},
                    "trading_costs": {"status": "NOT_READY", "missing": "verified fees, slippage and funding assumptions"},
                    "oos_holdout": {"status": "NOT_READY", "missing": "verified split, purge/embargo and unexposed holdout lineage"},
                    "overfitting_controls": {"status": "NOT_READY", "missing": "frozen search domains, trial denominator and multiple-testing protocol"},
                })
            memory = {}
            for key in ("original_memory", "refreshed_memory"):
                record = upstream[key]
                state = (record or {}).get("state", "UNKNOWN")
                if state in ("UNKNOWN_MEMORY_STATE", "MEMORY_UNAVAILABLE"):
                    state = "UNKNOWN"
                memory[key] = {"state": state, "record": record,
                               "interpretation": "historical recorded lookup only; unknown/unavailable or no match is not novelty"}
            result = {
                "index": index, "idea_id": entry["idea_id"], "status": entry["status"],
                "science_status": "NOT_READY", "source_02b": upstream, "source_02c": receipt,
                "source_native_intent": (hs._strict_json(prepared[f"source/{upstream['native_intent']['file']}"])
                                         if upstream["native_intent"] else None),
                "memory": memory, "technical_checks": checks,
                "preregistration": {"status": "NOT_READY", "missing_inputs": PREREG_MISSING,
                                     "native_semantics": "tools.research_domain.preregistration.build_preregistration_packet",
                                     "next_action": "establish genuine verified pipeline inputs before calling pure native semantics"},
                "search_contract": {"status": "NOT_ISSUABLE", "reasons": CONTRACT_REASONS,
                                    "native_requirements": "tools.research_autonomy.contract_builder: verify_evidence, validate_inputs, construct_contract",
                                    "next_action": "separately authorized canonical admission and verification of approved envelope/request/durable lineage"},
                "next_legal_investigation": ([upstream["next_legal_investigation"], receipt["next_legal_investigation"]]
                                             if not checks else ["review model/intent/native/spec semantic and parameter differences",
                                                                 "investigate exact historical coverage, costs and scientific protocol; no execution"]),
            }
            name = f"ideas/{index:02d}.receipt.json"
            files[name] = hs._json_bytes(result)
            ideas.append({"index": index, "idea_id": entry["idea_id"], "status": entry["status"],
                          "receipt": name, "receipt_sha256": dc._sha256_bytes(files[name])})
        summary = hs._hashed({
            "schema_version": SCHEMA, "authority": hs.AUTHORITY, "repo_sha": self.identity.repo_sha,
            "upstream_identity": {"02c": built["content_sha256"], "02c_prepared": manifest["content_sha256"],
                                  "02b": source["content_sha256"], "provenance_chain": built["provenance_chain"]},
            "input_hashes": {"built": {n: dc._sha256_bytes(r) for n, r in sorted(built_files.items())},
                             "prepared": {n: dc._sha256_bytes(r) for n, r in sorted(prepared.items())},
                             "responses": {n: dc._sha256_bytes(p.read_bytes())
                                           for n, p in dc._ordinary_tree(responses_dir).items()}},
            "ideas": ideas, "counts": {s: sum(i["status"] == s for i in ideas) for s in hs.BUILT_STATUSES},
            "science_counts": {"NOT_READY": len(ideas), "NOT_ISSUABLE": len(ideas)},
            "limitations": ["content hashes bind bytes, not actual Hermes model authorship or external source truth",
                            "02B memory is retained history, not refreshed scientific authority",
                            "no canonical admission, preregistration approval, SearchContract or execution",
                            "existing approved-envelope operating semantics are unchanged; no new per-experiment gate"],
        })
        files[hs.SUMMARY_FILE] = hs._json_bytes(summary)
        self._head()
        return self.handoff._guard(hs._render(files))

    def verify(self, directory: Path, built_dir: Path, prepared_dir: Path, responses_dir: Path) -> dict[str, Any]:
        _check_paths(directory)
        files = hs._read_tree(directory)
        summary = hs._strict_json(files[hs.SUMMARY_FILE])
        hs._check_hash(summary, SCHEMA)
        if files != self.build_files(built_dir, prepared_dir, responses_dir):
            raise hs.HandoffError("readiness replay did not reproduce identical bytes")
        return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "replay"))
    parser.add_argument("--built-dir", required=True, type=Path)
    parser.add_argument("--prepared-dir", required=True, type=Path)
    parser.add_argument("--responses-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="new external output for build; existing packet for verify/replay")
    args = parser.parse_args(argv)
    try:
        _check_paths(args.output)
        adapter = ScienceReadiness()
        inputs = (args.built_dir, args.prepared_dir, args.responses_dir)
        if args.command == "build":
            hs._publish(adapter.build_files(*inputs), args.output, lambda p: adapter.verify(p, *inputs))
        summary = adapter.verify(args.output, *inputs)
    except (dc.ConsumerError, ProjectEvidenceError, ValidationError, OSError, ValueError, KeyError,
            TypeError, AttributeError) as exc:
        print(f"SCIENCE_READINESS_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(json.dumps({k: summary[k] for k in ("content_sha256", "counts", "science_counts")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
