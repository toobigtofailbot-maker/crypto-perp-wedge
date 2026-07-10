/**
 * Same-origin read-only passthrough for the Agent Inbox scratch draft history
 * list (WP-INBOX-DRAFT-HISTORY-02B over the 02A `GET /api/agent/drafts`).
 *
 * It exists for the same single reason as the intake passthrough: the isolated
 * `tools.agent_inbox_intake` service ships no CORS middleware, so the browser
 * cannot read it cross-origin, and this package may not modify that service.
 *
 * This handler holds no logic of its own. It forwards nothing but the method to
 * one hardcoded upstream path and returns whatever the service said, verbatim,
 * with the service's own status code. It exposes only GET — there is no POST,
 * PUT, PATCH, or DELETE here — so it can neither submit an idea nor mutate a
 * stored packet. The upstream path is a constant, so this cannot be used as a
 * general-purpose forwarder, and it never contacts the read-only dashboard API.
 */
import { NextResponse } from "next/server";
import {
  AGENT_INBOX_DRAFTS_UPSTREAM_PATH,
  AGENT_INBOX_ORIGIN_ENV,
} from "@/lib/agentInboxClient";

/** Read the service origin per request, so no origin is baked into the build. */
export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  const origin = process.env[AGENT_INBOX_ORIGIN_ENV]?.trim();
  if (!origin) {
    return NextResponse.json(
      {
        detail: `${AGENT_INBOX_ORIGIN_ENV} is not set, so no isolated intake service origin is configured. No draft history can be read.`,
        agent_inbox_unconfigured: true,
      },
      { status: 503 },
    );
  }

  const upstream = `${origin.replace(/\/+$/, "")}${AGENT_INBOX_DRAFTS_UPSTREAM_PATH}`;

  let response: Response;
  try {
    response = await fetch(upstream, {
      method: "GET",
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    return NextResponse.json(
      {
        detail: `Could not reach the isolated intake service at ${upstream}. It may not be running. No draft history was read.`,
        agent_inbox_unreachable: true,
      },
      { status: 502 },
    );
  }

  // Return the service's answer untouched, success or failure alike.
  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
