"""Manual offline 02F queue consumer; prepared inputs grant no scientific authority."""

from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import sys
from pathlib import Path

from tools.data import materialize_takerflow_features as taker
from tools.data import resample_binance_usdtm_15m_to_4h as four
from tools.data import resample_binance_usdtm_15m_to_30m_1h as short
from tools.hermes import data_evidence_resolution as de
from tools.hermes import intent_strategy_spec_handoff as hs
from tools.hermes import science_readiness as sr

SCHEMA = "cpw_hermes_queue_input_preparation_v1"
TAKER = {"taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio"}


def _snapshot(root: Path) -> dict:
    """Stream corpus hashes separately from the small, bounded Hermes packet."""
    sr._check_paths(root)
    if not root.is_dir():
        raise hs.HandoffError("workspace must be an ordinary directory")
    return {
        p.relative_to(root).as_posix(): de.ft._sha256(
            de._local(root, p.relative_to(root).as_posix())
        )
        for p in sorted(root.rglob("*"))
        if not p.is_dir() or de.dc._is_link(p)
    }


def _separate(*paths: Path) -> None:
    for path in paths:
        sr._check_paths(path)
    resolved = [p.resolve() for p in paths]
    for i, path in enumerate(resolved):
        if any(path.is_relative_to(p) or p.is_relative_to(path) for p in resolved[i + 1 :]):
            raise hs.HandoffError("input, workspace and output directories must be disjoint")


def _external_target(path: Path) -> None:
    sr._check_paths(path)
    de.dc._check_output_target(path)
    if any((parent / ".git").exists() for parent in path.absolute().parents):
        raise hs.HandoffError("output must be external to every Git checkout")


def _packet_paths(root: Path) -> None:
    sr._check_paths(root)
    for relative in de.dc._ordinary_tree(root):
        de._local(root, relative)


def _window(window: dict) -> dict:
    if not isinstance(window, dict) or set(window) != {"start", "end"}:
        raise hs.HandoffError("window requires exactly start/end")
    a, b = (de.pd.Timestamp(window[k]) for k in ("start", "end"))
    if de.pd.isna(a) or de.pd.isna(b) or a.tzinfo is None or b.tzinfo is None or a >= b:
        raise hs.HandoffError("window must be explicit timezone-aware increasing [start,end)")
    return window


def _derived_bytes(parent: Path, timeframe: str) -> bytes:
    # Only the native pure resamplers run; their tracked-path CLI writers never run.
    rows = short._read_csv(parent)
    result, _ = (
        four.resample_rows(rows)
        if timeframe == "4h"
        else short.resample_rows(rows, short.TARGETS[timeframe])
    )
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=short.OUTPUT_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(result)
    return target.getvalue().encode("utf-8")


