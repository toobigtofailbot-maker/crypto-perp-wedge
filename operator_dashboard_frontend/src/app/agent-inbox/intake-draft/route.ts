/**
 * Same-origin passthrough to the isolated Agent Inbox intake service.
 *
 * This exists for one reason: `tools.agent_inbox_intake` ships no CORS
 * middleware, so it answers a browser preflight with `405` and no
 * `Access-Control-Allow-Origin` header. A cross-origin JSON POST from this
 * dashboard is therefore impossible, and this package may not modify that
 * service. Routing the POST through the dashboard origin resolves it without
 * touching the service or its contract.
 *
 * This handler holds no logic of its own. It does not validate, normalize,
 * enrich, retry, cache, persist, or interpret anything. It forwards one body to
 * one hardcoded upstream path and returns whatever the service said, verbatim,
 * with the service's own status code. Every rule about what an idea may contain
 * — the BTCUSDT bound, the locked timeframe set, the combined length cap —
 * stays where 01A put it, inside the service.
 *
 * Boundary: the upstream path is a constant, so this cannot be used as a
 * general-purpose forwarder. It reaches exactly one scratch-write endpoint and
 * exposes no execution, approval, promotion, crossing, candidate, runner,
 * pipeline, scheduler, notification, paper/live, or runtime call. It never
 * contacts the read-only dashboard API.
 */
import { NextResponse } from "next/server";
import {
  AGENT_INBOX_ORIGIN_ENV,
  AGENT_INBOX_UPSTREAM_PATH,
} from "@/lib/agentInboxClient";

/** Read the service origin per request, so no origin is baked into the build. */
export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(request: Request) {
  const origin = process.env[AGENT_INBOX_ORIGIN_ENV]?.trim();
  if (!origin) {
    return NextResponse.json(
      {
        detail: `${AGENT_INBOX_ORIGIN_ENV} is not set, so no isolated intake service origin is configured. No draft was created.`,
        agent_inbox_unconfigured: true,
      },
      { status: 503 },
    );
  }

  const body = await request.text();
  const upstream = `${origin.replace(/\/+$/, "")}${AGENT_INBOX_UPSTREAM_PATH}`;

  let response: Response;
  try {
    response = await fetch(upstream, {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body,
    });
  } catch {
    return NextResponse.json(
      {
        detail: `Could not reach the isolated intake service at ${upstream}. It may not be running. No draft was created.`,
        agent_inbox_unreachable: true,
      },
      { status: 502 },
    );
  }

  // Return the service's answer untouched, success or rejection alike.
  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
