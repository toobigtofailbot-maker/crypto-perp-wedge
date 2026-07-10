/**
 * Same-origin read-only passthrough for one Agent Inbox scratch draft packet
 * (WP-INBOX-DRAFT-HISTORY-02B over the 02A `GET /api/agent/drafts/{draft_id}`).
 *
 * Like the list passthrough, this exists only because the isolated intake
 * service ships no CORS middleware and this package may not modify it.
 *
 * The draft id is validated against the service's own `AIDRAFT-<16 hex>` shape
 * before any request is made, and the upstream path is otherwise a constant.
 * That keeps this from becoming a general forwarder: a caller cannot smuggle an
 * arbitrary path segment through it. It exposes only GET, so it can neither
 * submit nor mutate anything, and it never contacts the read-only dashboard API.
 * The service's answer — including its own 400/404/503 — is returned verbatim.
 */
import { NextResponse } from "next/server";
import {
  AGENT_INBOX_DRAFTS_UPSTREAM_PATH,
  AGENT_INBOX_ORIGIN_ENV,
  DRAFT_ID_PATTERN,
} from "@/lib/agentInboxClient";

/** Read the service origin per request, so no origin is baked into the build. */
export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(
  _request: Request,
  { params }: { params: { draft_id: string } },
) {
  const draftId = params.draft_id;
  if (!DRAFT_ID_PATTERN.test(draftId)) {
    return NextResponse.json(
      {
        detail:
          "draft_id must match AIDRAFT-<16 uppercase hex characters>. No request was made.",
      },
      { status: 400 },
    );
  }

  const origin = process.env[AGENT_INBOX_ORIGIN_ENV]?.trim();
  if (!origin) {
    return NextResponse.json(
      {
        detail: `${AGENT_INBOX_ORIGIN_ENV} is not set, so no isolated intake service origin is configured. No draft was read.`,
        agent_inbox_unconfigured: true,
      },
      { status: 503 },
    );
  }

  const upstream = `${origin.replace(/\/+$/, "")}${AGENT_INBOX_DRAFTS_UPSTREAM_PATH}/${draftId}`;

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
        detail: `Could not reach the isolated intake service at ${upstream}. It may not be running. No draft was read.`,
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
