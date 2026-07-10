/**
 * Same-origin passthrough for one scratch draft's append-only review trail
 * (WP-INBOX-DRAFT-REVIEW-STATE-03B over the 03A
 * `GET`/`POST /api/agent/drafts/{draft_id}/review-events` endpoints).
 *
 * Like the other Agent Inbox passthroughs, this exists only because the isolated
 * intake service (`tools.agent_inbox_intake`) ships no CORS middleware and this
 * package may not modify it. The browser cannot call the service cross-origin, so
 * the request is routed through the dashboard origin instead.
 *
 * This is not a general forwarder. It exposes exactly two verbs, GET and POST,
 * and no others — there is deliberately no PUT/PATCH/DELETE, matching the service,
 * which offers no edit or delete of an appended event. The draft id is validated
 * against the service's own `AIDRAFT-<16 hex>` shape before any upstream request
 * is made, and the upstream path is otherwise a constant with a constant
 * `/review-events` suffix, so no caller can smuggle an arbitrary path through it.
 * It never contacts the read-only dashboard API. The service's answer — including
 * its own 400/404/422/503 — is returned verbatim with its own status code.
 *
 * Boundary: the POST appends one human review annotation only. It approves,
 * promotes, canonicalizes, queues, and executes nothing. `flagged_for_canonicalization`
 * is an annotation; canonicalization remains a separate, Karl-gated concern that
 * this route neither reaches nor triggers.
 */
import { NextResponse } from "next/server";
import {
  AGENT_INBOX_DRAFTS_UPSTREAM_PATH,
  AGENT_INBOX_ORIGIN_ENV,
  AGENT_INBOX_REVIEW_EVENTS_SUFFIX,
  DRAFT_ID_PATTERN,
} from "@/lib/agentInboxClient";

/** Read the service origin per request, so no origin is baked into the build. */
export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** Reject a malformed id before any request, and resolve the single upstream URL. */
function resolveUpstream(draftId: string):
  | { ok: true; upstream: string }
  | { ok: false; response: NextResponse } {
  if (!DRAFT_ID_PATTERN.test(draftId)) {
    return {
      ok: false,
      response: NextResponse.json(
        {
          detail:
            "draft_id must match AIDRAFT-<16 uppercase hex characters>. No request was made.",
        },
        { status: 400 },
      ),
    };
  }

  const origin = process.env[AGENT_INBOX_ORIGIN_ENV]?.trim();
  if (!origin) {
    return {
      ok: false,
      response: NextResponse.json(
        {
          detail: `${AGENT_INBOX_ORIGIN_ENV} is not set, so no isolated intake service origin is configured. No review trail was read or written.`,
          agent_inbox_unconfigured: true,
        },
        { status: 503 },
      ),
    };
  }

  const upstream = `${origin.replace(/\/+$/, "")}${AGENT_INBOX_DRAFTS_UPSTREAM_PATH}/${draftId}${AGENT_INBOX_REVIEW_EVENTS_SUFFIX}`;
  return { ok: true, upstream };
}

/** Forward the service's answer untouched, or report that it was never reached. */
function unreachable(upstream: string): NextResponse {
  return NextResponse.json(
    {
      detail: `Could not reach the isolated intake service at ${upstream}. It may not be running. No review trail was read or written.`,
      agent_inbox_unreachable: true,
    },
    { status: 502 },
  );
}

export async function GET(
  _request: Request,
  { params }: { params: { draft_id: string } },
) {
  const resolved = resolveUpstream(params.draft_id);
  if (!resolved.ok) return resolved.response;

  let response: Response;
  try {
    response = await fetch(resolved.upstream, {
      method: "GET",
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    return unreachable(resolved.upstream);
  }

  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}

export async function POST(
  request: Request,
  { params }: { params: { draft_id: string } },
) {
  const resolved = resolveUpstream(params.draft_id);
  if (!resolved.ok) return resolved.response;

  const body = await request.text();

  let response: Response;
  try {
    response = await fetch(resolved.upstream, {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body,
    });
  } catch {
    return unreachable(resolved.upstream);
  }

  // Return the service's answer untouched, success or rejection alike.
  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
