"use client";

/**
 * The Agent Inbox intake form: the one form and the one submit button in this
 * dashboard.
 *
 * Its only submit target is the same-origin passthrough to the isolated
 * scratch-write service. It renders no run, approve, execute, promote, cross,
 * trade, create-candidate, or send-to-pipeline control, and it never contacts
 * the read-only dashboard API.
 *
 * Nothing typed here is persisted client-side: no localStorage, no
 * sessionStorage, no cookie. Reloading the page discards the draft, which is
 * the intended behavior — the service holds the packet, the browser does not.
 *
 * When the service is unconfigured or unreachable the form says so plainly. It
 * never synthesizes a draft packet to stand in for a real response.
 */

import { useState } from "react";
import { Badge, Card, CardTitle } from "@/components/ui";
import { UnavailableState } from "@/components/States";
import { DraftPacketView } from "@/components/agent-inbox/DraftPacketView";
import {
  AGENT_INBOX_ORIGIN_ENV,
  AGENT_INBOX_UPSTREAM_PATH,
  AgentInboxRejectedError,
  AgentInboxUnavailableError,
  FIELD_LIMITS,
  LOCKED_TIMEFRAMES,
  MAX_COMBINED_TEXT_LENGTH,
  postIntakeDraft,
  type AgentInboxDraftPacket,
  type IntakeDraftRequest,
  type LockedTimeframe,
} from "@/lib/agentInboxClient";

type Submission =
  | { state: "idle" }
  | { state: "submitting" }
  | { state: "success"; packet: AgentInboxDraftPacket }
  | { state: "error"; message: string; unreachable: boolean };

const EMPTY_FIELDS = {
  title: "",
  hypothesisText: "",
  marketHint: "BTCUSDT",
  timeframeHint: "15m" as LockedTimeframe,
  constraintsNotes: "",
  submitterLabel: "",
};

/** Mirrors the service rule: market_hint must still resolve to BTCUSDT. */
function looksBoundedToBtcusdt(marketHint: string): boolean {
  return marketHint.toUpperCase().replace(/[-_]/g, "").includes("BTCUSDT");
}

const inputClass =
  "w-full rounded border border-cockpit-border bg-cockpit-panel-2 px-2 py-1.5 text-sm text-cockpit-text placeholder:text-cockpit-muted focus:border-cockpit-accent focus:outline-none disabled:opacity-50";

function Field({
  htmlFor,
  label,
  hint,
  children,
}: {
  htmlFor: string;
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor={htmlFor}
        className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted"
      >
        {label}
      </label>
      {children}
      {hint ? <p className="text-xs text-cockpit-muted">{hint}</p> : null}
    </div>
  );
}

/**
 * `serviceConfigured` and `serviceOrigin` are resolved on the server, where the
 * origin env var lives. The origin is shown for operator orientation only; the
 * browser never fetches it directly.
 */
