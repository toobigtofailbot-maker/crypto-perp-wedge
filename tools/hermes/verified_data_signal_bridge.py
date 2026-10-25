"""Manual offline 02G technical compilation; no scientific or execution authority."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from tools.hermes import queue_input_preparation as qp
from tools.research_runner import spec_signal_compiler as compiler

de, hs, sr = qp.de, qp.hs, qp.sr
SCHEMA = "cpw_hermes_verified_data_signal_bridge_v1"
BASE_SHA = "49d39b77f831d3ba3537b1b5ff4b294291a79005"
FIXTURE = "SOFTWARE_FIXTURE_PROOF"
OHLCV = ("open", "high", "low", "close", "volume")


def _fixture_parent(shared: dict, workspace: Path) -> bool:
    """A label is insufficient: independently recognize the entire fixed fake corpus."""
    parent = shared.get("15m")
    if not parent or parent["local"]["status"] != "LOCAL_BYTES_VERIFIED":
        return False
    path = de._local(workspace, parent["path"])
    frame = de.pd.read_csv(path, dtype=str, keep_default_na=False)
    from tools.data.import_binance_usdtm_15m import OUTPUT_COLUMNS

    if list(frame.columns) != list(OUTPUT_COLUMNS) or frame.empty:
        return False
    index = de.pd.date_range("2020-01-01", periods=len(frame), freq="15min", tz="UTC")
    for n, row in enumerate(frame.to_dict("records")):
        ms = index[n].value // 1_000_000
        expected = {
            "open_time_ms": str(ms),
            "open_time": index[n].isoformat().replace("+00:00", "Z"),
            "open": "100",
            "high": "102",
            "low": "99",
            "close": "101",
            "volume": "10",
            "close_time_ms": str(ms + 899999),
            "quote_asset_volume": "1000",
            "num_trades": "4",
            "taker_buy_base_vol": "6",
            "taker_buy_quote_vol": "600",
            "ignore": "0",
        }
        if row != expected:
            return False
    return True


def _warm(frame, spec: dict, assignment: dict) -> bool:
    # Reuse native operand evaluation, including nested compositions and lagged primitives.
    context = compiler._CompileContext(
        strategy_spec=spec,
        variant_assignment=assignment,
        ohlcv=frame,
        catalog=compiler._load_default_catalog(),
    )
    valid = de.pd.Series(True, index=frame.index)

    def visit(value):
        nonlocal valid
        if isinstance(value, dict):
            if "operand_type" in value:
                resolved = compiler._resolve_operand(value, context)
                if isinstance(resolved, de.pd.Series):
                    valid &= resolved.notna() & resolved.map(lambda x: math.isfinite(float(x)))
            else:
                for child in value.values():
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(spec)
    atr = compiler._atr_stop_config(spec, context)
    if atr:
        valid &= atr.atr_series.notna()
    # At least two consecutive evaluable completed bars; never pad indicator warmup.
    return len(valid) >= 2 and bool(valid.iloc[-2:].all())


class VerifiedDataSignalBridge:
    def __init__(self, root: Path = de.ROOT):
        self.preparation = qp.QueueInputPreparation(root)

    def build_files(
        self,
        preparation_dir: Path,
        evidence_dir: Path,
        chain: tuple,
        workspace: Path,
        *,
        designation: Path | None = None,
        **options,
    ) -> dict[str, bytes]:
        upstream = self.preparation.verify(
            preparation_dir, evidence_dir, chain, workspace, **options
        )
        inputs = hs._read_tree(preparation_dir)
        designation_raw = None
        selected = {}
        if designation is not None:
            designation_raw = de._local(
                designation.absolute().parent, designation.name
            ).read_bytes()
            selected = hs._strict_json(designation_raw)
            if not isinstance(selected, dict) or set(selected) != {
                "purpose",
                "label",
                "source_02f",
                "windows",
                "fixture_recipe",
            }:
                raise hs.HandoffError(
                    "designation requires exact purpose/label/source/windows/recipe"
                )
            if (
                selected["purpose"] != "ENGINEERING_VALIDATION_ONLY"
                or selected["label"] not in (FIXTURE, "HISTORICAL")
                or selected["source_02f"] != upstream["content_sha256"]
            ):
                raise hs.HandoffError("designation identity or purpose differs")
            windows = selected["windows"]
            if not isinstance(windows, dict) or set(windows) - {
                i["idea_id"] for i in upstream["ideas"]
            }:
                raise hs.HandoffError("designation contains unknown ideas")
            for window in windows.values():
                if not isinstance(window, dict) or set(window) != {
                    "start",
                    "end",
                    "timeframe",
                    "source_sha256",
                }:
                    raise hs.HandoffError("designation window requires exact source identity")
                qp._window({k: window[k] for k in ("start", "end")})
        fixture = selected.get("label") == FIXTURE
        if fixture and (
            selected["fixture_recipe"] != "fixed_15m_v1"
            or not _fixture_parent(upstream["shared_sources"], workspace)
        ):
            raise hs.HandoffError(
                "fixture designation does not prove fixed synthetic parent values"
            )
        built = hs._read_tree(chain[1])
        built_summary = hs._strict_json(built[hs.SUMMARY_FILE])
        frames = {}
        ideas = []
        for entry, draft_entry in zip(upstream["ideas"], built_summary["ideas"], strict=True):
            retained = hs._strict_json(inputs[entry["receipt"]])
            result = {
                "idea_id": entry["idea_id"],
                "index": entry["index"],
                "source_02e_recheck": retained,
                "source_02c": hs._strict_json(built[draft_entry["receipt"]]),
                "science_status": "NOT_READY",
                "search_contract_status": "NOT_ISSUABLE",
                "semantic_review": "REQUIRES_REVIEW_NO_SEMANTIC_EQUIVALENCE_ASSERTED",
                "compilations": [],
                "status": "NOT_READY_NO_ELIGIBLE_DRAFT",
            }
            if draft_entry["status"] == hs.DRAFTED:
                for draft in draft_entry["drafts"]:
                    spec = hs._strict_json(built[draft["file"]])
                    check = self._compile(
                        spec, draft, retained, upstream, workspace, selected, fixture, frames
                    )
                    result["compilations"].append(check)
                statuses = [c["status"] for c in result["compilations"]]
                result["status"] = (
                    "PASS"
                    if statuses and all(s == "PASS" for s in statuses)
                    else next((s for s in statuses if s != "PASS"), "NOT_READY_NO_ELIGIBLE_DRAFT")
                )
            result["next_human_action"] = (
                "review draft semantics and retained scientific/data gaps; no scientific execution"
            )
            ideas.append(result)
        # Integrity recheck after native calls also detects concurrent mutations of upstreams.
        if (
            self.preparation.verify(preparation_dir, evidence_dir, chain, workspace, **options)
            != upstream
        ):
            raise hs.HandoffError("02F changed during compilation")
        if (
            designation is not None
            and de._local(designation.absolute().parent, designation.name).read_bytes()
            != designation_raw
        ):
            raise hs.HandoffError("designation changed during compilation")
        summary = hs._hashed(
            {
                "schema_version": SCHEMA,
                "authority": hs.AUTHORITY,
                "repo_sha": upstream["repo_sha"],
                "base_sha": BASE_SHA,
                "source_02f": upstream["content_sha256"],
                "source_packet_hashes": {n: de.dc._sha256_bytes(v) for n, v in inputs.items()},
                "designation_sha256": de.dc._sha256_bytes(designation_raw)
                if designation_raw
                else None,
                "label": FIXTURE if fixture else "TECHNICAL_COMPILATION_ONLY",
                "limitation": "TECHNICAL_COMPILATION_ONLY; no scientific admission or execution authority",
                "science_status": "NOT_READY",
                "search_contract_status": "NOT_ISSUABLE",
                "investigation_queue": upstream["investigation_queue"],
                "ideas": ideas,
            }
        )
        return self.preparation.evidence.readiness.handoff._guard(
            hs._render({hs.SUMMARY_FILE: hs._json_bytes(summary)})
        )

    def _compile(self, spec, draft, retained, upstream, workspace, selected, fixture, frames):
        params = {p["name"]: p["default"] for p in spec["free_parameters"]["parameters"]}
        result = {
            "draft": draft,
            "assignment": params,
            "parameters": spec["free_parameters"],
            "compiler": "tools.research_runner.spec_signal_compiler.compile_signal",
            "compiler_repo_sha": upstream["repo_sha"],
            "status": "NOT_READY_VERIFIED_INPUTS_MISSING",
            "source_bindings": retained["bases"],
            "feature_bindings": retained["features"],
        }
        if any(f["status"] == "NOT_READY" for f in retained["features"]):
            result["status"] = "NOT_READY_REQUIRED_FEATURE_EVIDENCE"
            return result
        tf = spec["timeframe_and_data"]["primary_timeframe"]
        bases = retained["bases"]
        if len(bases) != 1 or bases[0]["timeframe"] != tf:
            result["status"] = "NOT_READY_NATIVE_SINGLE_TIMEFRAME_REQUIRED"
            return result
        base = bases[0]
        shared = upstream["shared_sources"][tf]
        if base["local"].get("window_status") != "WINDOW_VERIFIED" or (
            "parent" in shared["catalog"] and not shared["parent_proof"]
        ):
            return result
        window = selected.get("windows", {}).get(retained["idea_id"])
        if window is not None:
            expected = {
                **retained["requested_window"],
                "timeframe": tf,
                "source_sha256": base["local"]["sha256"],
            }
            if window != expected:
                raise hs.HandoffError("technical window/source differs from verified 02F window")
        # No native partition certificate is established by 02F/02E. Fail closed for history.
        if window is None or not fixture or tf not in ("15m", "30m", "1h", "4h"):
            result["status"] = "NOT_READY_NON_HOLDOUT_WINDOW_UNVERIFIED"
            return result
        result["technical_window"] = window
        names = sorted(qp.TAKER & {f["feature"] for f in retained["features"]})
        key = (tf, tuple(names))
        if key not in frames:
            path = de._local(workspace, shared["path"])
            local, raw = de.inspect_local(shared["catalog"], path, retained["requested_window"])
            frame = raw.loc[:, list(OHLCV)].astype(float)
            if names:
                identity = shared["catalog"].get("slice_identity", {}).get("data_slice_identity")
                if identity is None:
                    identity = qp.taker.CANONICAL_KLINE_PARENT_CONFIG[tf]["data_slice_identity"]
                feature = shared["features"]
                joined = de.ft.resolve_research_feature_table(
                    base_frame=frame,
                    base_input_path=path,
                    base_data_slice_identity=identity,
                    base_normalized_sha256=local["sha256"],
                    base_market_identity={
                        "venue": "Binance",
                        "market_type": "USD-M perpetual",
                        "symbol": "BTCUSDT",
                    },
                    base_timeframe=tf,
                    base_coverage_start_utc_inclusive=de.pd.Timestamp(local["coverage_start"])
                    .isoformat(timespec="milliseconds")
                    .replace("+00:00", "Z"),
                    base_coverage_end_utc_exclusive=de.pd.Timestamp(local["coverage_end_exclusive"])
                    .isoformat(timespec="milliseconds")
                    .replace("+00:00", "Z"),
                    feature_manifest_path=de._local(workspace, feature["feature_manifest"]),
                    feature_csv_path=de._local(workspace, feature["feature_csv"]),
                    requested_feature_names=names,
                )
                frame = joined.joined_frame
            frames[key] = frame
        frame = frames[key]
        frame = frame.loc[
            (frame.index >= de.pd.Timestamp(window["start"]))
            & (frame.index < de.pd.Timestamp(window["end"]))
        ]
        assignment = {"parameter_values": params}
        try:
            if not _warm(frame, spec, assignment):
                result["status"] = "NOT_READY_GENUINE_WARMUP_REQUIRED"
                return result
            signal = compiler.compile_signal(spec, assignment, frame)
        except (compiler.SpecSignalCompilerError, ValueError, KeyError, TypeError) as exc:
            result.update(status="NOT_READY_NATIVE_COMPILER", reason=str(exc))
            return result
        if (
            not signal.index.equals(frame.index)
            or len(signal) != len(frame)
            or signal.isna().any()
            or not signal.isin((-1.0, 0.0, 1.0)).all()
        ):
            raise hs.HandoffError("native compiler returned an invalid signal series")
        result.update(
            status="PASS",
            rows=len(signal),
            signal_sha256=de.dc._sha256_bytes(signal.to_numpy(dtype="<f8").tobytes()),
            signal_encoding="little-endian float64 in verified index order",
        )
        return result

    def build(
        self,
        output: Path,
        preparation_dir: Path,
        evidence_dir: Path,
        chain: tuple,
        workspace: Path,
        **options,
    ):
        for path in (
            preparation_dir,
            evidence_dir,
            *chain,
            workspace,
            *[p for p in options.values() if isinstance(p, Path)],
        ):
            qp._separate(output, path)
        qp._external_target(output)
        files = self.build_files(preparation_dir, evidence_dir, chain, workspace, **options)
        hs._publish(
            files,
            output,
            lambda p: self.verify(p, preparation_dir, evidence_dir, chain, workspace, **options),
        )
        return hs._strict_json(files[hs.SUMMARY_FILE])

    def verify(self, output: Path, *inputs, **options):
        for path in (
            *inputs[:2],
            *inputs[2],
            inputs[3],
            *[p for p in options.values() if isinstance(p, Path)],
        ):
            qp._separate(output, path)
        qp._packet_paths(output)
        files = hs._read_tree(output)
        summary = hs._strict_json(files[hs.SUMMARY_FILE])
        hs._check_hash(summary, SCHEMA)
        if files != self.build_files(*inputs, **options):
            raise hs.HandoffError("02G replay did not reproduce exact bytes")
        return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "replay"))
    for name in (
        "output",
        "preparation-dir",
        "evidence-dir",
        "readiness-dir",
        "built-dir",
        "prepared-dir",
        "responses-dir",
        "workspace",
    ):
        parser.add_argument("--" + name, required=True, type=Path)
    for name in ("designation", "local-root", "inventory", "requests", "evidence-local-root"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    options = {
        key: getattr(args, key)
        for key in (
            "designation",
            "local_root",
            "inventory",
            "requests",
            "evidence_local_root",
            "materialize",
        )
    }
    try:
        adapter = VerifiedDataSignalBridge()
        chain = (args.readiness_dir, args.built_dir, args.prepared_dir, args.responses_dir)
        method = adapter.build if args.command == "build" else adapter.verify
        result = method(
            args.output, args.preparation_dir, args.evidence_dir, chain, args.workspace, **options
        )
    except (ValueError, OSError, KeyError, TypeError, RuntimeError, de.dc.ConsumerError) as exc:
        print(f"VERIFIED_DATA_SIGNAL_BRIDGE_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(json.dumps({k: result[k] for k in ("content_sha256", "science_status")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
