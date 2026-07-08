"""Deterministic static renderers for the lab product cockpit.

Both renderers emit a pure read-only document. The HTML renderer produces an
operator-grade single page built from hand-generated HTML/CSS/SVG only: no
``<script>``, no ``<button>``, no ``<form>``, no ``<input>``, no ``onclick``, no
network fetch, no auto-refresh. Output is a deterministic function of the data
model, so two renders over the same checkout are byte-identical.
"""

from __future__ import annotations

import html
from typing import Any

# ---------------------------------------------------------------------------
# Design system. A restrained, theme-aware palette with semantic accents. The
# page is dark-first with an explicit light-mode override; both are legible.
# ---------------------------------------------------------------------------
_CSS = """
:root {
  color-scheme: light dark;
  --bg: #f7f8fa; --panel: #ffffff; --panel-2: #f0f2f6; --ink: #1a1d24;
  --ink-soft: #545b68; --line: #d9dde4; --line-strong: #b9c0cc;
  --accent: #3f5fd6; --accent-soft: #e7ecfb;
  --pos: #1f9d6b; --pos-soft: #dff3ea;
  --warn: #c07a12; --warn-soft: #fbeed6;
  --neg: #c8384b; --neg-soft: #fbe1e4;
  --mute: #6b7280; --mute-soft: #eceef2;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0e1117; --panel: #161b23; --panel-2: #1d2530; --ink: #e6e9ef;
    --ink-soft: #9aa4b2; --line: #2a323d; --line-strong: #3a434f;
    --accent: #7aa2ff; --accent-soft: #1c2740;
    --pos: #45c495; --pos-soft: #123028;
    --warn: #e0a94a; --warn-soft: #33280f;
    --neg: #f27a8b; --neg-soft: #331319;
    --mute: #8b93a1; --mute-soft: #1f262f;
  }
}
* { box-sizing: border-box; }
body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  background: var(--bg); color: var(--ink); margin: 0; line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 1180px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }
header.masthead { margin-bottom: 1.4rem; }
header.masthead h1 { font-size: 1.65rem; margin: 0 0 0.2rem; letter-spacing: -0.01em; }
.subtitle { color: var(--ink-soft); font-size: 0.95rem; margin: 0; }
.chips { margin-top: 0.7rem; display: flex; flex-wrap: wrap; gap: 0.4rem; }
.chip {
  font-size: 0.72rem; font-weight: 600; padding: 0.2rem 0.55rem;
  border-radius: 999px; background: var(--mute-soft); color: var(--ink-soft);
  border: 1px solid var(--line); letter-spacing: 0.01em;
}
.chip.accent { background: var(--accent-soft); color: var(--accent); border-color: transparent; }
.chip.pos { background: var(--pos-soft); color: var(--pos); border-color: transparent; }
.chip.warn { background: var(--warn-soft); color: var(--warn); border-color: transparent; }
.chip.neg { background: var(--neg-soft); color: var(--neg); border-color: transparent; }
.banner {
  border-left: 3px solid var(--warn); background: var(--warn-soft);
  color: var(--ink); padding: 0.7rem 0.9rem; border-radius: 8px;
  margin: 1rem 0; font-size: 0.9rem;
}
.banner.info { border-left-color: var(--accent); background: var(--accent-soft); }
h2.section {
  font-size: 1.05rem; margin: 2.2rem 0 0.9rem; padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--line); letter-spacing: -0.01em;
}
h2.section .hint { font-weight: 400; color: var(--ink-soft); font-size: 0.82rem; }
.grid { display: grid; gap: 0.9rem; }
.kpis { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
.kpi {
  background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  padding: 0.9rem 1rem;
}
.kpi .val { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em; }
.kpi .lab { font-size: 0.78rem; color: var(--ink-soft); margin-top: 0.15rem; }
.kpi.pos .val { color: var(--pos); }
.kpi.warn .val { color: var(--warn); }
.kpi.neg .val { color: var(--neg); }
.kpi.zero .val { color: var(--mute); }
.cards { grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); }
.card {
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
  padding: 1.1rem 1.15rem; display: flex; flex-direction: column; gap: 0.7rem;
}
.card h3 { margin: 0; font-size: 1rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.card .hid { font-family: ui-monospace, "SF Mono", monospace; font-size: 0.82rem; color: var(--ink-soft); }
.card .route { font-size: 0.78rem; color: var(--ink-soft); font-family: ui-monospace, monospace; }
.pill { font-size: 0.68rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.03em; }
.pill.no_go { background: var(--neg-soft); color: var(--neg); }
.pill.non_promoting { background: var(--warn-soft); color: var(--warn); }
.metricline { display: grid; grid-template-columns: 1fr auto; gap: 0.3rem; font-size: 0.8rem; align-items: center; }
.metricline .k { color: var(--ink-soft); }
.metricline .v { font-variant-numeric: tabular-nums; font-weight: 600; }
.meter { background: var(--panel-2); border-radius: 6px; height: 0.5rem; overflow: hidden; border: 1px solid var(--line); }
.meter > span { display: block; height: 100%; }
.pips { display: flex; gap: 0.22rem; }
.pip { width: 0.7rem; height: 0.7rem; border-radius: 3px; background: var(--mute-soft); border: 1px solid var(--line); }
.pip.on { background: var(--pos); border-color: transparent; }
.reading { font-size: 0.83rem; color: var(--ink); background: var(--panel-2); border-radius: 8px; padding: 0.6rem 0.7rem; }
.smallcaps { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-soft); font-weight: 700; }
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 1.1rem 1.2rem; }
.two-col { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 0.9rem; }
table.data { border-collapse: collapse; width: 100%; font-size: 0.83rem; }
table.data th, table.data td { text-align: left; padding: 0.4rem 0.55rem; border-bottom: 1px solid var(--line); vertical-align: top; }
table.data th { color: var(--ink-soft); font-weight: 600; font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.03em; }
table.data td.num { text-align: right; font-variant-numeric: tabular-nums; }
code, .mono { font-family: ui-monospace, "SF Mono", monospace; font-size: 0.8rem; }
.tablewrap { overflow-x: auto; }
.badge-ok { color: var(--pos); font-weight: 600; }
.badge-miss { color: var(--neg); font-weight: 600; }
.badge-withheld { color: var(--mute); font-weight: 600; }
.funnel { display: flex; flex-direction: column; gap: 0.4rem; }
.funnel-row { display: grid; grid-template-columns: 210px 1fr 40px; align-items: center; gap: 0.6rem; font-size: 0.83rem; }
.funnel-bar { background: var(--panel-2); border-radius: 6px; height: 1.35rem; overflow: hidden; border: 1px solid var(--line); }
.funnel-bar > span { display: flex; align-items: center; height: 100%; color: #fff; font-size: 0.72rem; font-weight: 600; padding-left: 0.5rem; }
.timeline { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0; }
.tl { display: grid; grid-template-columns: 90px 1fr; gap: 0.8rem; position: relative; padding: 0 0 1.1rem 0; }
.tl:not(:last-child)::before { content: ""; position: absolute; left: 100px; top: 1.1rem; bottom: 0; width: 2px; background: var(--line); }
.tl .dot { justify-self: end; align-self: start; margin-top: 0.15rem; }
.tl .ref { font-family: ui-monospace, monospace; font-size: 0.8rem; color: var(--accent); font-weight: 700; }
.tl .lab { font-weight: 600; font-size: 0.9rem; }
.tl .det { font-size: 0.8rem; color: var(--ink-soft); }
.assertions { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 0.3rem 1.2rem; font-size: 0.8rem; }
.assertions .row { display: flex; justify-content: space-between; gap: 0.5rem; padding: 0.15rem 0; border-bottom: 1px dotted var(--line); }
.assertions .k { color: var(--ink-soft); }
.legend { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.76rem; color: var(--ink-soft); margin-top: 0.5rem; }
.legend span::before { content: ""; display: inline-block; width: 0.7rem; height: 0.7rem; border-radius: 2px; margin-right: 0.3rem; vertical-align: middle; }
.legend .l-pos::before { background: var(--pos); }
.legend .l-neg::before { background: var(--neg); }
.legend .l-warn::before { background: var(--warn); }
footer.foot { margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid var(--line); font-size: 0.78rem; color: var(--ink-soft); }
.pill.awaiting_prereg_approval { background: var(--warn-soft); color: var(--warn); }
.pill.blocked_or_invalid { background: var(--neg-soft); color: var(--neg); }
.pill.complete_spine_only { background: var(--accent-soft); color: var(--accent); }
.pill.complete { background: var(--pos-soft); color: var(--pos); }
.pill.unavailable { background: var(--mute-soft); color: var(--mute); }
.stages { display: flex; flex-wrap: wrap; gap: 0.25rem; }
.stage-chip {
  font-size: 0.64rem; padding: 0.12rem 0.4rem; border-radius: 5px;
  border: 1px solid var(--line); background: var(--mute-soft); color: var(--ink-soft);
  font-family: ui-monospace, monospace;
}
.stage-chip.complete { background: var(--pos-soft); color: var(--pos); border-color: transparent; }
.stage-chip.awaiting_approval { background: var(--warn-soft); color: var(--warn); border-color: transparent; }
.stage-chip.blocked { background: var(--neg-soft); color: var(--neg); border-color: transparent; }
.stage-chip.not_started { opacity: 0.5; }
.callout {
  border-left: 3px solid var(--accent); background: var(--accent-soft);
  padding: 0.5rem 0.7rem; border-radius: 8px; font-size: 0.82rem; color: var(--ink);
}
.callout.warn { border-left-color: var(--warn); background: var(--warn-soft); }
.callout.neg { border-left-color: var(--neg); background: var(--neg-soft); }
.callout .hashline { font-family: ui-monospace, monospace; font-size: 0.72rem; color: var(--ink-soft); word-break: break-all; }
.runmeta { font-size: 0.8rem; color: var(--ink-soft); display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; }
.runmeta code { color: var(--ink); }
""".strip()


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _fmt_num(value: Any, digits: int = 2) -> str:
    if not isinstance(value, (int, float)):
        return "n/a"
    return f"{value:,.{digits}f}"


