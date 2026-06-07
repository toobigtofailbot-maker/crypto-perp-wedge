"""Render validated dashboard_data.v1 into local static HTML."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any


TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "index.html"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def _esc(value: Any) -> str:
    if value is None:
        return "Not available"
    return html.escape(str(value), quote=True)


def _badge(status: str) -> str:
    safe = _esc(status)
    return f'<span class="badge badge-{safe.lower().replace("_", "-")}">{safe}</span>'


def _source_links(data: dict[str, Any], ref_ids: list[str]) -> str:
    refs = {ref["ref_id"]: ref for ref in data["source_refs"]}
    links = []
    for ref_id in ref_ids:
        ref = refs.get(ref_id)
        if ref is None:
            continue
        label = _esc(ref_id)
        path = _esc(ref["path"])
        links.append(f'<a href="../{path}">{label}</a>')
    return ", ".join(links) if links else "None"


def _cards(data: dict[str, Any]) -> str:
    cards = []
    for card in data["pages"]["overview"]["status_cards"]:
        cards.append(
            "\n".join(
                [
                    '<article class="card">',
                    f'<div class="card-top">{_badge(card["status"])}</div>',
                    f'<h3>{_esc(card["title"])}</h3>',
                    f'<p>{_esc(card["summary"])}</p>',
                    f'<p class="source-line">Sources: {_source_links(data, card["source_refs"])}</p>',
                    "</article>",
                ]
            )
        )
    return "\n".join(cards)


def _empty_states(data: dict[str, Any]) -> str:
    overview = data["pages"]["overview"]
    states = [
        overview["latest_result_population_empty_state"],
        overview["paper_runtime_empty_state"],
        overview["live_mode_empty_state"],
    ]
    rows = []
    for state in states:
        rows.append(
            "<li>"
            f"{_badge(state['status'])}"
            f"<span>{_esc(state['message'])}</span>"
            f'<small>{_source_links(data, state["source_refs"])}</small>'
            "</li>"
        )
    return "\n".join(rows)


def _facts_table(rows: list[tuple[str, Any]]) -> str:
    rendered = []
    for label, value in rows:
        rendered.append(
            f"<tr><th>{_esc(label)}</th><td><code>{_esc(value)}</code></td></tr>"
        )
    return "\n".join(rendered)


def _data_provenance(data: dict[str, Any]) -> str:
    page = data["pages"]["data_provenance"]
    d4 = page["d4_slice"]
    gaps = d4["gap_facts"]
    duplicates = d4["duplicate_facts"]
    range_facts = d4["timestamp_range"]
    rows = [
        ("D4 catalog ref", d4["catalog_ref"]),
        ("D4 slice identity", d4["data_slice_identity"]),
        ("D4 catalog artifact hash", d4["catalog_artifact_sha256"]),
        ("D3 validation report hash", page["d3_validation_report"]["sha256"]),
        ("D2 import report hash", page["d2_import_report"]["sha256"]),
        ("Dataset", d4["dataset_id"]),
        ("Venue / symbol", f"{d4['venue']} / {d4['symbol']}"),
        ("Market / stream / timeframe", f"{d4['market_type']} / {d4['stream']} / {d4['timeframe']}"),
        ("Rows", f"{d4['row_count']} of {d4['expected_row_count']} expected"),
        ("Timestamp range", f"{range_facts['start_utc']} to {range_facts['end_utc']}"),
        ("Gap facts", f"{gaps['gap_count']} gaps, {gaps['missing_bar_count']} missing bars"),
        ("Gap policy", gaps["policy"]),
        ("Duplicate facts", f"{duplicates['duplicate_group_count']} groups, {duplicates['duplicate_row_count']} rows"),
        ("Duplicate policy", duplicates["policy"]),
        ("Raw source hash", d4["raw_source_sha256"]),
        ("Normalized hash", d4["normalized_sha256"]),
    ]
    artifact_rows = []
    for artifact in page["artifact_paths"]:
        artifact_rows.append(
            "<tr>"
            f"<td>{_esc(artifact['artifact_id'])}</td>"
            f"<td>{_esc(artifact['artifact_type'])}</td>"
            f"<td><code>{_esc(artifact['path'])}</code></td>"
            f"<td><code>{_esc(artifact['sha256'])}</code></td>"
            "</tr>"
        )
    return "\n".join(
        [
            f'<div class="section-head">{_badge(page["status"])}<span>Data / Provenance</span></div>',
            '<table class="fact-table">',
            _facts_table(rows),
            "</table>",
            "<h3>Source Artifacts</h3>",
            '<table class="compact-table"><thead><tr><th>ID</th><th>Type</th><th>Path</th><th>SHA256</th></tr></thead><tbody>',
            "\n".join(artifact_rows),
            "</tbody></table>",
        ]
    )


def _gates(data: dict[str, Any]) -> str:
    gates = data["pages"]["gates"]["gates"]
    rows = []
    for gate in gates:
        rows.append(
            "<tr>"
            f"<td><code>{_esc(gate['gate_id'])}</code></td>"
            f"<td>{_esc(gate['title'])}</td>"
            f"<td>{_badge(gate['status'])}</td>"
            f"<td>{_esc(gate['why_it_matters'])}</td>"
            f"<td>{_esc(gate['required_human_action'])}</td>"
            f"<td>{_esc(gate['non_authority_note'])}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _warnings(data: dict[str, Any]) -> str:
    warnings = [*data.get("warnings", []), *data["pages"]["overview"].get("warnings", [])]
    if not warnings:
        return '<p class="muted">No dashboard warnings.</p>'
    return "\n".join(
        f"<li>{_badge(item['status'])}<span>{_esc(item['message'])}</span></li>" for item in warnings
    )


def _write_assets(output_dir: Path) -> None:
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    for asset_name in ["dashboard.css", "dashboard.js"]:
        shutil.copyfile(STATIC_DIR / asset_name, assets_dir / asset_name)


def render_dashboard(data: dict[str, Any], output_dir: Path | str) -> Path:
    """Render a validated dashboard_data dictionary to ``output_dir/index.html``."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    _write_assets(output_path)

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    overview = data["pages"]["overview"]
    counts = overview["open_gates_summary"]["counts_by_status"]
    replacements = {
        "generated_at": _esc(data["generated_at_utc"]),
        "source_commit": _esc(data["source_commit"]),
        "source_branch": _esc(data["source_branch"]),
        "dirty_state": _esc(data["dirty_state"]),
        "overall_status": _badge(overview["status"]),
        "cards": _cards(data),
        "empty_states": _empty_states(data),
        "warnings": _warnings(data),
        "data_provenance": _data_provenance(data),
        "gates": _gates(data),
        "gate_counts": _esc(json.dumps(counts, sort_keys=True)),
        "d4_catalog_ref": _esc(overview["latest_data_slice"]["d4_catalog_ref"]),
        "d4_slice_identity": _esc(overview["latest_data_slice"]["d4_slice_identity"]),
    }
    html_text = template
    for key, value in replacements.items():
        html_text = html_text.replace("{{ " + key + " }}", value)

    index_path = output_path / "index.html"
    index_path.write_text(html_text, encoding="utf-8")
    return index_path