export function IntakeForm({
  serviceConfigured,
  serviceOrigin,
}: {
  serviceConfigured: boolean;
  serviceOrigin: string | null;
}) {
  const [fields, setFields] = useState(EMPTY_FIELDS);
  const [submission, setSubmission] = useState<Submission>({ state: "idle" });

  const configured = serviceConfigured;

  const title = fields.title.trim();
  const hypothesis = fields.hypothesisText.trim();
  const constraints = fields.constraintsNotes.trim();
  const combinedLength = title.length + hypothesis.length + constraints.length;

  const overCombinedLimit = combinedLength > MAX_COMBINED_TEXT_LENGTH;
  const marketHintOffBounds =
    fields.marketHint.trim().length > 0 &&
    !looksBoundedToBtcusdt(fields.marketHint);

  const submitting = submission.state === "submitting";
  const canSubmit =
    configured &&
    !submitting &&
    title.length > 0 &&
    hypothesis.length > 0 &&
    !overCombinedLimit;

  function update<K extends keyof typeof EMPTY_FIELDS>(
    key: K,
    value: (typeof EMPTY_FIELDS)[K],
  ) {
    setFields((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;

    // `IntakeDraftRequest` forbids extra keys; omit optionals rather than
    // sending empty strings the service would only have to strip.
    const request: IntakeDraftRequest = {
      title,
      hypothesis_text: hypothesis,
      timeframe_hint: fields.timeframeHint,
    };
    const marketHint = fields.marketHint.trim();
    if (marketHint) request.market_hint = marketHint;
    if (constraints) request.constraints_notes = constraints;
    const submitterLabel = fields.submitterLabel.trim();
    if (submitterLabel) request.submitter_label = submitterLabel;

    setSubmission({ state: "submitting" });
    try {
      const packet = await postIntakeDraft(request);
      setSubmission({ state: "success", packet });
    } catch (error) {
      if (error instanceof AgentInboxUnavailableError) {
        setSubmission({ state: "error", message: error.message, unreachable: true });
      } else if (error instanceof AgentInboxRejectedError) {
        setSubmission({
          state: "error",
          message: `The intake service rejected this idea (HTTP ${error.status}): ${error.message}`,
          unreachable: false,
        });
      } else {
        setSubmission({
          state: "error",
          message:
            error instanceof Error
              ? error.message
              : "The intake service returned an unreadable response.",
          unreachable: false,
        });
      }
    }
  }

  function handleClear() {
    setFields(EMPTY_FIELDS);
    setSubmission({ state: "idle" });
  }

  return (
    <div className="flex flex-col gap-4">
      {configured ? null : (
        <UnavailableState
          title="Intake service not configured"
          reason={`${AGENT_INBOX_ORIGIN_ENV} is not set, so this dashboard has no origin for the isolated Agent Inbox intake service. The form below is shown disabled so you can see exactly what it would collect. No draft can be submitted, and none is simulated.`}
        />
      )}

      <Card>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <CardTitle>Submit an idea for a scratch draft</CardTitle>
          <Badge tone={configured ? "info" : "warn"}>
            {configured ? "POST" : "no target"} {AGENT_INBOX_UPSTREAM_PATH}
          </Badge>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <fieldset
            disabled={!configured || submitting}
            className="flex flex-col gap-4 border-0 p-0"
          >
            <Field
              htmlFor="intake-title"
              label="Idea title"
              hint={`Required. Up to ${FIELD_LIMITS.title} characters.`}
            >
              <input
                id="intake-title"
                name="title"
                type="text"
                required
                maxLength={FIELD_LIMITS.title}
                value={fields.title}
                onChange={(event) => update("title", event.target.value)}
                placeholder="EMA momentum continuation"
                className={inputClass}
              />
            </Field>

            <Field
              htmlFor="intake-hypothesis"
              label="Hypothesis / idea"
              hint={`Required. State the claimed edge and why it should exist. Up to ${FIELD_LIMITS.hypothesis_text} characters.`}
            >
              <textarea
                id="intake-hypothesis"
                name="hypothesis_text"
                required
                rows={6}
                maxLength={FIELD_LIMITS.hypothesis_text}
                value={fields.hypothesisText}
                onChange={(event) =>
                  update("hypothesisText", event.target.value)
                }
                placeholder="BTCUSDT 15m EMA momentum persists because slow information diffusion keeps pressure moving in the same direction after completed bars."
                className={`${inputClass} resize-y`}
              />
            </Field>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Field
                htmlFor="intake-market"
                label="Market / instrument hint"
                hint="Optional. The service is bounded to BTCUSDT and rejects anything else."
              >
                <input
                  id="intake-market"
                  name="market_hint"
                  type="text"
                  maxLength={FIELD_LIMITS.market_hint}
                  value={fields.marketHint}
                  onChange={(event) => update("marketHint", event.target.value)}
                  className={inputClass}
                />
              </Field>

              <Field
                htmlFor="intake-timeframe"
                label="Timeframe hint"
                hint="Optional. Restricted to the locked timeframe set."
              >
                <select
                  id="intake-timeframe"
                  name="timeframe_hint"
                  value={fields.timeframeHint}
                  onChange={(event) =>
                    update("timeframeHint", event.target.value as LockedTimeframe)
                  }
                  className={inputClass}
                >
                  {LOCKED_TIMEFRAMES.map((timeframe) => (
                    <option key={timeframe} value={timeframe}>
                      {timeframe}
                    </option>
                  ))}
                </select>
              </Field>
            </div>

            <Field
              htmlFor="intake-constraints"
              label="Constraints / notes"
              hint={`Optional. Up to ${FIELD_LIMITS.constraints_notes} characters.`}
            >
              <textarea
                id="intake-constraints"
                name="constraints_notes"
                rows={3}
                maxLength={FIELD_LIMITS.constraints_notes}
                value={fields.constraintsNotes}
                onChange={(event) =>
                  update("constraintsNotes", event.target.value)
                }
                placeholder="Review only. Keep this as a scratch draft packet."
                className={`${inputClass} resize-y`}
              />
            </Field>

            <Field
              htmlFor="intake-submitter"
              label="Submitter label"
              hint={`Optional. Recorded in the packet source_request. Up to ${FIELD_LIMITS.submitter_label} characters.`}
            >
              <input
                id="intake-submitter"
                name="submitter_label"
                type="text"
                maxLength={FIELD_LIMITS.submitter_label}
                value={fields.submitterLabel}
                onChange={(event) =>
                  update("submitterLabel", event.target.value)
                }
                className={inputClass}
              />
            </Field>
          </fieldset>

          <div className="flex flex-col gap-2 border-t border-cockpit-border/50 pt-3">
            {marketHintOffBounds ? (
              <p className="text-xs text-cockpit-warn">
                The service requires the market hint to resolve to BTCUSDT and
                will reject this value.
              </p>
            ) : null}
            {overCombinedLimit ? (
              <p className="text-xs text-cockpit-bad">
                Title, hypothesis, and notes total {combinedLength} characters,
                over the bounded service limit of {MAX_COMBINED_TEXT_LENGTH}.
              </p>
            ) : null}

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                disabled={!canSubmit}
                className="rounded border border-cockpit-accent bg-cockpit-accent/10 px-3 py-1.5 text-sm font-medium text-cockpit-accent hover:bg-cockpit-accent/20 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {submitting ? "Creating draft…" : "Create scratch draft"}
              </button>
              <button
                type="button"
                onClick={handleClear}
                disabled={submitting}
                className="rounded border border-cockpit-border px-3 py-1.5 text-sm text-cockpit-muted hover:text-cockpit-text disabled:opacity-40"
              >
                Clear form
              </button>
              <span className="text-xs text-cockpit-muted">
                {combinedLength} / {MAX_COMBINED_TEXT_LENGTH} combined characters
              </span>
            </div>

            <p className="text-xs text-cockpit-muted">
              Writes one scratch draft packet. It does not run a backtest,
              create a candidate, approve, promote, cross, or trade.
              {serviceOrigin ? (
                <>
                  {" "}
                  Target:{" "}
                  <span className="font-mono text-cockpit-text">
                    {serviceOrigin}
                    {AGENT_INBOX_UPSTREAM_PATH}
                  </span>
                </>
              ) : null}
            </p>
          </div>
        </form>
      </Card>

      {submission.state === "error" ? (
        <UnavailableState
          title={
            submission.unreachable
              ? "Intake service unreachable"
              : "Draft not created"
          }
          reason={submission.message}
        />
      ) : null}

      {submission.state === "success" ? (
        <DraftPacketView packet={submission.packet} />
      ) : null}
    </div>
  );
}
