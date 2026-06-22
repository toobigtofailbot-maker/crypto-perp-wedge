"""Render compact operator packets for account-mediated ChatGPT use."""

from __future__ import annotations

import json

from .reasoning_providers import PROVIDER_RESPONSE_SCHEMA, ProviderRequest


def render_chatgpt_request_packet(request: ProviderRequest) -> str:
    context = request.context
    capability_summary = json.dumps(context["capability_assessment"], indent=2, sort_keys=True)
    response_schema = json.dumps(PROVIDER_RESPONSE_SCHEMA, indent=2, sort_keys=True)
    return f"""# Bounded Idea Formalization Request

Request ID: `{request.request_id}`

## Task

Formalize the operator's research idea into the exact JSON response schema below.
Return JSON only. Do not run code, call tools, access APIs, or claim repo facts not
included in this packet.

Idea:

{context["idea"]}

Symbol: `{context.get("symbol") or "BTCUSDT"}`
Timeframe: `{context.get("timeframe") or "15m"}`
Operator constraints: `{json.dumps(context.get("constraints", []))}`

## Repo Capability and Data-Availability Summary

```json
{capability_summary}
```

## Non-Authority Rules

- This is advisory, scratch-only, non-canonical output.
- Do not approve, freeze, register, promote, rank, or declare readiness.
- Do not request paper/live/runtime, backtest, sweep, OMS, risk, capital,
  private-endpoint, credential, or network actions.
- Do not use provider memory as repo truth.
- Reject unsupported, vague, non-causal, non-falsifiable, or unavailable ideas.
- A compiler field existing does not prove historical testability.

## Required JSON Schema

```json
{response_schema}
```
"""