def _fmt_pct(fraction: Any, digits: int = 2) -> str:
    """Format a fraction (0.77) as a percent string (77.00%)."""
    if not isinstance(fraction, (int, float)):
        return "n/a"
    return f"{fraction * 100:.{digits}f}%"


# ---------------------------------------------------------------------------
# SVG comparison charts (deterministic; sizes computed in Python).
# ---------------------------------------------------------------------------
def _svg_diverging_bars(
    rows: list[tuple[str, float | None]], *, unit: str
) -> str:
    """Diverging horizontal bar chart around a zero centre line.

    ``rows`` is (label, value); positive values render right in the positive
    hue, negative left in the negative hue. Scale is the max absolute value.
    """
    values = [v for _, v in rows if isinstance(v, (int, float))]
    scale = max((abs(v) for v in values), default=1.0) or 1.0
    row_h, gap, label_w, num_w = 26, 8, 130, 96
    chart_w = 360
    centre = label_w + chart_w / 2
    total_w = label_w + chart_w + num_w
    height = len(rows) * (row_h + gap) + gap
    parts = [
        f"<svg viewBox='0 0 {total_w} {height}' width='100%' "
        f"role='img' preserveAspectRatio='xMinYMin meet' "
        f"style='max-width:{total_w}px'>"
    ]
    parts.append(
        f"<line x1='{centre:.1f}' y1='{gap}' x2='{centre:.1f}' "
        f"y2='{height - gap:.1f}' stroke='var(--line-strong)' stroke-width='1'/>"
    )
    for i, (label, value) in enumerate(rows):
        y = gap + i * (row_h + gap)
        parts.append(
            f"<text x='0' y='{y + row_h * 0.68:.1f}' font-size='12' "
            f"fill='var(--ink)'>{_esc(label)}</text>"
        )
        if isinstance(value, (int, float)):
            width = abs(value) / scale * (chart_w / 2)
            colour = "var(--pos)" if value >= 0 else "var(--neg)"
            x = centre if value >= 0 else centre - width
            parts.append(
                f"<rect x='{x:.1f}' y='{y + 3:.1f}' width='{max(width, 0.5):.1f}' "
                f"height='{row_h - 6}' rx='3' fill='{colour}'/>"
            )
            num = f"{value:,.0f}{unit}"
            parts.append(
                f"<text x='{total_w}' y='{y + row_h * 0.68:.1f}' font-size='11' "
                f"text-anchor='end' fill='var(--ink-soft)' "
                f"font-family='ui-monospace,monospace'>{_esc(num)}</text>"
            )
        else:
            parts.append(
                f"<text x='{centre:.1f}' y='{y + row_h * 0.68:.1f}' font-size='11' "
                f"text-anchor='middle' fill='var(--mute)'>withheld</text>"
            )
    parts.append("</svg>")
    return "".join(parts)


