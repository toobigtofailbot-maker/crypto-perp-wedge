"""Re-run the WP-8b SSS v2 advisory-source consumer queries."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd


def _rows_as_dicts(cursor: duckdb.DuckDBPyConnection) -> list[dict[str, object]]:
    columns = [description[0] for description in cursor.description or []]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _summary_row(summary_payload: dict[str, object]) -> dict[str, object]:
    corpus_window = summary_payload["corpus_window"]
    segmentation_axes = summary_payload["segmentation_axes"]
    return {
        "shadow_signal_summary_id": summary_payload["shadow_signal_summary_id"],
        "schema_version": summary_payload["schema_version"],
        "generated_at": summary_payload["generated_at"],
        "first_overlay_shadow_log_id": corpus_window["first_overlay_shadow_log_id"],
        "last_overlay_shadow_log_id": corpus_window["last_overlay_shadow_log_id"],
        "first_observed_at": corpus_window["first_observed_at"],
        "last_observed_at": corpus_window["last_observed_at"],
        "total_source_observation_count": corpus_window["total_source_observation_count"],
        "derivation_method": summary_payload["derivation_method"],
        "segmentation_axes_json": json.dumps(segmentation_axes),
        "segmentation_axis_count": len(segmentation_axes),
        "advisory_source_is_first_class_segment_key": segmentation_axes == ["advisory_source"],
    }


def _segment_rows(summary_payload: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for segment in summary_payload["segments"]:
        rows.append(
            {
                "shadow_signal_summary_id": summary_payload["shadow_signal_summary_id"],
                "schema_version": summary_payload["schema_version"],
                "advisory_source": segment["advisory_source"],
                "match_count": segment["match_count"],
                "mismatch_count": segment["mismatch_count"],
                "abstention_count": segment["abstention_count"],
                "observation_count": segment["observation_count"],
                "rate_denominator": segment["rate_denominator"],
                "agreement_rate": segment["agreement_rate"],
                "disagreement_rate": segment["disagreement_rate"],
                "insufficient_evidence": segment["insufficient_evidence"],
                "signal_outcome": segment["signal_outcome"],
                "first_observed_at": segment["first_observed_at"],
                "last_observed_at": segment["last_observed_at"],
            }
        )
    return rows


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _register_views(conn: duckdb.DuckDBPyConnection, repo_root: Path) -> None:
    summary_path = (
        repo_root
        / "research"
        / "shadow_signal_summaries_v2"
        / "SSS-0002.shadow_signal_summary.json"
    )
    wp7w_q03_path = (
        repo_root
        / "research"
        / "briefs"
        / "2026-04-shadow_signal_advisory_source_slice_01"
        / "outputs"
        / "Q03.json"
    )
    wp7w_q04_path = (
        repo_root
        / "research"
        / "briefs"
        / "2026-04-shadow_signal_advisory_source_slice_01"
        / "outputs"
        / "Q04.json"
    )

    summary_payload = _load_json(summary_path)
    wp7w_rollup_payload = _load_json(wp7w_q03_path)
    wp7w_floor_payload = _load_json(wp7w_q04_path)

    conn.register("sss_v2_summary", pd.DataFrame([_summary_row(summary_payload)]))
    conn.register("sss_v2_segments", pd.DataFrame(_segment_rows(summary_payload)))
    conn.register("wp7w_source_rollup", pd.DataFrame(wp7w_rollup_payload))
    conn.register("wp7w_floor_status", pd.DataFrame(wp7w_floor_payload))


def main() -> int:
    brief_dir = Path(__file__).resolve().parent
    repo_root = Path(__file__).resolve().parents[3]
    queries_dir = brief_dir / "queries"
    outputs_dir = brief_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(database=":memory:")
    _register_views(conn, repo_root)

    for query_path in sorted(queries_dir.glob("Q*.sql")):
        query_prefix = query_path.stem.split("_", 1)[0]
        output_path = outputs_dir / f"{query_prefix}.json"
        sql_text = query_path.read_text(encoding="utf-8")
        rows = _rows_as_dicts(conn.execute(sql_text))
        output_path.write_text(json.dumps(rows, indent=2, default=str) + "\n", encoding="utf-8")
        print(f"Wrote {output_path.relative_to(repo_root)}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
