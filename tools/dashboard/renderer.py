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
    return f'<span class="badge badge-{safe.lower().replace("_", "-")}" data-status="{safe}">{safe}</span>'


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
        status_class = _esc(card["status"].lower().replace("_", "-"))
        cards.append(
            "\n".join(
                [
                    f'<article class="card status-card status-card-{status_class}">',
                    '<div class="card-top">',
                    f'<h3>{_esc(card["title"])}</h3>',
                    f'{_badge(card["status"])}',
                    "</div>",
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
            '<li class="empty-state-item">'
            f"{_badge(state['status'])}"
            '<div class="empty-state-copy">'
            f"<span>{_esc(state['message'])}</span>"
            f'<small>{_source_links(data, state["source_refs"])}</small>'
            "</div>"
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
            '<tr class="filter-row">'
            f"<td>{_esc(artifact['artifact_id'])}</td>"
            f"<td>{_esc(artifact['artifact_type'])}</td>"
            f"<td><code>{_esc(artifact['path'])}</code></td>"
            f"<td><code>{_esc(artifact['sha256'])}</code></td>"
            "</tr>"
        )
    return "\n".join(
        [
            '<div class="section-head">',
            "<div>",
            "<span>Data / Provenance</span>",
            '<p>Committed artifact identities and local generated-output posture.</p>',
            "</div>",
            f'{_badge(page["status"])}',
            "</div>",
            '<div class="table-wrap">',
            '<table class="fact-table">',
            _facts_table(rows),
            "</table>",
            "</div>",
            '<div class="table-toolbar">',
            "<h3>Source Artifacts</h3>",
            '<label class="search-label">Filter <input type="search" data-filter-target="artifact-table" placeholder="Artifact, type, path, hash"></label>',
            "</div>",
            '<div class="table-wrap">',
            '<table class="compact-table"><thead><tr><th>ID</th><th>Type</th><th>Path</th><th>SHA256</th></tr></thead><tbody>',
            "\n".join(artifact_rows),
            "</tbody></table>",
            "</div>",
        ]
    )


def _gates(data: dict[str, Any]) -> str:
    gates = data["pages"]["gates"]["gates"]
    rows = []
    for gate in gates:
        rows.append(
            '<tr class="filter-row">'
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
        f'<li class="warning-item">{_badge(item["status"])}<span>{_esc(item["message"])}</span></li>'
        for item in warnings
    )


def _gate_status_summary(counts: dict[str, int]) -> str:
    items = []
    for status in ["PASS", "WARN", "FAIL", "BLOCKED", "UNKNOWN", "NOT_AVAILABLE"]:
        items.append(
            '<li class="status-count">'
            f"{_badge(status)}"
            f'<strong>{_esc(counts.get(status, 0))}</strong>'
            "</li>"
        )
    return "\n".join(items)


def _posture_flags() -> str:
    flags = [
        ("Research", "only"),
        ("Paper", "disabled"),
        ("Live", "disabled"),
    ]
    return "\n".join(
        f'<span class="posture-flag"><strong>{_esc(label)}</strong>{_esc(value)}</span>' for label, value in flags
    )


def _freshness_rows(data: dict[str, Any]) -> str:
    overview = data["pages"]["overview"]
    data_freshness = overview["latest_data_slice"]["freshness"]
    validation_freshness = overview["latest_validation"]["freshness"]
    rows = [
        ("Data slice", overview["latest_data_slice"]["status"], data_freshness["staleness_status"], data_freshness["staleness_reason"]),
        (
            "Validation",
            overview["latest_validation"]["status"],
            validation_freshness["staleness_status"],
            validation_freshness["staleness_reason"],
        ),
    ]
    return "\n".join(
        "<tr>"
        f"<th>{_esc(label)}</th>"
        f"<td>{_badge(status)}</td>"
        f"<td><code>{_esc(staleness)}</code></td>"
        f"<td>{_esc(reason)}</td>"
        "</tr>"
        for label, status, staleness, reason in rows
    )


def _results(data: dict[str, Any]) -> str:
    results = data["pages"].get("results")
    if results is None:
        return "\n".join([
            '<section class="panel">',
            '<p>Results data is not available in this dashboard_data payload.</p>',
            '<p class="muted">Absence of Results data does not imply failure, readiness, or approval.</p>',
            '</section>',
        ])

    rp = results["result_population"]
    cp = results["complete_population"]
    ds = results["descriptive_summary"]
    vt = results["variant_table"]
    ba = results["backtest_assumptions"]

    banner = "\n".join([
        '<div class="results-authority-notice">',
        '<strong>Display-only / Non-authoritative</strong>',
        '<ul>',
        '<li>No ranking authority — rows appear in variant ID order only; order is not a performance ranking.</li>',
        '<li>No recommendation — no variant is recommended or preferred by this display.</li>',
        '<li>No readiness authority — this display does not evaluate deployment readiness.</li>',
        '<li>No promotion authority — this display does not approve or deploy variants.</li>',
        '<li>No execution authority — this display does not create orders, trades, or deployments.</li>',
        '</ul>',
        '</div>',
    ])

    rp_html = "\n".join([
        '<section class="panel">',
        '<h2>Result Population</h2>',
        '<div class="table-wrap"><table class="fact-table">',
        _facts_table([
            ("Result population ID", rp["result_population_id"]),
            ("Path", rp["path"]),
            ("Provenance class", rp["provenance_class"]),
            ("Result population identity hash", rp["result_population_identity_hash"]),
            ("Input identity hash", rp["input_identity_hash"]),
            ("Strategy spec ID", rp["strategy_spec_id"]),
            ("Variant manifest ID", rp["variant_manifest_id"]),
            ("Sweep plan ID", rp["sweep_plan_id"]),
        ]),
        '</table></div>',
        f'<p class="muted source-line">Sources: {_source_links(data, rp["source_refs"])}</p>',
        '</section>',
    ])

    cp_html = "\n".join([
        '<section class="panel">',
        '<h2>Complete Population Facts</h2>',
        '<div class="table-wrap"><table class="fact-table">',
        _facts_table([
            ("Committed denominator", cp["committed_denominator"]),
            ("Result row count", cp["result_row_count"]),
            ("Outcome count sum", cp["outcome_counts_sum"]),
            ("Represented variant count", cp["represented_variant_count"]),
            ("Variant ID range", f"{cp['variant_id_start']} to {cp['variant_id_end']}"),
            ("All-variant retention required", "Yes — partial or selection-biased retention is prohibited"),
            ("Complete-denominator required", "Yes — executed-only denominator is prohibited"),
        ]),
        '</table></div>',
        f'<p class="muted source-line">Sources: {_source_links(data, cp["source_refs"])}</p>',
        '</section>',
    ])

    obs_html = "\n".join(f"<li>{_esc(obs)}</li>" for obs in ds["observations"])
    cav_html = "\n".join(f"<li>{_esc(cav)}</li>" for cav in ds["caveats"])
    summary_html = "\n".join([
        '<section class="panel">',
        '<h2>Descriptive Summary</h2>',
        f'<p><strong>Variant order policy:</strong> <code>{_esc(ds["variant_order_policy"])}</code></p>',
        '<h3>Observations</h3>',
        f'<ul>{obs_html}</ul>',
        '<h3>Caveats</h3>',
        f'<ul>{cav_html}</ul>',
        f'<p class="muted source-line">Sources: {_source_links(data, ds["source_refs"])}</p>',
        '</section>',
    ])

    vt_rows = []
    for row in vt["rows"]:
        vt_rows.append(
            '<tr class="filter-row">'
            f'<td><code>{_esc(row["variant_id"])}</code></td>'
            f'<td>{_esc(row["outcome_category"])}</td>'
            f'<td><code>{_esc(row["return_pct"])}</code></td>'
            f'<td><code>{_esc(row["pnl"])}</code></td>'
            f'<td><code>{_esc(row["drawdown"])}</code></td>'
            f'<td><code>{_esc(row["sharpe"])}</code></td>'
            f'<td><code>{_esc(row["trade_count"])}</code></td>'
            f'<td><code>{_esc(row["win_rate"])}</code></td>'
            f'<td><code>{_esc(row["fees"])}</code></td>'
            f'<td><code>{_esc(row["slippage"])}</code></td>'
            f'<td><code>{_esc(row["funding"])}</code></td>'
            '</tr>'
        )
    variant_html = "\n".join([
        '<section class="panel">',
        '<h2>Variant Table</h2>',
        '<p class="muted results-order-note">Rows are displayed in variant ID order only; order is not a performance ranking.</p>',
        '<div class="table-toolbar">',
        f'<span class="muted">{_esc(len(vt["rows"]))} rows</span>',
        '<label class="search-label">Filter <input type="search" data-filter-target="results-table" placeholder="Variant ID, outcome, value"></label>',
        '</div>',
        '<div class="table-wrap">',
        '<table class="compact-table results-variant-table">',
        '<thead><tr>',
        '<th>Variant ID</th><th>Outcome</th><th>Return %</th><th>PnL</th><th>Drawdown</th>',
        '<th>Sharpe</th><th>Trades</th><th>Win Rate</th><th>Fees</th><th>Slippage</th><th>Funding</th>',
        '</tr></thead>',
        '<tbody>',
        "\n".join(vt_rows),
        '</tbody></table>',
        '</div>',
        f'<p class="muted source-line">Variant order policy: <code>{_esc(vt["variant_order_policy"])}</code> &mdash; Sources: {_source_links(data, vt["source_refs"])}</p>',
        '</section>',
    ])

    ba_html = "\n".join([
        '<section class="panel">',
        '<h2>Backtest Assumptions</h2>',
        '<div class="table-wrap"><table class="fact-table">',
        _facts_table([
            ("Fill mode", ba["fill_mode"]),
            ("Bar path assumption", ba["bar_path_assumption"]),
            ("Fee-side assumption", ba["fee_side_assumption"]),
            ("Slippage model", ba["slippage_model"]),
            ("Mark price source", ba["mark_price_source"]),
            ("Liquidation mode", ba["liquidation_mode"]),
            ("Order size assumption", ba["order_size_assumption"]),
            ("Funding notional", ba["funding_notional"]),
            ("Liquidity capacity assumption", ba.get("liquidity_capacity_assumption")),
            ("Maintenance margin assumption", ba.get("maintenance_margin_assumption")),
        ]),
        '</table></div>',
        f'<p class="muted source-line">Sources: {_source_links(data, ba["source_refs"])}</p>',
        '</section>',
    ])

    registry = results.get("lab_registry")
    registry_html = ""
    if registry is not None:
        registry_rows = []
        for record in registry["records"]:
            adopted_reports = [
                ref for ref in [
                    record.get("analytics_report_ref"),
                    record.get("robustness_report_ref"),
                    record.get("triage_sidecar_report_ref"),
                ]
                if ref
            ]
            registry_rows.append(
                '<tr class="filter-row">'
                f'<td><code>{_esc(record["run_id"])}</code></td>'
                f'<td>{_badge(record["status"])}</td>'
                f'<td><code>{_esc(record["strategy_spec_id"])}</code></td>'
                f'<td><code>{_esc(record["variant_manifest_id"])}</code></td>'
                f'<td><code>{_esc(record["sweep_plan_id"])}</code></td>'
                f'<td><code>{_esc(record["result_population_id"])}</code></td>'
                f'<td><code>{_esc(record["result_row_count"])}/{_esc(record["committed_denominator"])}</code></td>'
                f'<td><code>{_esc(record["return_pct_min"])} to {_esc(record["return_pct_max"])}</code></td>'
                f'<td><code>{_esc(record["sharpe_min"])} to {_esc(record["sharpe_max"])}</code></td>'
                f'<td>{_esc(", ".join(adopted_reports) if adopted_reports else "Not available")}</td>'
                '</tr>'
            )
        registry_html = "\n".join([
            '<section class="panel">',
            '<h2>Lab Run / Result Registry</h2>',
            '<p class="muted results-order-note">Runs are displayed in run ID order only; order is not a quality ranking.</p>',
            '<div class="table-toolbar">',
            f'<span class="muted">{_esc(registry["record_count"])} records</span>',
            '<label class="search-label">Filter <input type="search" data-filter-target="lab-registry-table" placeholder="Run, strategy, result, report"></label>',
            '</div>',
            '<div class="table-wrap">',
            '<table class="compact-table results-variant-table">',
            '<thead><tr>',
            '<th>Run</th><th>Status</th><th>Strategy</th><th>VM</th><th>Sweep</th><th>Result Population</th>',
            '<th>Rows</th><th>Return % Range</th><th>Sharpe Range</th><th>Adopted Reports</th>',
            '</tr></thead>',
            '<tbody>',
            "\n".join(registry_rows),
            '</tbody></table>',
            '</div>',
            f'<p class="muted source-line">Run order policy: <code>{_esc(registry["run_order_policy"])}</code> &mdash; Sources: {_source_links(data, registry["source_refs"])}</p>',
            '</section>',
        ])

    # variant_html is placed before cp_html and summary_html so that
    # html.index("VAR-XXXXXX") finds the first occurrence in variant table order
    # (ascending), before re-occurrences in cp facts and descriptive summary.
    return "\n".join([
        '<div class="section-head">',
        "<div>",
        "<span>Results</span>",
        '<p>Display-only. Non-authoritative. Rendered from validated dashboard_data.v1 only.</p>',
        "</div>",
        f'{_badge(results["status"])}',
        "</div>",
        banner,
        rp_html,
        variant_html,
        registry_html,
        cp_html,
        summary_html,
        ba_html,
    ])


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
        "posture_flags": _posture_flags(),
        "cards": _cards(data),
        "empty_states": _empty_states(data),
        "warnings": _warnings(data),
        "data_provenance": _data_provenance(data),
        "gates": _gates(data),
        "gate_status_summary": _gate_status_summary(counts),
        "freshness_rows": _freshness_rows(data),
        "gate_counts": _esc(json.dumps(counts, sort_keys=True)),
        "d4_catalog_ref": _esc(overview["latest_data_slice"]["d4_catalog_ref"]),
        "d4_slice_identity": _esc(overview["latest_data_slice"]["d4_slice_identity"]),
        "results": _results(data),
    }
    html_text = template
    for key, value in replacements.items():
        html_text = html_text.replace("{{ " + key + " }}", value)

    index_path = output_path / "index.html"
    index_path.write_text(html_text, encoding="utf-8")
    return index_path