def _svg_magnitude_bars(
    rows: list[tuple[str, float | None]], *, as_percent: bool
) -> str:
    """Left-anchored magnitude bars scaled 0..max (e.g. drawdown severity)."""
    values = [v for _, v in rows if isinstance(v, (int, float))]
    scale = max(values, default=1.0) or 1.0
    row_h, gap, label_w, num_w = 26, 8, 130, 70
    chart_w = 380
    total_w = label_w + chart_w + num_w
    height = len(rows) * (row_h + gap) + gap
    parts = [
        f"<svg viewBox='0 0 {total_w} {height}' width='100%' role='img' "
        f"preserveAspectRatio='xMinYMin meet' style='max-width:{total_w}px'>"
    ]
    for i, (label, value) in enumerate(rows):
        y = gap + i * (row_h + gap)
        parts.append(
            f"<text x='0' y='{y + row_h * 0.68:.1f}' font-size='12' "
            f"fill='var(--ink)'>{_esc(label)}</text>"
        )
        parts.append(
            f"<rect x='{label_w}' y='{y + 3:.1f}' width='{chart_w}' "
            f"height='{row_h - 6}' rx='3' fill='var(--panel-2)' "
            f"stroke='var(--line)' stroke-width='0.5'/>"
        )
        if isinstance(value, (int, float)):
            width = value / scale * chart_w
            # Severity hue by magnitude: higher drawdown is more alarming.
            colour = "var(--neg)" if value >= 0.9 else "var(--warn)"
            parts.append(
                f"<rect x='{label_w}' y='{y + 3:.1f}' width='{max(width, 0.5):.1f}' "
                f"height='{row_h - 6}' rx='3' fill='{colour}'/>"
            )
            num = _fmt_pct(value) if as_percent else f"{value:,.2f}"
            parts.append(
                f"<text x='{total_w}' y='{y + row_h * 0.68:.1f}' font-size='11' "
                f"text-anchor='end' fill='var(--ink-soft)' "
                f"font-family='ui-monospace,monospace'>{_esc(num)}</text>"
            )
        else:
            parts.append(
                f"<text x='{label_w + 6}' y='{y + row_h * 0.68:.1f}' font-size='11' "
                f"fill='var(--mute)'>withheld</text>"
            )
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Panels.
# ---------------------------------------------------------------------------
def _kpi(val: str, label: str, tone: str = "") -> str:
    cls = f"kpi {tone}".strip()
    return (
        f"<div class='{cls}'><div class='val'>{_esc(val)}</div>"
        f"<div class='lab'>{_esc(label)}</div></div>"
    )


def _presence_badge(present: Any) -> str:
    if present:
        return '<span class="badge-ok">present</span>'
    return '<span class="badge-miss">missing</span>'


def _overview_html(data: dict[str, Any]) -> str:
    ov = data["overview"]
    batch = data["real_traffic_batch"]
    totals = batch.get("totals", {})
    rt = ov["real_traffic_batch"]
    hyp_count = totals.get("hypothesis_count", 0)
    kpis = "".join(
        [
            _kpi(str(rt.get("frozen_denominator_rows", "n/a")), "Frozen denominator rows", "accent"),
            _kpi(str(rt.get("preserved_rows", "n/a")), "Rows preserved", "pos"),
            _kpi(str(rt.get("executed_successful_rows", "n/a")), "Executed successful rows", "pos"),
            _kpi(
                f"{totals.get('hypotheses_with_positive_median_pnl', 0)}/{hyp_count}",
                "Positive median-PnL hypotheses",
                "warn",
            ),
            _kpi(str(totals.get("go_like_hypotheses", 0)), "GO-like hypotheses", "zero"),
            _kpi("0", "Candidate-ready for review", "zero"),
        ]
    )
    blockers = "".join(f"<li>{_esc(b)}</li>" for b in ov["top_blockers"])
    return (
        "<h2 class='section'>Lab overview "
        "<span class='hint'>&mdash; concluded real-traffic batch, full denominator</span></h2>"
        f"<p class='subtitle'>{_esc(ov['productization_status'])}</p>"
        f"<div class='grid kpis' style='margin-top:0.9rem'>{kpis}</div>"
        "<div class='banner'><strong>Top blockers &amp; caveats.</strong>"
        f"<ul style='margin:0.4rem 0 0;padding-left:1.1rem'>{blockers}</ul></div>"
    )


def _short_hash(value: Any) -> str:
    """Truncate a ``sha256:...`` digest for compact display."""
    if not isinstance(value, str) or not value:
        return "—"
    if value.startswith("sha256:") and len(value) > 7 + 16:
        return value[: 7 + 16] + "…"
    return value


