"""Manual metadata-only protocol proposal review; never data/scientific verification."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tools.hermes import intent_strategy_spec_handoff as hs
from tools.hermes import queue_input_preparation as qp

SCHEMA = "cpw_hermes_scientific_protocol_preflight_v1"
PROPOSAL_SCHEMA = "cpw_hermes_protocol_proposal_v1"
SOURCE_SCHEMA = "cpw_hermes_verified_data_signal_bridge_v1"
METADATA = "METADATA_ONLY_UNVERIFIED"
FIXTURE = "SOFTWARE_FIXTURE_NATIVE_REPLAY"
MAX_BYTES = 2_000_000
TIMEFRAMES = {"15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400}
SOURCE_KEYS = {
    "schema_version",
    "authority",
    "repo_sha",
    "base_sha",
    "source_02f",
    "source_packet_hashes",
    "designation_sha256",
    "label",
    "limitation",
    "science_status",
    "search_contract_status",
    "investigation_queue",
    "ideas",
    "content_sha256",
}
IDEA_KEYS = {
    "idea_id",
    "index",
    "source_02e_recheck",
    "source_02c",
    "science_status",
    "search_contract_status",
    "semantic_review",
    "compilations",
    "status",
    "next_human_action",
}
MISSING = [
    "NOT_VERIFIED: physical source bytes, availability, lineage and native 02B-02G replay",
    "NOT_VERIFIED: independent non-holdout partition admission; no protected holdout access",
    "NOT_READY: approved scientific protocol, leakage/purge/embargo/warmup and cost policy",
    "NOT_READY: human strategy semantics and family/data requirements review",
    "NOT_READY: true native binding of exact 02C Strategy Spec, 02G data and approved protocol",
    "NOT_READY: native preregistration, search domains, cumulative trial/multiple-testing lineage",
    "NOT_ISSUABLE: valid approved envelope, durable budgets/holdout state and SearchContract",
    "NOT_READY: separately implemented, validated and explicitly activated Stage 5B",
]
Text = Annotated[str, Field(min_length=1, max_length=4000, pattern=r"\S")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Bars = Annotated[int, Field(ge=0)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Assumption(Strict):
    value: Positive
    provenance: Text


class Costs(Strict):
    fee_bps: Assumption
    slippage_bps: Assumption
    funding_bps: Assumption
    other_cost_bps: Assumption


class Budget(Strict):
    trials: Annotated[int, Field(gt=0)]
    cpu_seconds: Positive
    memory_mb: Positive
    rationale: Text


class Window(Strict):
    kind: Literal["construction", "validation", "final_holdout"]
    start: Text
    end: Text


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if "T" not in value or parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("windows require explicit UTC timestamps")
    return parsed.astimezone(UTC)


class IdeaProposal(Strict):
    idea_id: Text
    source_idea_sha256: Digest
    parameters: dict[Text, float | int]
    timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    cadence_bars: Annotated[int, Field(gt=0)]
    windows: Annotated[list[Window], Field(min_length=3, max_length=32)]
    purge_bars: Bars
    embargo_bars: Bars
    gap_convention: Literal["purge_plus_embargo_between_windows"]
    indicator_warmup_bars: Annotated[int, Field(gt=0)]
    warmup_bars: Annotated[int, Field(gt=0)]
    warmup_convention: Literal["within_each_window"]
    costs: Costs
    budget: Budget
    family_data_requirements: Annotated[list[Text], Field(min_length=1, max_length=32)]
    review_rationale: Text

    @model_validator(mode="after")
    def structure(self):
        kinds = [w.kind for w in self.windows]
        order = {"construction": 0, "validation": 1, "final_holdout": 2}
        if set(kinds) != set(order) or kinds != sorted(kinds, key=order.get):
            raise ValueError("windows need ordered construction, validation, final_holdout")
        if kinds.count("final_holdout") != 1:
            raise ValueError("exactly one proposed final_holdout required")
        if self.warmup_bars < self.indicator_warmup_bars:
            raise ValueError("warmup contradicts declared indicator requirement")
        seconds = TIMEFRAMES[self.timeframe]
        previous = None
        for window in self.windows:
            start, end = _utc(window.start), _utc(window.end)
            if start >= end or any(
                t.timestamp() % (seconds * self.cadence_bars) for t in (start, end)
            ):
                raise ValueError("window must increase and align to declared cadence")
            if (end - start).total_seconds() <= self.warmup_bars * seconds:
                raise ValueError("window cannot accommodate proposed warmup")
            if (
                previous is not None
                and (start - previous).total_seconds()
                < (self.purge_bars + self.embargo_bars) * seconds
            ):
                raise ValueError("overlap or gap contradicts proposed purge/embargo")
            previous = end
        if any(not math.isfinite(v) for v in self.parameters.values()):
            raise ValueError("parameters must be finite")
        return self


class Proposal(Strict):
    schema_version: Literal[PROPOSAL_SCHEMA]
    repo_sha: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    source_02g: Digest
    ideas: Annotated[list[IdeaProposal], Field(min_length=1, max_length=hs.MAX_IDEAS)]


def _read_metadata(path: Path) -> bytes:
    # No directory traversal, source discovery, frame loader or upstream verify call.
    qp.sr._check_paths(path)
    if path.suffix != ".json" or any(
        (parent / ".git").exists() for parent in path.absolute().parents
    ):
        raise hs.HandoffError("supply stand-alone external JSON metadata only")
    info = path.stat()
    if not path.is_file() or info.st_nlink != 1 or info.st_size > MAX_BYTES:
        raise hs.HandoffError("metadata must be bounded ordinary unlinked files")
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise hs.HandoffError("metadata exceeds bound")
    return raw


def _no_raw(value):
    if isinstance(value, dict):
        if set(value) & {"signal_values", "bars", "ohlcv", "raw_data", "raw_frame"}:
            raise hs.HandoffError("raw values are outside metadata scope")
        for child in value.values():
            _no_raw(child)
    elif isinstance(value, list):
        for child in value:
            _no_raw(child)


def review(source_raw: bytes, proposal_raw: bytes, repo_sha: str) -> dict:
    """Self-declared hash consistency and proposal structure only; no trust elevation."""
    if max(len(source_raw), len(proposal_raw)) > MAX_BYTES:
        raise hs.HandoffError("metadata exceeds bound")
    source = hs._strict_json(source_raw)
    if not isinstance(source, dict) or set(source) != SOURCE_KEYS:
        raise hs.HandoffError("expected stand-alone exact 02G summary structure")
    hs._check_hash(source, SOURCE_SCHEMA)
    _no_raw(source)
    if source["repo_sha"] != repo_sha:
        raise hs.HandoffError("stale declared repo identity")
    if (
        source["science_status"] != "NOT_READY"
        or source["search_contract_status"] != "NOT_ISSUABLE"
    ):
        raise hs.HandoffError("upstream scientific disposition differs")
    entries = source["ideas"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= hs.MAX_IDEAS:
        raise hs.HandoffError("invalid idea population")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != IDEA_KEYS or entry["index"] != index:
            raise hs.HandoffError("unknown idea fields or lost population ordering")
        if not isinstance(entry["idea_id"], str) or not entry["idea_id"]:
            raise hs.HandoffError("invalid idea identity")
        if not isinstance(entry["source_02e_recheck"], dict) or (
            entry["source_02e_recheck"].get("idea_id") != entry["idea_id"]
        ):
            raise hs.HandoffError("cross-idea metadata mismatch")
        if not isinstance(entry["source_02c"], dict) or (
            entry["source_02c"].get("idea_id") != entry["idea_id"]
        ):
            raise hs.HandoffError("cross-idea draft mismatch")
    ids = [e["idea_id"] for e in entries]
    if len(set(ids)) != len(ids):
        raise hs.HandoffError("duplicate population identity")
    proposal = Proposal.model_validate(hs._strict_json(proposal_raw))
    if proposal.repo_sha != repo_sha or proposal.source_02g != source["content_sha256"]:
        raise hs.HandoffError("proposal repo/source binding differs")
    if [p.idea_id for p in proposal.ideas] != ids:
        raise hs.HandoffError("proposal must preserve exact population and order")
    ideas = []
    for entry, plan in zip(entries, proposal.ideas, strict=True):
        if plan.source_idea_sha256 != hs.di.canonical_sha256(entry):
            raise hs.HandoffError("cross-idea proposal binding differs")
        assignments = [c["assignment"] for c in entry["compilations"]]
        # No new search domains or invented parameters: retain the native draft assignment.
        if (assignments and any(plan.parameters != a for a in assignments)) or (
            not assignments and plan.parameters
        ):
            raise hs.HandoffError("parameters differ from declared native draft assignment")
        for compilation in entry["compilations"]:
            defaults = {p["name"]: p["default"] for p in compilation["parameters"]["parameters"]}
            if compilation["assignment"] != defaults:
                raise hs.HandoffError("assignment differs from declared parameter definitions")
            window = compilation.get("technical_window")
            if window and window["timeframe"] != plan.timeframe:
                raise hs.HandoffError("proposal timeframe differs from declared draft")
        ideas.append(
            {
                "idea_id": entry["idea_id"],
                "index": entry["index"],
                "verification_class": METADATA,
                "status": "PROPOSED_METADATA_ONLY_UNVERIFIED",
                "science_status": "NOT_READY",
                "search_contract_status": "NOT_ISSUABLE",
                "upstream_status": entry["status"],
                "proposal": plan.model_dump(),
                "next_inputs": [
                    *[
                        "resolve feature: " + f["feature"]
                        for f in entry["source_02e_recheck"]["features"]
                        if f["status"] == "NOT_READY"
                    ],
                    *entry["source_02c"]["review_requirements"],
                    *MISSING,
                ],
            }
        )
    return hs._hashed(
        {
            "schema_version": SCHEMA,
            "authority": hs.AUTHORITY,
            "repo_sha": repo_sha,
            "verification_class": METADATA,
            "status": "PROPOSED_METADATA_ONLY_UNVERIFIED",
            "science_status": "NOT_READY",
            "search_contract_status": "NOT_ISSUABLE",
            "integrity_scope": "02H output integrity and self-declared metadata digests only; NOT_VERIFIED upstream",
            "source_sha256": hs.dc._sha256_bytes(source_raw),
            "proposal_sha256": hs.dc._sha256_bytes(proposal_raw),
            "source_02g_metadata_unverified": source,
            "shared_next_inputs": MISSING,
            "ideas": ideas,
        }
    )


class ScientificProtocolPreflight:
    def __init__(self, root: Path = hs.REPO_ROOT):
        self.root = root

    def build_files(self, summary: Path, proposal: Path) -> dict[str, bytes]:
        result = review(
            _read_metadata(summary),
            _read_metadata(proposal),
            hs.RepoIdentity.resolve(self.root).repo_sha,
        )
        return hs._render({hs.SUMMARY_FILE: hs._json_bytes(result)})

    def build(self, output: Path, summary: Path, proposal: Path) -> dict:
        qp._separate(output, summary, proposal)
        qp._external_target(output)
        files = self.build_files(summary, proposal)
        hs._publish(files, output, lambda p: self.verify(p, summary, proposal))
        return hs._strict_json(files[hs.SUMMARY_FILE])

    def verify(self, output: Path, summary: Path, proposal: Path) -> dict:
        qp._separate(output, summary, proposal)
        qp._packet_paths(output)
        files = hs._read_tree(output)
        if files != self.build_files(summary, proposal):
            raise hs.HandoffError(
                "02H metadata-only replay differs; no upstream verification performed"
            )
        return hs._strict_json(files[hs.SUMMARY_FILE])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "replay"))
    for name in ("output", "summary", "proposal"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        adapter = ScientificProtocolPreflight()
        method = adapter.build if args.command == "build" else adapter.verify
        result = method(args.output, args.summary, args.proposal)
    except (ValueError, OSError, KeyError, TypeError, RuntimeError) as exc:
        print(f"PROTOCOL_PREFLIGHT_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {k: result[k] for k in ("content_sha256", "verification_class", "science_status")}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
