/**
 * Browser-side client for the ISOLATED Agent Inbox scratch intake draft service
 * (`tools.agent_inbox_intake`, WP-DASH-AGENT-INBOX-WRITE-01A).
 *
 * This module is deliberately separate from `@/lib/apiClient`, which is the
 * GET-only client for the read-only dashboard API (`tools.operator_dashboard_api`).
 * The two are different FastAPI apps. The dashboard API mounts no POST route at
 * all and still projects `agent_inbox_write` as unavailable. Nothing in this
 * file reads from, writes to, or otherwise touches the dashboard API.
 *
 * Why the browser does not call the intake service directly: that service ships
 * no CORS middleware. A cross-origin JSON POST is preceded by an `OPTIONS`
 * preflight, which the service answers `405` with no `Access-Control-Allow-Origin`
 * header, so every browser blocks the request. Rather than change the service —
 * which this package may not do — the request goes to the same-origin passthrough
 * at `AGENT_INBOX_PROXY_PATH`, whose only possible upstream is the one endpoint
 * below.
 *
 * Boundary: one endpoint, one verb. This module defines no execution, approval,
 * promotion, crossing, candidate, runner, pipeline, scheduler, notification, or
 * paper/live call, and no generic `request(method, ...)` escape hatch. The
 * returned packet is review material only: not evidence, authority, approval,
 * recommendation, ranking, readiness, promotion, or execution input.
 */

/** Same-origin passthrough this client posts to. Served by the Next route handler. */
export const AGENT_INBOX_PROXY_PATH = "/agent-inbox/intake-draft";

/** The single upstream endpoint on the isolated service. The proxy hardcodes it. */
export const AGENT_INBOX_UPSTREAM_PATH = "/api/agent/intake-draft";

/**
 * Read-only draft history (WP-INBOX-DRAFT-HISTORY-02A/02B). These are GET-only
 * views of scratch packets already written; they submit and mutate nothing. Each
 * has a same-origin passthrough (the service ships no CORS) whose upstream is a
 * single hardcoded read endpoint, so neither passthrough is a general forwarder.
 */
export const AGENT_INBOX_DRAFTS_PROXY_PATH = "/agent-inbox/drafts";
export const AGENT_INBOX_DRAFTS_UPSTREAM_PATH = "/api/agent/drafts";

/** `AIDRAFT-<16 uppercase hex>`; mirrors `DRAFT_ID_RE` in the 02A service. */
export const DRAFT_ID_PATTERN = /^AIDRAFT-[A-F0-9]{16}$/;

/** Same-origin passthrough for one draft's stored packet. */
export function agentInboxDraftDetailProxyPath(draftId: string): string {
  return `${AGENT_INBOX_DRAFTS_PROXY_PATH}/${encodeURIComponent(draftId)}`;
}

/** Server-only env var naming the isolated service origin, e.g. `http://127.0.0.1:8100`. */
export const AGENT_INBOX_ORIGIN_ENV = "AGENT_INBOX_SERVICE_ORIGIN";

/**
 * Mirrors `LOCKED_TIMEFRAMES` in `tools/research_agents/idea_formalizer_agent.py`.
 * The service rejects anything outside this set, so the UI offers only these.
 */
export const LOCKED_TIMEFRAMES = ["15m", "30m", "1h", "4h", "1d"] as const;
export type LockedTimeframe = (typeof LOCKED_TIMEFRAMES)[number];

/** Field bounds from `IntakeDraftRequest` in `tools/agent_inbox_intake/models.py`. */
export const FIELD_LIMITS = {
  title: 120,
  hypothesis_text: 4000,
  market_hint: 80,
  constraints_notes: 1200,
  submitter_label: 80,
} as const;

/**
 * `service.py::_normalise_request` also caps the combined length of
 * title + hypothesis_text + constraints_notes.
 */
export const MAX_COMBINED_TEXT_LENGTH = 5200;

/**
 * The request body. `IntakeDraftRequest` sets `extra="forbid"`, so no key
 * outside this shape may be sent. Optional keys are omitted, not sent empty.
 */