def _pipeline_run_card(run: dict[str, Any]) -> str:
    status = run["display_status"]
    pill = f"<span class='pill {status}'>{_esc(run['display_label'])}</span>"

    if not run.get("available", False):
        return (
            "<div class='card'>"
            f"<h3>{pill}<span class='hid'>{_esc(run['pipeline_run_id'])}</span></h3>"
            "<div class='callout neg'><strong>Fail-closed.</strong> "
            f"{_esc(run.get('invalid_reason'))}. No run state is fabricated.</div>"
            "</div>"
        )

    meta = (
        "<div class='runmeta'>"
        f"<span>symbol <code>{_esc(run.get('symbol'))}</code></span>"
        f"<span>timeframe <code>{_esc(run.get('timeframe'))}</code></span>"
        f"<span>requested by <code>{_esc(run.get('requested_by'))}</code></span>"
        f"<span>request <code>{_esc(run.get('request_id'))}</code></span>"
        "</div>"
    )

    stage_chips = "".join(
        f"<span class='stage-chip {_esc(s.get('status'))}'>{_esc(s.get('stage'))}</span>"
        for s in run.get("stages", [])
    )

    callouts: list[str] = []
    if run.get("awaiting_approval"):
        approval = run.get("approval", {})
        callouts.append(
            "<div class='callout warn'><strong>Awaiting prereg approval.</strong> "
            "This run is halted until an exact-content preregistration approval "
            "marker is supplied out-of-band. No approval control exists here."
            f"<div class='hashline'>scope: {_esc(approval.get('approval_scope'))}</div>"
            f"<div class='hashline'>packet sha256: "
            f"{_esc(approval.get('preregistration_packet_sha256'))}</div></div>"
        )
    if run.get("blocked_reasons"):
        reasons = "".join(
            f"<li>{_esc(r)}</li>" for r in run["blocked_reasons"]
        )
        callouts.append(
            "<div class='callout neg'><strong>Blocked.</strong>"
            f"<ul style='margin:0.3rem 0 0;padding-left:1.1rem'>{reasons}</ul></div>"
        )
    if run.get("spine_only"):
        callouts.append(
            "<div class='callout'><strong>State-spine proof only.</strong> "
            f"runner_invoked = <code>{_esc(run.get('runner_invoked'))}</code> "
            f"(execution_kind <code>{_esc(run.get('execution_kind'))}</code>). "
            "This is the deterministic pipeline spine, not a real hypothesis "
            "run; real agent/runner adapter flow is not yet complete.</div>"
        )

    art_rows = "".join(
        f"<tr><td>{_esc(a['filename'])}</td>"
        f"<td>{_presence_badge(a['present'])}</td>"
        f"<td class='mono'>{_esc(_short_hash(a['sha256']))}</td></tr>"
        for a in run.get("artifacts", [])
    )
    artifacts = (
        "<div><span class='smallcaps'>Artifacts</span>"
        "<div class='tablewrap'><table class='data'><thead><tr><th>file</th>"
        "<th>status</th><th>sha256</th></tr></thead>"
        f"<tbody>{art_rows}</tbody></table></div></div>"
    )

    return (
        "<div class='card'>"
        f"<h3>{pill}<span class='hid'>{_esc(run['pipeline_run_id'])}</span></h3>"
        f"<div style='font-weight:600'>{_esc(run.get('source_idea'))}</div>"
        f"{meta}"
        f"<div><span class='smallcaps'>Current stage</span> "
        f"<code>{_esc(run.get('current_stage'))}</code></div>"
        f"<div><span class='smallcaps'>Stage timeline</span>"
        f"<div class='stages' style='margin-top:0.35rem'>{stage_chips}</div></div>"
        f"{''.join(callouts)}"
        f"{artifacts}"
        "</div>"
    )


def _pipeline_state_html(data: dict[str, Any]) -> str:
    ps = data["pipeline_state"]
    header = (
        "<h2 class='section'>Pipeline runs &middot; run-state "
        "<span class='hint'>&mdash; read-only over committed pipeline packets</span></h2>"
    )
    if not ps.get("available"):
        return (
            f"{header}"
            "<div class='panel'><div class='banner'>No committed pipeline run "
            "packets are available "
            f"(<span class='mono'>{_esc(ps.get('runs_root'))}</span>). "
            f"{_esc(ps.get('unavailable_reason'))}. The pipeline state panel "
            "fails closed rather than fabricating runs.</div>"
            f"<div class='banner info'>{_esc(ps.get('spine_only_label'))}</div></div>"
        )

    totals = ps["totals"]
    kpis = "".join(
        [
            _kpi(str(totals.get("run_count", 0)), "Pipeline runs", "accent"),
            _kpi(str(totals.get("awaiting_approval", 0)), "Awaiting prereg approval", "warn"),
            _kpi(str(totals.get("blocked_or_invalid", 0)), "Blocked / invalid", "neg"),
            _kpi(str(totals.get("complete_spine_only", 0)), "Complete (spine only)", "accent"),
            _kpi(str(totals.get("complete_real", 0)), "Complete (real runner)", "zero"),
        ]
    )
    spine_banner = ""
    if ps.get("spine_only"):
        spine_banner = (
            f"<div class='banner info'><strong>Honest labeling.</strong> "
            f"{_esc(ps.get('spine_only_label'))}</div>"
        )
    cards = "".join(_pipeline_run_card(r) for r in ps.get("runs", []))
    return (
        f"{header}"
        "<div class='banner info' style='margin-top:0'>Read-only projection of "
        "committed <span class='mono'>tools/lab_pipeline</span> run packets. No "
        "run, approve, retry, promote, or candidate control exists on this "
        "page.</div>"
        f"<div class='grid kpis' style='margin-top:0.9rem'>{kpis}</div>"
        f"{spine_banner}"
        f"<div class='grid cards' style='margin-top:0.9rem'>{cards}</div>"
    )


