"""Deterministic static renderers for the unified operator-surface index.

Both renderers emit a pure read-only landing page: tables, links, and text only.
No forms, no buttons, no ``<script>``, no network fetch, no auto-refresh. Output
is a deterministic function of the index data model, so two renders are
byte-identical.
"""

from __future__ import annotations

import html
from typing import Any

_CSS = """
:root { color-scheme: light dark; }
body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
       margin: 2rem; line-height: 1.45; }
h1 { font-size: 1.4rem; margin-bottom: 0.2rem; }
h2 { font-size: 1.1rem; margin-top: 1.6rem;
     border-bottom: 1px solid #8884; padding-bottom: 0.2rem; }
h3 { font-size: 1rem; margin-bottom: 0.2rem; }
table { border-collapse: collapse; margin: 0.4rem 0 1rem; width: 100%; }
th, td { border: 1px solid #8884; padding: 0.3rem 0.5rem;
         text-align: left; vertical-align: top; font-size: 0.9rem; }
th { background: #8881; }
.banner { border: 1px solid #c93; background: #fc31; padding: 0.5rem 0.75rem;
          border-radius: 6px; margin: 0.6rem 0; font-size: 0.9rem; }
.state { font-family: ui-monospace, monospace; }
.caveat { font-size: 0.9rem; }
code { font-family: ui-monospace, monospace; font-size: 0.85rem; }
""".strip()

_READ_ONLY_BANNER = (
    "Read-only operator index. This is where to look, not a control panel: no "
    "run, approve, reject, promote, retry, scheduler, or live-fetch control."
)


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _summary_pairs(summary: dict[str, Any]) -> list[tuple[str, str]]:
    """Flatten a tile summary into ``(label, value)`` rows, deterministically."""
    pairs: list[tuple[str, str]] = []
    for key in summary:  # dicts preserve the model's insertion order
        value = summary[key]
        if isinstance(value, dict):
            rendered = ", ".join(f"{k}={value[k]}" for k in value)
        elif isinstance(value, list):
            rendered = ", ".join(str(v) for v in value) or "none"
        else:
            rendered = str(value)
        pairs.append((key, rendered))
    return pairs