export interface IntakeDraftRequest {
  title: string;
  hypothesis_text: string;
  market_hint?: string;
  timeframe_hint?: LockedTimeframe;
  constraints_notes?: string;
  submitter_label?: string;
}

export interface FeatureAssessment {
  feature: string;
  compiler_field_exists: boolean;
  coverage_class: string;
  historical_testability: string;
  source_class: string;
  warnings: string[];
}

export interface CapabilityAssessment {
  detected_features: string[];
  blocking_features: string[];
  historically_testable_now: boolean;
  distinction: string;
  feature_assessments: FeatureAssessment[];
}

export interface ParameterBound {
  name: string;
  minimum: number;
  maximum: number;
}

/** The formalizer's draft language. Not a Strategy Spec — see `draft_strategy_spec`. */
export interface ResearchObject {
  summary?: string;
  causal_rationale?: string;
  falsifiable_prediction?: string;
  entry_concept?: string;
  exit_concept?: string;
  features?: string[];
  symbols?: string[];
  timeframe?: string;
  parameter_bounds?: ParameterBound[];
  stop_conditions?: string[];
}

export interface FormalizerResult {
  schema_version?: string;
  status?: string;
  run_id?: string;
  rejection_reasons?: string[];
  research_object?: ResearchObject | null;
  /** `produced` is always false: 01A disables Strategy Spec emission outright. */
  draft_strategy_spec?: {
    produced?: boolean;
    path?: string | null;
    blockers?: string[];
  } | null;
  capability_assessment?: CapabilityAssessment | null;
  provider_metadata?: {
    provider_id?: string;
    provider_mode?: string;
    api_call_made?: boolean;
    response_source?: string;
    request_id?: string;
  } | null;
  non_authority?: Record<string, boolean>;
}

export interface DraftProvenance {
  service_namespace?: string;
  package_id?: string;
  formalizer_module?: string;
  formalizer_mode?: string;
  provider_mode?: string;
  provider_id?: string;
  tool_context_role?: string;
  tool_context_wp_id?: string;
  output_path?: string;
  formalizer_writes_captured_in_memory?: boolean;
  captured_formalizer_write_paths?: string[];
}

export interface ToolContextAuditRecord {
  action_type: string;
  decision: string;
  target_path: string;
  role: string;
  policy_id: string;
  reason: string;
  timestamp_utc: string;
  wp_id: string;
  non_authority: string;
}

/** `agent_inbox_intake_draft_packet_v1`, as returned and persisted by the service. */
export interface AgentInboxDraftPacket {
  schema_version: string;
  draft_id: string;
  created_at: string;
  source_request: Record<string, string | null>;
  formalizer_result: FormalizerResult;
  availability_primitive_check?: CapabilityAssessment | null;
  open_questions: string[];
  blockers: string[];
  warnings: string[];
  non_authority_flags: Record<string, boolean>;
  provenance: DraftProvenance;
  source_hashes: Record<string, string>;
  tool_context_audit: ToolContextAuditRecord[];
  fabricated: boolean;
}

/** The service is unconfigured or unreachable. Never stands in for a real packet. */
export class AgentInboxUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AgentInboxUnavailableError";
  }
}

/** The service was reached and rejected the request. Carries its own words. */
export class AgentInboxRejectedError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "AgentInboxRejectedError";
    this.status = status;
  }
}

/** Shape the passthrough uses to report that it never reached the service. */
interface ProxyFailureBody {
  detail?: unknown;
  agent_inbox_unconfigured?: boolean;
  agent_inbox_unreachable?: boolean;
}

/** FastAPI reports `IntakeDraftError` as 400 (string detail) and schema failures as 422 (list). */
function describeDetail(detail: unknown, status: number): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((entry) => {
        const { loc, msg } = entry as { loc?: unknown[]; msg?: string };
        const field = Array.isArray(loc) ? loc.slice(1).join(".") : "";
        return field && msg ? `${field}: ${msg}` : (msg ?? "");
      })
      .filter(Boolean);
    if (messages.length > 0) return messages.join("; ");
  }
  return `The intake service answered with status ${status}.`;
}