def _funnel_html(data: dict[str, Any]) -> str:
    funnel = data["candidate_funnel"]
    stages = funnel["stages"]
    top = max((s["count"] for s in stages), default=1) or 1
    tones = {
        "frozen_hypotheses": "var(--accent)",
        "executed": "var(--accent)",
        "positive_median_pnl": "var(--warn)",
        "go_like_evidence": "var(--mute)",
        "candidate_ready": "var(--mute)",
    }
    rows = []
    for s in stages:
        width = (s["count"] / top * 100) if top else 0
        colour = tones.get(s["stage"], "var(--accent)")
        inner = (
            f"<span style='width:{max(width, 3):.1f}%;background:{colour}'>"
            f"{s['count']}</span>"
            if s["count"] > 0
            else "<span style='width:3%;background:var(--line-strong)'></span>"
        )
        rows.append(
            f"<div class='funnel-row'><div>{_esc(s['label'])}</div>"
            f"<div class='funnel-bar'>{inner}</div>"
            f"<div class='mono' style='text-align:right'>{s['count']}</div></div>"
        )
    return (
        "<h2 class='section'>Candidate funnel "
        "<span class='hint'>&mdash; full denominator, no winner-only view</span></h2>"
        "<div class='panel'>"
        "<div class='banner info' style='margin-top:0'>The funnel narrows to "
        "<strong>zero candidate-ready</strong> on committed evidence: no GO-like or "
        "candidate-worthy result was produced. No action controls exist here.</div>"
        f"<div class='funnel'>{''.join(rows)}</div></div>"
    )


def _hypothesis_card(h: dict[str, Any]) -> str:
    status = h["status"]
    pill = f"<span class='pill {status}'>{_esc(h['status_label'])}</span>"
    # Positive-row pips (out of the successful/denominator row count).
    denom = h.get("denominator") or 0
    positive = h.get("positive_pnl_rows") or 0
    pips = "".join(
        f"<span class='pip {'on' if i < positive else ''}'></span>"
        for i in range(denom)
    )
    dd = h.get("max_drawdown")
    dd_width = (dd * 100) if isinstance(dd, (int, float)) else 0
    dd_colour = "var(--neg)" if isinstance(dd, (int, float)) and dd >= 0.9 else "var(--warn)"
    trades = sum(h.get("trade_counts") or [])
    wf_ok = h.get("walkforward_successful_rows")
    wf_tot = h.get("walkforward_rows")
    context_flags = "".join(
        f"<span class='chip warn'>{_esc(f)}</span>"
        for f in h.get("result_context_flags", [])
        if isinstance(f, str) and "caution" in f.lower()
    )
    metrics = "".join(
        [
            f"<div class='metricline'><span class='k'>Median PnL</span>"
            f"<span class='v'>{_esc(_fmt_num(h.get('median_pnl'), 2))}</span></div>",
            f"<div class='metricline'><span class='k'>Median return</span>"
            f"<span class='v'>{_esc(_fmt_num(h.get('median_return_pct'), 3))}%</span></div>",
            f"<div class='metricline'><span class='k'>Median fees / slippage</span>"
            f"<span class='v'>{_esc(_fmt_num(h.get('median_fees'), 2))} / "
            f"{_esc(_fmt_num(h.get('median_slippage'), 2))}</span></div>",
            f"<div class='metricline'><span class='k'>Trades (sum across rows)</span>"
            f"<span class='v'>{_esc(trades)}</span></div>",
        ]
    )
    reading = (
        f"<div class='reading'>{_esc(h.get('reading'))}</div>"
        if h.get("reading")
        else ""
    )
    return (
        "<div class='card'>"
        f"<h3>{pill}<span class='hid'>{_esc(h['hypothesis_id'])}</span></h3>"
        f"<div style='font-weight:600'>{_esc(h.get('name'))}</div>"
        f"<div class='route'>{_esc(h.get('family_route'))}</div>"
        f"<div><span class='smallcaps'>Result Population</span> "
        f"<code>{_esc(h.get('result_population_id'))}</code> &middot; "
        f"<span class='mono'>{positive}/{denom} positive rows</span></div>"
        f"<div class='pips'>{pips}</div>"
        "<div><div class='metricline'><span class='k'>Max drawdown</span>"
        f"<span class='v'>{_esc(_fmt_pct(dd))}</span></div>"
        f"<div class='meter'><span style='width:{min(dd_width,100):.1f}%;background:{dd_colour}'></span></div></div>"
        f"{metrics}"
        f"<div><span class='chip'>WFO {_esc(wf_ok)}/{_esc(wf_tot)} dry-run</span> "
        "<span class='chip'>MC withheld</span> "
        f"<span class='chip'>freshness: {_esc(h.get('freshness_check_result'))}</span></div>"
        f"{context_flags}"
        f"<div><span class='smallcaps'>Non-promoting</span> &mdash; {_esc(h.get('non_promoting_reason'))}.</div>"
        f"{reading}"
        "</div>"
    )


def _explorer_html(data: dict[str, Any]) -> str:
    batch = data["real_traffic_batch"]
    if not batch.get("available"):
        return (
            "<h2 class='section'>Strategy / hypothesis explorer</h2>"
            "<div class='banner'>Real-traffic batch rollup unavailable "
            "(source artifact missing).</div>"
        )
    cards = "".join(_hypothesis_card(h) for h in batch["hypotheses"])
    return (
        "<h2 class='section'>Strategy / hypothesis explorer "
        "<span class='hint'>&mdash; four frozen hypotheses, all rows preserved</span></h2>"
        f"<div class='grid cards'>{cards}</div>"
    )


