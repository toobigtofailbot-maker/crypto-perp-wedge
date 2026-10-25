"""Manual 02E data investigation; catalog metadata never grants science authority."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from tools.data import research_feature_table as ft
from tools.data import validate_binance_usdtm_15m as d3
from tools.hermes import discovery_intent_consumer as dc
from tools.hermes import intent_strategy_spec_handoff as hs
from tools.hermes import science_readiness as sr

SCHEMA = "cpw_hermes_data_evidence_batch_v1"
TIMEFRAMES = ("15m", "30m", "1h", "4h", "1d")
AVAILABILITY = "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
INDICATORS = "research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json"
SCIENCE_GAPS = (
    "fees_slippage_funding_pnl",
    "genuine_preregistration",
    "frozen_search_domains",
    "oos_unexposed_holdout",
    "purge_embargo",
    "multiple_testing",
    "cumulative_trial_lineage",
)


def _relative(value: str) -> str:
    value = value.replace("\\", "/")
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or any(p in ("..", ".", "") for p in value.split("/"))
        or ":" in value
    ):
        raise hs.HandoffError("unsafe relative path")
    return path.as_posix()


def _local(root: Path, relative: str) -> Path:
    sr._check_paths(root)
    path = root.absolute() / _relative(relative)
    sr._check_paths(path)
    if any(
        dc._is_link(cursor)
        for cursor in (path, *path.parents)
        if cursor.is_symlink() or cursor.exists()
    ):
        raise hs.HandoffError("local source traverses a symlink or junction")
    if not path.resolve().is_relative_to(root.resolve()):
        raise hs.HandoffError("local source escapes admitted root")
    if path.exists() and (not path.is_file() or path.stat().st_nlink != 1):
        raise hs.HandoffError("local source must be an ordinary unlinked file")
    return path


def inspect_local(catalog: dict, path: Path, window: dict | None) -> tuple[dict, Any]:
    """Check exact manifest bytes, native 15m semantics and complete explicit grid."""
    if not path.exists():
        return {"status": "NOT_READY", "gaps": ["LOCAL_SOURCE_MISSING"]}, None
    digest = ft._sha256(path)
    expected = catalog.get("normalized", catalog)
    if digest != expected["sha256"].removeprefix("sha256:"):
        raise hs.HandoffError("local source digest differs from committed canonical manifest")
    frame = (
        pd.read_parquet(path)
        if path.suffix == ".parquet"
        else pd.read_csv(path, dtype=str, keep_default_na=False)
    )
    timeframe = catalog["timeframe"]
    native = "COMMITTED_VALIDATION_REPORT_ONLY_NO_PHYSICAL_REDERIVATION"
    gaps = []
    if timeframe == "15m":
        _, errors = d3.validate_frame(frame)
        if errors:
            raise hs.HandoffError("native D3 validation failed: " + "; ".join(errors))
        native = "tools.data.validate_binance_usdtm_15m.validate_frame"
    elif timeframe == "1d":
        from tools.data.register_binance_usdtm_1d_lineage import build_lineage

        build_lineage(path, expected_sha256=digest)
        native = "tools.data.register_binance_usdtm_1d_lineage.build_lineage"
    else:
        gaps.append("PHYSICAL_PARENT_REDERIVATION_NOT_PERFORMED")
    delta = ft._interval_delta(timeframe)
    opens = pd.to_numeric(frame["open_time_ms"], errors="raise")
    closes = pd.to_numeric(frame["close_time_ms"], errors="raise")
    index = pd.DatetimeIndex(pd.to_datetime(opens, unit="ms", utc=True))
    cadence = int(delta.total_seconds() * 1000)
    if (
        index.empty
        or index.has_duplicates
        or not index.is_monotonic_increasing
        or (opens % cadence != 0).any()
        or (closes != opens + cadence - 1).any()
        or not index.equals(pd.date_range(index[0], index[-1], freq=delta))
    ):
        raise hs.HandoffError("local bars violate cadence, uniqueness or completed-bar timing")
    bounds = catalog.get("range", catalog.get("coverage"))
    start = pd.Timestamp(bounds.get("start_utc", bounds.get("start_open_utc")))
    end = pd.Timestamp(bounds.get("end_utc", bounds.get("end_open_utc"))) + delta
    if len(frame) != bounds["row_count"] or index[0] != start or index[-1] + delta != end:
        raise hs.HandoffError("local bars do not cover the complete committed manifest")
    result = {
        "status": "LOCAL_BYTES_VERIFIED",
        "sha256": digest,
        "rows": len(frame),
        "native_validation": native,
        "gaps": gaps,
        "window_status": "NOT_READY",
        "completed_bar_available_at": "exclusive bar close",
        "coverage_start": str(start),
        "coverage_end_exclusive": str(end),
    }
    if window is None:
        gaps.append("WINDOW_MISSING")
    else:
        if set(window) != {"start", "end"}:
            raise hs.HandoffError("window requires exactly start/end")
        a, b = (pd.Timestamp(window[k]) for k in ("start", "end"))
        if pd.isna(a) or pd.isna(b) or a.tzinfo is None or b.tzinfo is None or a >= b:
            raise hs.HandoffError("window must be explicit timezone-aware increasing [start,end)")
        result["requested_window"] = window
        if a < start or b > end or a.value % delta.value or b.value % delta.value:
            gaps.append("WINDOW_OUTSIDE_OR_UNALIGNED")
        else:
            selected = index[(index >= a) & (index < b)]
            if not selected.equals(pd.date_range(a, b, freq=delta, inclusive="left")):
                raise hs.HandoffError("requested window contains missing bars")
            result.update(window_status="WINDOW_VERIFIED", window_rows=len(selected))
    if ft._sha256(path) != digest:
        raise hs.HandoffError("local source changed during validation")
    frame.index = index
    return result, frame


def assess_feature(feature: str, availability: list[dict], indicators: list[dict]) -> dict:
    rows = [r for r in availability if r["feature_name"] == feature]
    indicator = [r for r in indicators if r["indicator_id"] == feature]
    kind = (
        "OHLCV_BUILTIN"
        if feature in ("ohlcv", "open", "high", "low", "close", "volume")
        else "INDICATOR_CATALOG"
        if indicator
        else "CONDITIONAL_HISTORY"
        if any(r["canonical_full_history_allowed"] == "conditional" for r in rows)
        else "RECENT_SNAPSHOT_VENDOR_ONLY"
        if rows
        else "UNRECOGNIZED"
    )
    return {
        "feature": feature,
        "kind": kind,
        "availability_rows": rows,
        "indicator_rows": indicator,
        "status": "NOT_READY",
    }


def inspect_features(
    catalog: dict, local: dict, frame: Any, path: Path, manifest: Path, csv: Path, names: list[str]
) -> dict:
    identity = catalog.get("slice_identity", {}).get("data_slice_identity")
    if identity is None:
        from tools.data.materialize_takerflow_features import CANONICAL_KLINE_PARENT_CONFIG

        identity = CANONICAL_KLINE_PARENT_CONFIG[catalog["timeframe"]]["data_slice_identity"]
    manifest_sha = ft._sha256(manifest)
    csv_sha = ft._sha256(csv)
    joined = ft.resolve_research_feature_table(
        base_frame=frame,
        base_input_path=path,
        base_data_slice_identity=identity,
        base_normalized_sha256=local["sha256"],
        base_market_identity={
            "venue": "Binance",
            "market_type": "USD-M perpetual",
            "symbol": "BTCUSDT",
        },
        base_timeframe=catalog["timeframe"],
        base_coverage_start_utc_inclusive=pd.Timestamp(local["coverage_start"])
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
        base_coverage_end_utc_exclusive=pd.Timestamp(local["coverage_end_exclusive"])
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
        feature_manifest_path=manifest,
        feature_csv_path=csv,
        requested_feature_names=names,
    )
    if ft._sha256(manifest) != manifest_sha or ft._sha256(csv) != csv_sha:
        raise hs.HandoffError("feature inputs changed during validation")
    return {
        "status": "LOCAL_FEATURE_TABLE_VERIFIED",
        "identity": joined.feature_table_identity,
        "manifest_sha256": manifest_sha,
        "csv_sha256": csv_sha,
    }


class DataEvidenceResolution:
    def __init__(self, root: Path = ROOT):
        self.readiness = sr.ScienceReadiness(root)
        self.root = root
        self.sources: dict[str, dict] = {}

    def _metadata(self, relative: str) -> Any:
        relative = _relative(relative)
        raw = self.readiness.git.blob(relative)
        if raw is None:
            raise hs.HandoffError("required committed metadata missing: " + relative)
        self.sources[relative] = {
            "repo_sha": self.readiness.identity.repo_sha,
            "sha256": dc._sha256_bytes(raw),
        }
        return hs._strict_json(raw) if relative.endswith(".json") else raw.decode("utf-8")

    def _catalog(self, timeframe: str) -> dict:
        if timeframe not in TIMEFRAMES:
            raise hs.HandoffError("unknown canonical timeframe")
        base = f"research/data_slices/binance_usdtm_btcusdt_{timeframe}/binance_usdtm_btcusdt_{timeframe}_20200101_20260411"
        catalog = self._metadata(base + ".catalog_slice.json")
        for key in ("validation_report", "derivation_report"):
            if key in catalog:
                ref = catalog[key]
                self._metadata(ref["path"])
                if self.sources[_relative(ref["path"])]["sha256"] != ref["sha256"]:
                    raise hs.HandoffError("committed report digest mismatch")
        if "parent" in catalog:
            parent = catalog["parent"]
            d4 = self._catalog("15m")
            if (
                parent["data_slice_identity"] != d4["slice_identity"]["data_slice_identity"]
                or parent["normalized_sha256"] != d4["normalized"]["sha256"]
                or parent["validation_report_sha256"] != d4["validation_report"]["sha256"]
                or parent["dataset_id"] != d4["dataset_id"]
                or _relative(parent["catalog_slice_path"])
                != _relative(base.replace(timeframe, "15m") + ".catalog_slice.json")
            ):
                raise hs.HandoffError("canonical parent differs from D4")
        return catalog

    def build_files(
        self,
        readiness_dir: Path,
        built_dir: Path,
        prepared_dir: Path,
        responses_dir: Path,
        requests: Path | None = None,
        local_root: Path | None = None,
    ) -> dict[str, bytes]:
        self.sources = {}
        upstream = self.readiness.verify(readiness_dir, built_dir, prepared_dir, responses_dir)
        raw_inputs = hs._read_tree(readiness_dir)
        requested = {}
        request_hash = None
        if requests is not None:
            sr._check_paths(requests)
            requests = _local(requests.absolute().parent, requests.name)
            raw = requests.read_bytes()
            requested = hs._strict_json(raw)
            request_hash = dc._sha256_bytes(raw)
        if not isinstance(requested, dict) or set(requested) - {
            i["idea_id"] for i in upstream["ideas"]
        }:
            raise hs.HandoffError("unknown idea in explicit requests")
        if local_root is not None:
            sr._check_paths(local_root)
            if not local_root.is_dir():
                raise hs.HandoffError("admitted local root must exist")
        availability = self._metadata(AVAILABILITY)["entries"]
        indicators = self._metadata(INDICATORS)["entries"]
        self._metadata("docs/decisions.md")
        files, ideas, queue = {}, [], []
        built = hs._read_tree(built_dir)
        for entry in upstream["ideas"]:
            source = hs._strict_json(raw_inputs[entry["receipt"]])
            native = source["source_native_intent"] or {}
            intent = native
            spec_data = [
                hs._strict_json(built[c["draft"]["file"]])["timeframe_and_data"]
                for c in source["technical_checks"]
            ]
            timeframes = list(
                dict.fromkeys(
                    [intent.get("primary_timeframe")]
                    + [d["primary_timeframe"] for d in spec_data]
                    + [tf for d in spec_data for tf in d.get("confirmation_timeframes", [])]
                )
            )
            timeframes = list(
                dict.fromkeys(
                    [tf for tf in timeframes if tf]
                    + [
                        r["timeframe"]
                        for d in spec_data
                        for r in d.get("host_data_refs", [])
                        if r.get("timeframe")
                    ]
                )
            )
            features = list(
                dict.fromkeys(
                    intent.get("required_data_features", [])
                    + [r["field"] for d in spec_data for r in d.get("host_data_refs", [])]
                )
            )
            refs = [r for d in spec_data for r in d.get("host_data_refs", [])]
            request = requested.get(entry["idea_id"], {})
            if not isinstance(request, dict) or set(request) - {"window", "sources"}:
                raise hs.HandoffError("unknown request fields")
            selections = request.get("sources", {})
            if not isinstance(selections, dict) or set(selections) - set(timeframes):
                raise hs.HandoffError("source selection is not an idea timeframe")
            feature_results = [assess_feature(f, availability, indicators) for f in features]
            bases, gaps = [], []
            if request.get("window") is not None:
                window = request["window"]
                if not isinstance(window, dict) or set(window) != {"start", "end"}:
                    raise hs.HandoffError("window requires exactly start/end")
            if not timeframes:
                gaps.append(
                    {"code": "NATIVE_DATA_REQUIREMENTS_MISSING", "field": "source_native_intent"}
                )
            for tf in timeframes:
                catalog = self._catalog(tf)
                expected = catalog.get("normalized", catalog)
                relative = _relative(expected["path"])
                selection = selections.get(tf, {})
                if not isinstance(selection, dict) or set(selection) - {
                    "path",
                    "feature_manifest",
                    "feature_csv",
                }:
                    raise hs.HandoffError("unknown source selection fields")
                if selection.get("path", relative) != relative:
                    raise hs.HandoffError(
                        "diagnostic or alternate source cannot replace canonical base"
                    )
                local = {"status": "NOT_READY", "gaps": ["LOCAL_ROOT_NOT_SUPPLIED"]}
                frame = None
                if local_root is not None:
                    path = _local(local_root, relative)
                    local, frame = inspect_local(catalog, path, request.get("window"))
                    local["path"] = relative
                if request.get("window") is None and "WINDOW_MISSING" not in local["gaps"]:
                    local["gaps"].append("WINDOW_MISSING")
                feature_table = {"status": "NOT_READY", "gap": "EXACT_FEATURE_TABLE_NOT_SUPPLIED"}
                taker = sorted(
                    set(features)
                    & {"taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio"}
                )
                if ("feature_manifest" in selection) != ("feature_csv" in selection):
                    raise hs.HandoffError("feature manifest and CSV must be supplied together")
                if "feature_manifest" in selection:
                    if local_root is None:
                        raise hs.HandoffError("feature input requires admitted local root")
                    manifest_path = _local(local_root, selection["feature_manifest"])
                    feature_path = _local(local_root, selection["feature_csv"])
                    if not manifest_path.exists() or not feature_path.exists() or frame is None:
                        feature_table["gap"] = "FEATURE_OR_PARENT_BYTES_MISSING"
                    elif taker:
                        feature_table = inspect_features(
                            catalog, local, frame, path, manifest_path, feature_path, taker
                        )
                    else:
                        feature_table["gap"] = "NO_NATIVE_CONSUMER_FOR_SUPPLIED_FEATURES"
                if taker and feature_table["status"] == "NOT_READY":
                    gaps.append(
                        {
                            "code": feature_table["gap"],
                            "timeframe": tf,
                            "features": taker,
                            "parent_path": relative,
                        }
                    )
                for gap in local["gaps"]:
                    gaps.append(
                        {
                            "code": gap,
                            "timeframe": tf,
                            "path": relative,
                            "window": request.get("window"),
                        }
                    )
                bases.append(
                    {
                        "timeframe": tf,
                        "metadata_status": "REPOSITORY_METADATA_VERIFIED_ONLY",
                        "catalog": catalog,
                        "local": local,
                        "feature_table": feature_table,
                        "source_authority": "D2-021_CANONICAL_BASE",
                        "diagnostic_direct_source_is_authority": False,
                    }
                )
            for f in feature_results:
                if (
                    f["kind"] in ("OHLCV_BUILTIN", "INDICATOR_CATALOG")
                    and bases
                    and all(b["local"].get("window_status") == "WINDOW_VERIFIED" for b in bases)
                ):
                    f["status"] = "LOCAL_BASE_WINDOW_VERIFIED_WARMUP_NOT_ESTABLISHED"
                elif (
                    f["feature"]
                    in {"taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio"}
                    and bases
                    and all(
                        b["feature_table"]["status"] == "LOCAL_FEATURE_TABLE_VERIFIED"
                        and b["local"].get("window_status") == "WINDOW_VERIFIED"
                        for b in bases
                    )
                ):
                    f["status"] = "LOCAL_FEATURE_TABLE_VERIFIED"
                else:
                    gaps.append(
                        {
                            "code": "FEATURE_EVIDENCE_REQUIRED",
                            "feature": f["feature"],
                            "kind": f["kind"],
                            "field": "exact source/feature manifest and requested window",
                        }
                    )
            gaps.extend(
                {"code": "SCIENTIFIC_PROTOCOL_MISSING", "field": gap} for gap in SCIENCE_GAPS
            )
            retained = {
                k: source["source_02b"].get(k)
                for k in (
                    "fingerprint",
                    "critic_assessment",
                    "original_memory",
                    "refreshed_memory",
                    "source_failures",
                    "block_reasons",
                    "missing_evidence",
                    "source_claims",
                )
            }
            result = {
                "index": entry["index"],
                "idea_id": entry["idea_id"],
                "status": entry["status"],
                "science_status": "NOT_READY",
                "source_02d": entry,
                "retained": retained,
                "memory": source["memory"],
                "native_research_memory": intent.get("research_memory"),
                "required_data_refs": refs,
                "bases": bases,
                "requested_window": request.get("window"),
                "upstream_next_investigations": source["next_legal_investigation"],
                "features": feature_results,
                "scientific_boundary": {g: "NOT_READY" for g in SCIENCE_GAPS},
                "next_investigations": gaps,
            }
            name = entry["receipt"]
            files[name] = hs._json_bytes(result)
            ideas.append(
                {
                    "index": entry["index"],
                    "idea_id": entry["idea_id"],
                    "status": entry["status"],
                    "receipt": name,
                    "receipt_sha256": dc._sha256_bytes(files[name]),
                }
            )
            queue.extend({"idea_id": entry["idea_id"], **gap} for gap in gaps)
        summary = hs._hashed(
            {
                "schema_version": SCHEMA,
                "authority": hs.AUTHORITY,
                "repo_sha": self.readiness.identity.repo_sha,
                "source_02d": upstream["content_sha256"],
                "input_hashes": {n: dc._sha256_bytes(v) for n, v in sorted(raw_inputs.items())},
                "requests_sha256": request_hash,
                "metadata_sources": self.sources,
                "ideas": ideas,
                "counts": upstream["counts"],
                "science_counts": {"NOT_READY": len(ideas)},
                "investigation_queue": queue,
                "queue_order": "source idea order then data/feature/science gaps; no profitability ranking",
                "limitations": [
                    "hashes prove bytes, not source truth or Hermes authorship",
                    "no OOS or holdout selected; no experiment or scientific authority",
                    "indicator warmup and physical parent rederivation are not established",
                ],
            }
        )
        files[hs.SUMMARY_FILE] = hs._json_bytes(summary)
        self.readiness._head()
        return self.readiness.handoff._guard(hs._render(files))

    def verify(self, output: Path, *inputs, **kwargs) -> dict:
        sr._check_paths(output)
        files = hs._read_tree(output)
        summary = hs._strict_json(files[hs.SUMMARY_FILE])
        hs._check_hash(summary, SCHEMA)
        if files != self.build_files(*inputs, **kwargs):
            raise hs.HandoffError("02E replay did not reproduce exact bytes")
        return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "replay"))
    for name in ("readiness-dir", "built-dir", "prepared-dir", "responses-dir", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--requests", type=Path)
    parser.add_argument("--local-root", type=Path)
    args = parser.parse_args(argv)
    try:
        sr._check_paths(args.output)
        adapter = DataEvidenceResolution()
        inputs = (args.readiness_dir, args.built_dir, args.prepared_dir, args.responses_dir)
        options = {"requests": args.requests, "local_root": args.local_root}
        if args.command == "build":
            hs._publish(
                adapter.build_files(*inputs, **options),
                args.output,
                lambda p: adapter.verify(p, *inputs, **options),
            )
        summary = adapter.verify(args.output, *inputs, **options)
    except (ValueError, OSError, KeyError, TypeError, dc.ConsumerError) as exc:
        print(f"DATA_EVIDENCE_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(json.dumps({k: summary[k] for k in ("content_sha256", "counts", "science_counts")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