/**
 * Submit one bounded idea and receive the scratch-only draft packet.
 *
 * Throws `AgentInboxUnavailableError` when the service is unconfigured or
 * unreachable, and `AgentInboxRejectedError` when the service answers non-2xx.
 * Neither is ever converted into a synthesized packet.
 */
export async function postIntakeDraft(
  request: IntakeDraftRequest,
): Promise<AgentInboxDraftPacket> {
  let response: Response;
  try {
    response = await fetch(AGENT_INBOX_PROXY_PATH, {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(request),
    });
  } catch {
    throw new AgentInboxUnavailableError(
      "The dashboard could not reach its own intake passthrough.",
    );
  }

  if (response.ok) {
    return (await response.json()) as AgentInboxDraftPacket;
  }

  let body: ProxyFailureBody = {};
  try {
    body = (await response.json()) as ProxyFailureBody;
  } catch {
    throw new AgentInboxRejectedError(
      response.status,
      `The intake service answered with status ${response.status}.`,
    );
  }

  const message = describeDetail(body.detail, response.status);
  if (body.agent_inbox_unconfigured || body.agent_inbox_unreachable) {
    throw new AgentInboxUnavailableError(message);
  }
  throw new AgentInboxRejectedError(response.status, message);
}

/**
 * The compact per-draft non-authority posture echoed by the 02A list endpoint.
 * A summary of the packet's own flags, not a separate verdict.
 */
export interface AgentInboxDraftListNonAuthority {
  scratch_only: boolean;
  noncanonical: boolean;
  draft_only: boolean;
  review_only: boolean;
  not_approval: boolean;
  not_promotion: boolean;
  not_execution: boolean;
}

/**
 * One row of the draft history list, exactly as `list_intake_drafts` projects
 * it. These are compact metadata for orientation, not the full packet — opening
 * a draft fetches the stored packet whole via {@link getIntakeDraft}.
 */
export interface AgentInboxDraftSummary {
  draft_id: string;
  created_at: string;
  schema_version: string;
  title: string | null;
  submitter_label: string | null;
  market_hint: string | null;
  timeframe_hint: string | null;
  hypothesis_preview: string | null;
  blocker_count: number;
  warning_count: number;
  open_question_count: number;
  fabricated: boolean;
  non_authority: AgentInboxDraftListNonAuthority;
  source_packet_path: string;
}

/** The envelope returned by `GET /api/agent/drafts`, forwarded verbatim. */
export interface AgentInboxDraftListEnvelope {
  status: "available" | "empty";
  count: number;
  drafts: AgentInboxDraftSummary[];
  storage_source: string;
  scratch_only: boolean;
}

/**
 * Read the scratch draft history from the isolated service via the same-origin
 * passthrough. GET only; nothing is submitted, and no packet is synthesized when
 * the service is unconfigured or unreachable — those raise
 * `AgentInboxUnavailableError`. A malformed-history 503 raises
 * `AgentInboxRejectedError` with the service's own words.
 */