def _visuals_html(data: dict[str, Any]) -> str:
    batch = data["real_traffic_batch"]
    if not batch.get("available"):
        return ""
    hyps = batch["hypotheses"]
    pnl_rows = [(h["hypothesis_id"], h.get("median_pnl")) for h in hyps]
    dd_rows = [(h["hypothesis_id"], h.get("max_drawdown")) for h in hyps]
    pos_rows = [
        (h["hypothesis_id"], float(h.get("positive_pnl_rows") or 0)) for h in hyps
    ]
    return (
        "<h2 class='section'>Visual result panels "
        "<span class='hint'>&mdash; population comparison across the batch</span></h2>"
        "<div class='two-col'>"
        "<div class='panel'><div class='smallcaps'>Median PnL by hypothesis</div>"
        f"{_svg_diverging_bars(pnl_rows, unit='')}"
        "<div class='legend'><span class='l-pos'>positive</span>"
        "<span class='l-neg'>negative</span></div></div>"
        "<div class='panel'><div class='smallcaps'>Max drawdown severity</div>"
        f"{_svg_magnitude_bars(dd_rows, as_percent=True)}"
        "<div class='legend'><span class='l-warn'>high</span>"
        "<span class='l-neg'>&ge; 90%</span></div></div>"
        "<div class='panel'><div class='smallcaps'>Positive PnL rows (of 8 per hypothesis)</div>"
        f"{_svg_magnitude_bars(pos_rows, as_percent=False)}</div>"
        "<div class='panel'><div class='smallcaps'>Non-promoting reason</div>"
        "<div class='banner' style='margin-top:0.4rem'>Positive raw PnL surfaces "
        "coexist with drawdown-lethal risk profiles. The primary drawdown screen "
        "blocks escalation; no hypothesis is GO-like. This is descriptive "
        "accumulated evidence, not an edge claim.</div></div>"
        "</div>"
    )


def _wfo_robustness_html(data: dict[str, Any]) -> str:
    wfo = data["wfo_oos"]
    rob = data["robustness"]
    proto = wfo.get("protocol", {})
    wfo_rows = "".join(
        f"<tr><td class='mono'>{_esc(r['hypothesis_id'])}</td>"
        f"<td class='num'>{_esc(r['walkforward_successful_rows'])}/{_esc(r['walkforward_rows'])}</td>"
        f"<td>{_esc(', '.join(r['warnings']) or '—')}</td></tr>"
        for r in wfo.get("per_hypothesis", [])
    )
    withheld = " ".join(
        f"<span class='chip'>{_esc(s)} withheld</span>"
        for s in rob.get("withheld_statistics", [])
    )
    return (
        "<h2 class='section'>Robustness &middot; WFO / OOS posture "
        "<span class='hint'>&mdash; withheld statistics shown explicitly</span></h2>"
        "<div class='two-col'>"
        "<div class='panel'><div class='smallcaps'>Walk-forward / OOS</div>"
        "<div class='banner' style='margin-top:0.4rem'>Bounded dry-run "
        "walk-forward &mdash; <strong>not a rigorous OOS gate pass</strong>.</div>"
        f"<div style='font-size:0.82rem;color:var(--ink-soft);margin-bottom:0.5rem'>"
        f"method: {_esc(proto.get('method'))}; windows: {_esc(proto.get('window_count'))}; "
        f"IS/OOS bars: {_esc(proto.get('in_sample_bars'))}/{_esc(proto.get('out_of_sample_bars'))}; "
        f"purge/embargo: {_esc(proto.get('purge_embargo'))}</div>"
        "<div class='tablewrap'><table class='data'><thead><tr><th>hypothesis</th>"
        "<th>WF rows</th><th>warnings</th></tr></thead>"
        f"<tbody>{wfo_rows}</tbody></table></div></div>"
        "<div class='panel'><div class='smallcaps'>Robustness / Monte-Carlo</div>"
        f"<div style='margin:0.5rem 0'><span class='badge-withheld'>Monte-Carlo run: "
        f"{_esc(rob.get('monte_carlo_run'))}</span></div>"
        f"<div style='font-size:0.82rem;color:var(--ink-soft)'>{_esc(rob.get('monte_carlo_reason'))}</div>"
        f"<div style='margin-top:0.5rem'>{withheld}</div>"
        f"<div class='banner' style='margin-top:0.6rem'>{_esc(rob.get('withheld_note'))}</div>"
        f"<div style='font-size:0.82rem;color:var(--ink-soft)'>{_esc(rob.get('axis_sensitivity_review'))}</div>"
        "</div></div>"
    )


def _timeline_html(data: dict[str, Any]) -> str:
    kind_colour = {
        "freeze": "var(--accent)",
        "execute": "var(--warn)",
        "complete": "var(--pos)",
        "conclude": "var(--pos)",
    }
    items = []
    for ev in data["timeline"]:
        colour = kind_colour.get(ev["kind"], "var(--mute)")
        dot = (
            f"<span class='dot' style='display:inline-block;width:0.8rem;height:0.8rem;"
            f"border-radius:50%;background:{colour}'></span>"
        )
        items.append(
            "<li class='tl'>"
            f"<div class='ref'>{_esc(ev['ref'])}{dot}</div>"
            f"<div><div class='lab'>{_esc(ev['label'])}</div>"
            f"<div class='det'>{_esc(ev['detail'])}</div>"
            f"<div class='det mono'>{_esc(ev['source'])}</div></div></li>"
        )
    return (
        "<h2 class='section'>Activity / evidence timeline "
        "<span class='hint'>&mdash; committed PR sequence, no live refresh</span></h2>"
        f"<div class='panel'><ul class='timeline'>{''.join(items)}</ul></div>"
    )


