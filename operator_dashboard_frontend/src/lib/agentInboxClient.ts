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