export async function getIntakeDrafts(): Promise<AgentInboxDraftListEnvelope> {
  let response: Response;
  try {
    response = await fetch(AGENT_INBOX_DRAFTS_PROXY_PATH, {
      method: "GET",
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new AgentInboxUnavailableError(
      "The dashboard could not reach its own draft-history passthrough.",
    );
  }

  if (response.ok) {
    return (await response.json()) as AgentInboxDraftListEnvelope;
  }

  let body: ProxyFailureBody = {};
  try {
    body = (await response.json()) as ProxyFailureBody;
  } catch {
    throw new AgentInboxRejectedError(
      response.status,
      `The intake service answered with status ${response.status}.`,
    );
  }

  const message = describeDetail(body.detail, response.status);
  if (body.agent_inbox_unconfigured || body.agent_inbox_unreachable) {
    throw new AgentInboxUnavailableError(message);
  }
  throw new AgentInboxRejectedError(response.status, message);
}

/* ------------------------------------------------------------------------- *
 * Scratch draft review trail (WP-INBOX-DRAFT-REVIEW-STATE-03A/03B)
 *
 * Append-only human review annotations over an existing scratch draft. The
 * `GET` reads the trail; the `POST` appends exactly one event. Both go through a
 * same-origin passthrough because the isolated service (`tools.agent_inbox_intake`)
 * ships no CORS, and each passthrough hardcodes one upstream endpoint per verb —
 * neither is a general forwarder. A review event is annotation only: it does not
 * approve, promote, canonicalize, admit to a queue, create a candidate, or
 * authorize research/paper/live/runtime execution. In particular
 * `flagged_for_canonicalization` is a note that a human may later pursue a
 * separate Karl-gated canonicalization review; it creates and approves nothing.
 * ------------------------------------------------------------------------- */

/** The four review states the 03A service accepts. Mirrors `ALLOWED_REVIEW_STATES`. */
export const REVIEW_STATES = [
  "reviewed",
  "rejected",
  "needs_clarification",
  "flagged_for_canonicalization",
] as const;
export type ReviewState = (typeof REVIEW_STATES)[number];

/** Field bounds from `DraftReviewEventRequest` in `tools/agent_inbox_intake/models.py`. */
export const REVIEW_FIELD_LIMITS = {
  reviewer_label: 80,
  rationale: 1200,
  clarification_request: 1200,
} as const;

/** Upstream suffix appended to `/api/agent/drafts/{draft_id}`. The proxy hardcodes it. */
export const AGENT_INBOX_REVIEW_EVENTS_SUFFIX = "/review-events";

/** Same-origin passthrough for one draft's append-only review trail. */
export function agentInboxReviewEventsProxyPath(draftId: string): string {
  return `${AGENT_INBOX_DRAFTS_PROXY_PATH}/${encodeURIComponent(draftId)}${AGENT_INBOX_REVIEW_EVENTS_SUFFIX}`;
}

/**
 * The request body for one appended review event. The service model sets
 * `extra="forbid"`, so no key outside this shape may be sent; `clarification_request`
 * is omitted, not sent empty, when the reviewer leaves it blank.
 */
export interface AgentInboxReviewEventRequest {
  review_state: ReviewState;
  reviewer_label: string;
  rationale: string;
  clarification_request?: string;
}

/**
 * The explicit non-authority posture the service stamps onto every review event.
 * Kept open (`Record`) so it renders verbatim through `FlagGrid`; the 03A service
 * currently stamps exactly: `scratch_only`, `annotation_only`,
 * `not_canonicalization_approval`, `not_queue_admission`, `not_research_execution`,
 * `not_candidate_creation`, and `not_runtime_action`.
 */
export type AgentInboxReviewNonAuthorityFlags = Record<string, boolean>;

/**
 * One stored review event, exactly as `append_draft_review_event` writes it and
 * `list_draft_review_events` reads it back. `append_index` is 1-based and defines
 * the append order; the trail is never reordered or edited.
 */
export interface AgentInboxReviewEvent {
  schema_version: string;
  event_id: string;
  draft_id: string;
  append_index: number;
  review_state: string;
  reviewer_label: string;
  timestamp_utc: string;
  rationale: string;
  clarification_request: string | null;
  non_authority_flags: AgentInboxReviewNonAuthorityFlags;
}

/** The envelope returned by `GET /api/agent/drafts/{draft_id}/review-events`. */
export interface AgentInboxReviewTrailEnvelope {
  draft_id: string;
  count: number;
  review_events: AgentInboxReviewEvent[];
  storage_source: string;
  append_only: boolean;
  scratch_only: boolean;
  canonical_authority: boolean;
}

/** The body returned by the append POST: the new event plus the whole current trail. */
export interface AgentInboxReviewAppendResult {
  event: AgentInboxReviewEvent;
  review_trail: AgentInboxReviewTrailEnvelope;
}

/**
 * Read the append-only review trail for one existing scratch draft via the
 * same-origin passthrough. GET only; nothing is submitted. Unconfigured/unreachable
 * raise `AgentInboxUnavailableError`; a rejected/missing draft (400/404/503)
 * raises `AgentInboxRejectedError`. The trail is review material only — not
 * approval, ranking, readiness, canonicalization, queue admission, or execution.
 */
export async function getDraftReviewEvents(
  draftId: string,
): Promise<AgentInboxReviewTrailEnvelope> {
  let response: Response;
  try {
    response = await fetch(agentInboxReviewEventsProxyPath(draftId), {
      method: "GET",
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new AgentInboxUnavailableError(
      "The dashboard could not reach its own review-trail passthrough.",
    );
  }

  if (response.ok) {
    return (await response.json()) as AgentInboxReviewTrailEnvelope;
  }

  let body: ProxyFailureBody = {};
  try {
    body = (await response.json()) as ProxyFailureBody;
  } catch {
    throw new AgentInboxRejectedError(
      response.status,
      `The intake service answered with status ${response.status}.`,
    );
  }

  const message = describeDetail(body.detail, response.status);
  if (body.agent_inbox_unconfigured || body.agent_inbox_unreachable) {
    throw new AgentInboxUnavailableError(message);
  }
  throw new AgentInboxRejectedError(response.status, message);
}

/**
 * Append exactly one human review annotation to a scratch draft's trail via the
 * same-origin passthrough. This is the only write in this module besides intake,
 * and it appends review material only: it approves, promotes, canonicalizes,
 * queues, and executes nothing. Unconfigured/unreachable raise
 * `AgentInboxUnavailableError`; a rejected request (400/404/422/503) raises
 * `AgentInboxRejectedError` with the service's own words. The returned trail is
 * the service's, unchanged.
 */
export async function appendDraftReviewEvent(
  draftId: string,
  request: AgentInboxReviewEventRequest,
): Promise<AgentInboxReviewAppendResult> {
  let response: Response;
  try {
    response = await fetch(agentInboxReviewEventsProxyPath(draftId), {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(request),
    });
  } catch {
    throw new AgentInboxUnavailableError(
      "The dashboard could not reach its own review-trail passthrough.",
    );
  }

  if (response.ok) {
    return (await response.json()) as AgentInboxReviewAppendResult;
  }

  let body: ProxyFailureBody = {};
  try {
    body = (await response.json()) as ProxyFailureBody;
  } catch {
    throw new AgentInboxRejectedError(
      response.status,
      `The intake service answered with status ${response.status}.`,
    );
  }

  const message = describeDetail(body.detail, response.status);
  if (body.agent_inbox_unconfigured || body.agent_inbox_unreachable) {
    throw new AgentInboxUnavailableError(message);
  }
  throw new AgentInboxRejectedError(response.status, message);
}

/**
 * Read one stored scratch packet by id via the same-origin passthrough. GET
 * only. Unconfigured/unreachable raise `AgentInboxUnavailableError`; a rejected
 * or missing draft (400/404/503) raises `AgentInboxRejectedError`. The returned
 * packet is the persisted JSON, unchanged; it is review material only.
 */
export async function getIntakeDraft(
  draftId: string,
): Promise<AgentInboxDraftPacket> {
  let response: Response;
  try {
    response = await fetch(agentInboxDraftDetailProxyPath(draftId), {
      method: "GET",
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new AgentInboxUnavailableError(
      "The dashboard could not reach its own draft-history passthrough.",
    );
  }

  if (response.ok) {
    return (await response.json()) as AgentInboxDraftPacket;
  }

  let body: ProxyFailureBody = {};
  try {
    body = (await response.json()) as ProxyFailureBody;
  } catch {
    throw new AgentInboxRejectedError(
      response.status,
      `The intake service answered with status ${response.status}.`,
    );
  }

  const message = describeDetail(body.detail, response.status);
  if (body.agent_inbox_unconfigured || body.agent_inbox_unreachable) {
    throw new AgentInboxUnavailableError(message);
  }
  throw new AgentInboxRejectedError(response.status, message);
}