def _coordinator_html(data: dict[str, Any]) -> str:
    coord = data["coordinator"]
    summary = coord["denominator_summary"]
    state_rows = "".join(
        f"<tr><td class='mono'>{_esc(state)}</td><td class='num'>{_esc(count)}</td></tr>"
        for state, count in summary["by_overall_state"].items()
    )
    subj_rows = "".join(
        f"<tr><td class='mono'>{_esc(s['subject_id'])}</td>"
        f"<td class='mono'>{_esc(s['overall_state'])}</td>"
        f"<td>{_esc(s['evidence_class'])}</td></tr>"
        for s in coord["subjects"]
    )
    held = coord["held_boundary_panel"]
    held_html = ""
    if held.get("available"):
        def _ul(items: list[str]) -> str:
            return "<ul style='margin:0.3rem 0 0.7rem;padding-left:1.1rem;font-size:0.82rem'>" + "".join(
                f"<li>{_esc(i)}</li>" for i in items
            ) + "</ul>"

        parts = []
        if held.get("go_gated_protected"):
            parts.append("<div class='smallcaps'>GO-gated protected</div>")
            parts.append(_ul(held["go_gated_protected"]))
        if held.get("requires_real_go_candidate"):
            parts.append("<div class='smallcaps'>Requires first real GO candidate</div>")
            parts.append(_ul(held["requires_real_go_candidate"]))
        held_html = "".join(parts)
    return (
        "<h2 class='section'>Coordinator state &middot; held boundary "
        "<span class='hint'>&mdash; lab-wide, from the merged state model</span></h2>"
        "<div class='two-col'>"
        "<div class='panel'><div class='smallcaps'>Subjects by overall state</div>"
        "<div class='tablewrap'><table class='data'><thead><tr><th>state</th>"
        "<th>count</th></tr></thead>"
        f"<tbody>{state_rows}</tbody></table></div>"
        f"<div style='margin-top:0.6rem;font-size:0.82rem;color:var(--ink-soft)'>"
        f"candidate-ready: {summary['candidate_ready_count']} &middot; "
        f"operator-gate pending: {summary['operator_gate_pending_count']}</div></div>"
        "<div class='panel'><div class='smallcaps'>Held boundary / deferred-B</div>"
        f"{held_html or '<p>Held-boundary map unavailable.</p>'}</div>"
        "</div>"
        "<div class='panel' style='margin-top:0.9rem'>"
        "<div class='smallcaps'>Coordinator subjects</div>"
        "<div class='tablewrap'><table class='data'><thead><tr><th>subject</th>"
        "<th>overall state</th><th>evidence class</th></tr></thead>"
        f"<tbody>{subj_rows}</tbody></table></div></div>"
    )


def _artifacts_html(data: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{_esc(a['category'])}</td>"
        f"<td><code>{_esc(a['path'])}</code></td>"
        f"<td>{_presence_badge(a['present'])}</td></tr>"
        for a in data["artifact_drilldown"]
    )
    return (
        "<h2 class='section'>Artifact drilldown "
        "<span class='hint'>&mdash; repo-relative, read-only</span></h2>"
        "<div class='panel'><div class='tablewrap'><table class='data'>"
        "<thead><tr><th>category</th><th>path</th><th>status</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></div>"
    )


def _boundary_html(data: dict[str, Any]) -> str:
    boundary = data["boundary"]
    rows = "".join(
        f"<div class='row'><span class='k'>{_esc(k)}</span>"
        f"<span class='{'badge-ok' if v else 'badge-miss'}'>{_esc(v)}</span></div>"
        for k, v in boundary.get("assertions", {}).items()
    )
    decl = data["non_authority_declaration"]
    decl_rows = "".join(
        f"<div class='row'><span class='k'>{_esc(k)}</span>"
        f"<span class='{'badge-ok' if not v else 'badge-miss'}'>{_esc(v)}</span></div>"
        for k, v in decl.items()
    )
    return (
        "<h2 class='section'>Boundary &middot; non-authority "
        "<span class='hint'>&mdash; committed assertions + cockpit declaration</span></h2>"
        "<div class='two-col'>"
        "<div class='panel'><div class='smallcaps'>Committed batch assertions</div>"
        f"<div class='assertions' style='margin-top:0.5rem'>{rows}</div></div>"
        "<div class='panel'><div class='smallcaps'>Cockpit non-authority declaration</div>"
        f"<div class='assertions' style='margin-top:0.5rem'>{decl_rows}</div></div>"
        "</div>"
    )


def render_html(data: dict[str, Any]) -> str:
    chips = (
        f"<span class='chip accent'>schema {_esc(data['schema_version'])}</span>"
        f"<span class='chip'>{_esc(data['surface_kind'])}</span>"
        "<span class='chip pos'>read-only</span>"
        "<span class='chip'>static &middot; no controls</span>"
    )
    body = "".join(
        [
            _overview_html(data),
            _pipeline_state_html(data),
            _funnel_html(data),
            _explorer_html(data),
            _visuals_html(data),
            _wfo_robustness_html(data),
            _timeline_html(data),
            _coordinator_html(data),
            _artifacts_html(data),
            _boundary_html(data),
        ]
    )
    caveats = "".join(f"<li>{_esc(c)}</li>" for c in data["caveats"])
    return (
        "<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        "<title>Lab Product Cockpit (read-only)</title>\n"
        f"<style>{_CSS}</style>\n</head>\n<body>\n<div class='wrap'>\n"
        "<header class='masthead'><h1>Lab Product Cockpit</h1>"
        "<p class='subtitle'>Static, read-only operator surface over concluded "
        "real-traffic lab evidence and the merged coordinator state model.</p>"
        f"<div class='chips'>{chips}</div></header>\n"
        "<div class='banner info'><strong>Read-only cockpit.</strong> No run, "
        "approve, promote, retry, candidate, scheduler, or live-fetch control "
        "exists on this page. Every number is projected from a committed "
        f"artifact.</div>\n<div class='banner'>{_esc(data['edge_search_hold'])}</div>\n"
        f"{body}\n"
        f"<footer class='foot'><strong>Caveats.</strong><ul style='margin:0.4rem 0 0;padding-left:1.1rem'>{caveats}</ul>"
        "<p style='margin-top:0.8rem'>Static read-only visualization only; no run, "
        "approval, promotion, candidate, crossing, paper/live/runtime, scheduler, "
        "notification, provider/API, credential, dependency, data, or protected-path "
        "authority.</p></footer>\n"
        "</div>\n</body>\n</html>\n"
    )