class QueueInputPreparation:
    def __init__(self, root: Path = de.ROOT):
        self.evidence = de.DataEvidenceResolution(root)

    def _evaluate(
        self,
        evidence_dir: Path,
        chain: tuple,
        workspace: Path,
        *,
        local_root: Path | None,
        inventory: Path | None,
        requests: Path | None,
        materialize: bool,
        prepare: bool,
        evidence_local_root: Path | None = None,
    ) -> dict[str, bytes]:
        for directory in (evidence_dir, *chain):
            _packet_paths(directory)
        upstream = self.evidence.verify(
            evidence_dir, *chain, requests=requests, local_root=evidence_local_root
        )
        if local_root is not None:
            sr._check_paths(local_root)
            if not local_root.is_dir():
                raise hs.HandoffError("admitted local source root must exist")
        source_files = hs._read_tree(evidence_dir)
        supplied = {}
        inventory_sha = None
        if inventory is not None:
            raw = de._local(inventory.absolute().parent, inventory.name).read_bytes()
            supplied = hs._strict_json(raw)
            inventory_sha = de.dc._sha256_bytes(raw)
        if not isinstance(supplied, dict) or set(supplied) - {"windows", "features"}:
            raise hs.HandoffError("inventory permits only explicit windows and feature paths")
        windows, features = supplied.get("windows", {}), supplied.get("features", {})
        ids = {i["idea_id"] for i in upstream["ideas"]}
        if not isinstance(windows, dict) or set(windows) - ids:
            raise hs.HandoffError("unknown idea in window assignments")
        windows = {key: _window(value) for key, value in windows.items()}
        if not isinstance(features, dict) or set(features) - set(de.TIMEFRAMES):
            raise hs.HandoffError("unknown feature timeframe")
        for selection in features.values():
            if not isinstance(selection, dict) or set(selection) != {
                "feature_manifest",
                "feature_csv",
            }:
                raise hs.HandoffError("feature manifest and CSV must be supplied together")
            for value in selection.values():
                de._relative(value)
        if requests is not None:
            previous = hs._strict_json(
                de._local(requests.absolute().parent, requests.name).read_bytes()
            )
            for request in previous.values():
                for tf, selection in request.get("sources", {}).items():
                    retained = {k: v for k, v in selection.items() if k != "path"}
                    if retained:
                        if tf in features and features[tf] != retained:
                            raise hs.HandoffError(
                                "conflicting feature inventories for one canonical source"
                            )
                        features[tf] = retained
        receipts = [hs._strict_json(source_files[i["receipt"]]) for i in upstream["ideas"]]
        timeframes = list(dict.fromkeys(b["timeframe"] for r in receipts for b in r["bases"]))
        needed_taker = {
            b["timeframe"]
            for r in receipts
            for b in r["bases"]
            if TAKER & {f["feature"] for f in r["features"]}
        }
        if set(features) - set(timeframes):
            raise hs.HandoffError("feature selection is not an idea timeframe")
        catalogs = {tf: self.evidence._catalog(tf) for tf in timeframes}
        if any("parent" in c for c in catalogs.values()):
            catalogs["15m"] = self.evidence._catalog("15m")
        inputs, shared = {}, {}

        def admit(relative: str) -> Path:
            relative = de._relative(relative)
            destination = de._local(workspace, relative)
            source = de._local(local_root, relative) if local_root is not None else None
            digest = de.ft._sha256(source) if source is not None and source.exists() else None
            inputs[relative] = digest
            if prepare and digest is not None:
                if destination.exists():
                    raise hs.HandoffError("workspace input collision")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("xb") as target, source.open("rb") as handle:
                    shutil.copyfileobj(handle, target)
            if digest is not None and de.ft._sha256(destination) != digest:
                raise hs.HandoffError("copied input differs from original source")
            return destination

        # Parent first; a catalog alone never proves that its local bytes exist.
        for tf in sorted(catalogs, key=lambda tf: tf != "15m"):
            catalog = catalogs[tf]
            expected = catalog.get("normalized", catalog)
            expected = {**expected, "path": de._relative(expected["path"])}
            path = admit(expected["path"])
            origin = "LOCAL_SOURCE" if inputs[expected["path"]] else "UNAVAILABLE"
            parent_proof = None
            if "parent" in catalog:
                parent_catalog = catalogs["15m"]
                parent = de._local(workspace, parent_catalog["normalized"]["path"])
                if parent.exists():
                    raw = _derived_bytes(parent, tf)
                    if de.dc._sha256_bytes(raw) != expected["sha256"].removeprefix("sha256:"):
                        raise hs.HandoffError(
                            "native derivation differs from canonical normalized digest"
                        )
                    parent_proof = {
                        "status": "PHYSICAL_PARENT_REDERIVATION_VERIFIED",
                        "parent_sha256": shared["15m"]["local"]["sha256"],
                        "parent_identity": catalog["parent"]["data_slice_identity"],
                        "derived_sha256": de.dc._sha256_bytes(raw),
                    }
                    if origin == "UNAVAILABLE" and materialize:
                        origin = "NATIVE_SCRATCH_DERIVATION"
                        if prepare:
                            path.parent.mkdir(parents=True, exist_ok=True)
                            with path.open("xb") as handle:
                                handle.write(raw)
            local, _ = de.inspect_local(catalog, path, None)
            shared[tf] = {
                "catalog": catalog,
                "path": expected["path"],
                "origin": origin,
                "local": local,
                "parent_proof": parent_proof,
                "features": {},
            }
            selection = features.get(tf, {})
            if selection:
                for relative in selection.values():
                    admit(relative)
            elif tf in needed_taker and materialize and path.exists():
                selection = {
                    "feature_csv": f"features/{tf}.csv",
                    "feature_manifest": f"features/{tf}.manifest.json",
                }
                if prepare:
                    csv_path = de._local(workspace, selection["feature_csv"])
                    manifest_path = de._local(workspace, selection["feature_manifest"])
                    availability = de._local(workspace, "availability.json")
                    if not availability.exists():
                        availability.write_bytes(self.evidence.readiness.git.blob(de.AVAILABILITY))
                    options = {
                        "output_path": csv_path,
                        "manifest_path": manifest_path,
                        "availability_catalog_path": availability,
                    }
                    if tf == "15m":
                        taker.materialize_d4_native_takerflow_features(d4_path=path, **options)
                    else:
                        taker.materialize_canonical_kline_takerflow_features(
                            canonical_kline_path=path, timeframe=tf, **options
                        )
            shared[tf]["features"] = selection

        recheck_requests = {}
        for r in receipts:
            window = windows.get(r["idea_id"], r["requested_window"])
            if window is not None:
                _window(window)
            recheck_requests[r["idea_id"]] = {
                "window": window,
                "sources": {
                    b["timeframe"]: {
                        "path": shared[b["timeframe"]]["path"],
                        **shared[b["timeframe"]]["features"],
                    }
                    for b in r["bases"]
                },
            }
        request_bytes = hs._json_bytes(recheck_requests)
        request_path = de._local(workspace, "recheck.requests.json")
        if prepare:
            with request_path.open("xb") as handle:
                handle.write(request_bytes)
        if request_path.read_bytes() != request_bytes:
            raise hs.HandoffError("recheck request map changed")
        recheck = self.evidence.build_files(*chain, requests=request_path, local_root=workspace)
        checked = hs._strict_json(recheck[hs.SUMMARY_FILE])
        queue = [
            gap
            for gap in checked["investigation_queue"]
            if not (
                gap["code"] == "PHYSICAL_PARENT_REDERIVATION_NOT_PERFORMED"
                and shared[gap["timeframe"]]["parent_proof"]
            )
        ]
        # Re-read original inputs after all native calls; reject concurrent input changes.
        for relative, digest in inputs.items():
            source = de._local(local_root, relative) if local_root is not None else None
            actual = de.ft._sha256(source) if source is not None and source.exists() else None
            if actual != digest:
                raise hs.HandoffError("original local source changed during preparation")
        if hs._read_tree(evidence_dir) != source_files:
            raise hs.HandoffError("source 02E packet changed during preparation")
        if inventory is not None and de.ft._sha256(inventory) != inventory_sha:
            raise hs.HandoffError("inventory changed during preparation")
        summary = hs._hashed(
            {
                "schema_version": SCHEMA,
                "authority": hs.AUTHORITY,
                "repo_sha": self.evidence.readiness.identity.repo_sha,
                "source_02e": upstream["content_sha256"],
                "source_packet_hashes": {
                    n: de.dc._sha256_bytes(v) for n, v in source_files.items()
                },
                "upstream_02e_requests_sha256": upstream["requests_sha256"],
                "inventory_sha256": inventory_sha,
                "local_root": str(local_root.absolute()) if local_root else None,
                "workspace": str(workspace.absolute()),
                "materialize": materialize,
                "source_bytes": inputs,
                "workspace_hashes": _snapshot(workspace),
                "shared_sources": shared,
                "ideas": [
                    {**entry, "receipt": "recheck/" + entry["receipt"]}
                    for entry in checked["ideas"]
                ],
                "counts": checked["counts"],
                "science_counts": checked["science_counts"],
                "science_status": "NOT_READY",
                "search_contract_status": "NOT_ISSUABLE",
                "recheck_content_sha256": checked["content_sha256"],
                "investigation_queue": queue,
                "next_data_investigation": next(
                    (g for g in queue if g["code"] != "SCIENTIFIC_PROTOCOL_MISSING"), None
                ),
            }
        )
        files = {"recheck/" + n: raw for n, raw in recheck.items()}
        files.update({hs.SUMMARY_FILE: hs._json_bytes(summary), "requests.json": request_bytes})
        self.evidence.readiness._head()
        return self.evidence.readiness.handoff._guard(hs._render(files))

    def build(
        self, output: Path, evidence_dir: Path, chain: tuple, workspace: Path, **options
    ) -> dict:
        _separate(
            output,
            workspace,
            evidence_dir,
            *chain,
            *([options["local_root"]] if options.get("local_root") else []),
        )
        _external_target(output)
        _external_target(workspace)
        workspace.mkdir()
        files = self._evaluate(evidence_dir, chain, workspace, prepare=True, **options)
        hs._publish(
            files, output, lambda p: self.verify(p, evidence_dir, chain, workspace, **options)
        )
        return hs._strict_json(files[hs.SUMMARY_FILE])

    def verify(
        self, output: Path, evidence_dir: Path, chain: tuple, workspace: Path, **options
    ) -> dict:
        sr._check_paths(output, workspace)
        _packet_paths(output)
        files = hs._read_tree(output)
        summary = hs._strict_json(files[hs.SUMMARY_FILE])
        hs._check_hash(summary, SCHEMA)
        if _snapshot(workspace) != summary["workspace_hashes"]:
            raise hs.HandoffError("workspace inventory changed")
        if files != self._evaluate(evidence_dir, chain, workspace, prepare=False, **options):
            raise hs.HandoffError("02F replay did not reproduce exact bytes")
        return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "replay"))
    for name in (
        "output",
        "evidence-dir",
        "readiness-dir",
        "built-dir",
        "prepared-dir",
        "responses-dir",
        "workspace",
    ):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("local-root", "inventory", "requests", "evidence-local-root"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    try:
        adapter = QueueInputPreparation()
        chain = (args.readiness_dir, args.built_dir, args.prepared_dir, args.responses_dir)
        options = {
            "local_root": args.local_root,
            "inventory": args.inventory,
            "requests": args.requests,
            "evidence_local_root": args.evidence_local_root,
            "materialize": args.materialize,
        }
        method = adapter.build if args.command == "build" else adapter.verify
        result = method(args.output, args.evidence_dir, chain, args.workspace, **options)
    except (ValueError, OSError, KeyError, TypeError, RuntimeError, de.dc.ConsumerError) as exc:
        print(f"QUEUE_INPUT_PREPARATION_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(json.dumps({key: result[key] for key in ("content_sha256", "science_counts")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