# ---------------------------------------------------------------------------
# Markdown renderer.
# ---------------------------------------------------------------------------
def render_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Lab Operator Surface — Unified Index (read-only)")
    lines.append("")
    lines.append(f"_schema: `{data['schema_version']}` -- {data['surface_kind']}_")
    lines.append("")
    lines.append(f"> {_READ_ONLY_BANNER}")
    lines.append("")
    lines.append(f"> {data['edge_search_hold']}")
    lines.append("")
    lines.append(
        f"_as-of label: `{data['as_of']}` -- period label: `{data['period']}` "
        "(descriptive only; no clock is read)_"
    )
    lines.append("")

    honest = data["honest_state"]
    lines.append("## Honest current state")
    lines.append("")
    lines.append(f"- {honest['note']}")
    lines.append(
        f"- candidate ready (committed evidence): {honest['candidate_ready_count']}"
    )
    lines.append(
        f"- operator gate pending: {honest['operator_gate_pending_count']}"
    )
    lines.append(
        f"- nothing candidate-ready: `{str(honest['nothing_candidate_ready']).lower()}`"
    )
    lines.append("")

    batch = data["batch_boundary"]
    lines.append("## Batch boundary (full population, not winners only)")
    lines.append("")
    lines.append(f"- subjects: {batch['subject_count']}")
    lines.append(
        f"- completed experiment runs reached: "
        f"{batch['completed_experiment_run_count']}"
    )
    lines.append(f"- NO-GO: {batch['no_go_count']}")
    lines.append(f"- blocked: {batch['blocked_count']}")
    lines.append(f"- candidate ready for human review: {batch['candidate_ready_count']}")
    lines.append(
        f"- operator gate pending: {batch['operator_gate_pending_count']}"
    )
    lines.append(
        f"- distinct Result Population sets: "
        f"{batch['distinct_result_population_sets']}"
    )
    lines.append("")
    lines.append("### Subjects by overall state")
    lines.append("")
    lines.append("| overall state | count |")
    lines.append("| --- | ---: |")
    for state, count in batch["by_overall_state"].items():
        lines.append(f"| `{state}` | {count} |")
    lines.append("")

    lines.append("## Surfaces")
    lines.append("")
    for tile in data["surfaces"]:
        lines.append(f"### {tile['title']}")
        lines.append("")
        lines.append(f"- package: `{tile['package']}`")
        lines.append(f"- module: `{tile['module']}`")
        lines.append(f"- open: `{tile['cli']}`")
        lines.append(f"- doc: [`{tile['doc']}`]({tile['doc']})")
        lines.append("- summary:")
        for label, value in _summary_pairs(tile["summary"]):
            lines.append(f"  - {label}: {value}")
        lines.append("")

    lines.append("## Related artifacts and docs")
    lines.append("")
    lines.append("| role | path | present |")
    lines.append("| --- | --- | --- |")
    for ref in data["related_docs"]:
        flag = "present" if ref["present"] else "missing"
        lines.append(f"| {ref['role']} | [`{ref['path']}`]({ref['path']}) | {flag} |")
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    for caveat in data["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Static HTML renderer.
# ---------------------------------------------------------------------------
def _summary_table(summary: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{_esc(label)}</td><td class='state'>{_esc(value)}</td></tr>"
        for label, value in _summary_pairs(summary)
    )
    return (
        "<table><thead><tr><th>field</th><th>value</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def _state_rows(by_overall_state: dict[str, Any]) -> str:
    return "".join(
        f"<tr><td class='state'>{_esc(state)}</td><td>{_esc(count)}</td></tr>"
        for state, count in by_overall_state.items()
    )


def _tile_html(tile: dict[str, Any]) -> str:
    return (
        f"<h3>{_esc(tile['title'])}</h3>"
        "<table><tbody>"
        f"<tr><td>package</td><td><code>{_esc(tile['package'])}</code></td></tr>"
        f"<tr><td>module</td><td><code>{_esc(tile['module'])}</code></td></tr>"
        f"<tr><td>open</td><td><code>{_esc(tile['cli'])}</code></td></tr>"
        "<tr><td>doc</td><td>"
        f"<a href='{_esc(tile['doc'])}'><code>{_esc(tile['doc'])}</code></a>"
        "</td></tr>"
        "</tbody></table>"
        f"{_summary_table(tile['summary'])}"
    )


def _docs_rows(related_docs: list[dict[str, Any]]) -> str:
    return "".join(
        f"<tr><td>{_esc(ref['role'])}</td>"
        f"<td><a href='{_esc(ref['path'])}'><code>{_esc(ref['path'])}</code></a></td>"
        f"<td>{'present' if ref['present'] else 'missing'}</td></tr>"
        for ref in related_docs
    )


def render_html(data: dict[str, Any]) -> str:
    honest = data["honest_state"]
    batch = data["batch_boundary"]
    caveats = "".join(f"<li>{_esc(c)}</li>" for c in data["caveats"])
    tiles = "".join(_tile_html(t) for t in data["surfaces"])

    return (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
        "<title>Lab Operator Surface &mdash; Unified Index (read-only)</title>\n"
        f"<style>{_CSS}</style>\n</head>\n<body>\n"
        "<h1>Lab Operator Surface &mdash; Unified Index</h1>\n"
        f"<p>schema <code>{_esc(data['schema_version'])}</code> &mdash; "
        f"{_esc(data['surface_kind'])}</p>\n"
        f"<div class='banner'>{_esc(_READ_ONLY_BANNER)}</div>\n"
        f"<div class='banner'>{_esc(data['edge_search_hold'])}</div>\n"
        f"<p>as-of label <code>{_esc(data['as_of'])}</code> &mdash; period "
        f"label <code>{_esc(data['period'])}</code> (descriptive only; no clock "
        "is read).</p>\n"
        "<h2>Honest current state</h2>\n"
        f"<div class='banner'>{_esc(honest['note'])}</div>\n"
        "<table><tbody>"
        "<tr><td>candidate ready (committed evidence)</td>"
        f"<td>{_esc(honest['candidate_ready_count'])}</td></tr>"
        "<tr><td>operator gate pending</td>"
        f"<td>{_esc(honest['operator_gate_pending_count'])}</td></tr>"
        "<tr><td>nothing candidate-ready</td>"
        f"<td class='state'>{_esc(str(honest['nothing_candidate_ready']).lower())}</td></tr>"
        "</tbody></table>\n"
        "<h2>Batch boundary (full population, not winners only)</h2>\n"
        "<table><tbody>"
        f"<tr><td>subjects</td><td>{_esc(batch['subject_count'])}</td></tr>"
        "<tr><td>completed experiment runs reached</td>"
        f"<td>{_esc(batch['completed_experiment_run_count'])}</td></tr>"
        f"<tr><td>NO-GO</td><td>{_esc(batch['no_go_count'])}</td></tr>"
        f"<tr><td>blocked</td><td>{_esc(batch['blocked_count'])}</td></tr>"
        "<tr><td>candidate ready for human review</td>"
        f"<td>{_esc(batch['candidate_ready_count'])}</td></tr>"
        "<tr><td>operator gate pending</td>"
        f"<td>{_esc(batch['operator_gate_pending_count'])}</td></tr>"
        "<tr><td>distinct Result Population sets</td>"
        f"<td>{_esc(batch['distinct_result_population_sets'])}</td></tr>"
        "</tbody></table>\n"
        "<h3>Subjects by overall state</h3>\n"
        "<table><thead><tr><th>overall state</th><th>count</th></tr></thead>"
        f"<tbody>{_state_rows(batch['by_overall_state'])}</tbody></table>\n"
        f"<h2>Surfaces</h2>\n{tiles}\n"
        "<h2>Related artifacts and docs</h2>\n"
        "<table><thead><tr><th>role</th><th>path</th><th>present</th></tr>"
        f"</thead><tbody>{_docs_rows(data['related_docs'])}</tbody></table>\n"
        f"<h2>Caveats</h2>\n<ul>{caveats}</ul>\n"
        "</body>\n</html>\n"
    )