# ---------------------------------------------------------------------------
# Markdown renderer (for terminal / diff-friendly review).
# ---------------------------------------------------------------------------
def render_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Lab Product Cockpit (read-only)")
    lines.append("")
    lines.append(f"_schema: `{data['schema_version']}` — {data['surface_kind']}_")
    lines.append("")
    lines.append(
        "> Static read-only cockpit. No run / approve / promote / retry / "
        "candidate / scheduler / live-fetch control."
    )
    lines.append("")
    lines.append(f"> {data['edge_search_hold']}")
    lines.append("")

    ov = data["overview"]
    rt = ov["real_traffic_batch"]
    lines.append("## Lab overview")
    lines.append("")
    lines.append(f"- {ov['productization_status']}")
    lines.append(
        f"- Real-traffic batch: decision `{rt.get('decision')}`, "
        f"{rt.get('preserved_rows')}/{rt.get('frozen_denominator_rows')} rows "
        f"preserved, {rt.get('executed_successful_rows')} executed successful, "
        f"GO-like evidence: {rt.get('go_like_evidence')}, canonical RP written: "
        f"{rt.get('canonical_result_population_written')}."
    )
    lines.append("- Top blockers:")
    for b in ov["top_blockers"]:
        lines.append(f"  - {b}")
    lines.append("")

    ps = data["pipeline_state"]
    lines.append("## Pipeline runs / run-state")
    lines.append("")
    if not ps.get("available"):
        lines.append(
            f"- No committed pipeline run packets ({ps.get('runs_root')}); "
            f"{ps.get('unavailable_reason')}. Panel fails closed to unavailable."
        )
        lines.append(f"- {ps.get('spine_only_label')}")
        lines.append("")
    else:
        totals = ps["totals"]
        lines.append(
            f"- Runs: {totals.get('run_count')} "
            f"(awaiting approval: {totals.get('awaiting_approval')}, "
            f"blocked/invalid: {totals.get('blocked_or_invalid')}, "
            f"complete spine-only: {totals.get('complete_spine_only')}, "
            f"complete real-runner: {totals.get('complete_real')})."
        )
        if ps.get("spine_only"):
            lines.append(f"- Honest labeling: {ps.get('spine_only_label')}")
        lines.append("")
        lines.append("| run | status | current stage | runner_invoked | blocker |")
        lines.append("| --- | --- | --- | --- | --- |")
        for r in ps["runs"]:
            blocker = "; ".join(r.get("blocked_reasons", [])) or "—"
            lines.append(
                f"| `{r['pipeline_run_id']}` | {r['display_label']} | "
                f"`{r.get('current_stage')}` | {r.get('runner_invoked')} | "
                f"{blocker} |"
            )
        lines.append("")

    lines.append("## Candidate funnel (full denominator)")
    lines.append("")
    lines.append("| stage | count |")
    lines.append("| --- | ---: |")
    for s in data["candidate_funnel"]["stages"]:
        lines.append(f"| {s['label']} | {s['count']} |")
    lines.append("")

    batch = data["real_traffic_batch"]
    if batch.get("available"):
        lines.append("## Strategy / hypothesis explorer")
        lines.append("")
        lines.append(
            "| hypothesis | status | positive rows | median PnL | max drawdown | RP |"
        )
        lines.append("| --- | --- | ---: | ---: | ---: | --- |")
        for h in batch["hypotheses"]:
            lines.append(
                f"| `{h['hypothesis_id']}` | {h['status_label']} | "
                f"{h['positive_pnl_rows']}/{h['denominator']} | "
                f"{_fmt_num(h['median_pnl'], 2)} | {_fmt_pct(h['max_drawdown'])} | "
                f"{h['result_population_id']} |"
            )
        lines.append("")
        for h in batch["hypotheses"]:
            lines.append(f"### `{h['hypothesis_id']}` — {h.get('name')}")
            lines.append("")
            lines.append(f"- route: `{h.get('family_route')}`")
            lines.append(
                f"- non-promoting: {h.get('non_promoting_reason')}; "
                f"WFO {h.get('walkforward_successful_rows')}/{h.get('walkforward_rows')} "
                "dry-run; Monte-Carlo withheld."
            )
            if h.get("reading"):
                lines.append(f"- reading: {h['reading']}")
            for flag in h.get("result_context_flags", []):
                if isinstance(flag, str) and "caution" in flag.lower():
                    lines.append(f"- context: {flag}")
            lines.append("")

    rob = data["robustness"]
    lines.append("## Robustness / WFO / OOS")
    lines.append("")
    lines.append("- Walk-forward is bounded dry-run only; not a rigorous OOS gate pass.")
    lines.append(f"- Monte-Carlo run: {rob.get('monte_carlo_run')} — {rob.get('monte_carlo_reason')}")
    lines.append(
        f"- Withheld statistics: {', '.join(rob.get('withheld_statistics', []))}."
    )
    lines.append("")

    lines.append("## Activity / evidence timeline")
    lines.append("")
    for ev in data["timeline"]:
        lines.append(f"- {ev['ref']} — {ev['label']} (`{ev['source']}`)")
    lines.append("")

    coord = data["coordinator"]
    lines.append("## Coordinator state")
    lines.append("")
    lines.append("| overall state | count |")
    lines.append("| --- | ---: |")
    for state, count in coord["denominator_summary"]["by_overall_state"].items():
        lines.append(f"| `{state}` | {count} |")
    lines.append("")

    lines.append("## Artifact drilldown")
    lines.append("")
    for a in data["artifact_drilldown"]:
        flag = "present" if a["present"] else "missing"
        lines.append(f"- [{a['category']}] `{a['path']}` ({flag})")
    lines.append("")

    lines.append("## Boundary / non-authority")
    lines.append("")
    for k, v in data["boundary"].get("assertions", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    for c in data["caveats"]:
        lines.append(f"> {c}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
