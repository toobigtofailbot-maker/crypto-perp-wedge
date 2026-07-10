"use client";

/**
 * Append-only human review trail for one opened scratch draft
 * (WP-INBOX-DRAFT-REVIEW-STATE-03B over the 03A review-event endpoints).
 *
 * This is the one place in the Agent Inbox besides intake that writes: it appends
 * exactly one bounded review annotation to a draft's trail via the same-origin
 * passthrough. It has no other network write. Nothing here approves, promotes,
 * ranks, canonicalizes, admits to a queue, creates a candidate, or authorizes
 * research/paper/live/runtime execution — the append is review material only.
 *
 * The four states mean exactly what the service says they mean, no more:
 *   reviewed              — a human reviewed the draft.
 *   rejected              — a human rejected it as not worth further intake work.
 *   needs_clarification   — a human requests clarification before further consideration.
 *   flagged_for_canonicalization — a human thinks it *may* merit a later,
 *       separate, Karl-gated canonicalization review. It is an annotation only:
 *       it creates and approves no Strategy Spec, queues no research, and
 *       authorizes no execution.
 *
 * Nothing is persisted client-side: no localStorage, sessionStorage, cookie, or
 * IndexedDB is written, so a reload simply re-reads the trail from the service.
 * When the service is unconfigured or unreachable this says so plainly and never
 * synthesizes a trail; an empty trail renders an honest empty state.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { Badge, Card, CardTitle } from "@/components/ui";
import { EmptyState, LoadingState, UnavailableState } from "@/components/States";
import { FlagGrid } from "@/components/explorer/primitives";
import {
  AgentInboxRejectedError,
  AgentInboxUnavailableError,
  REVIEW_FIELD_LIMITS,
  REVIEW_STATES,
  appendDraftReviewEvent,
  getDraftReviewEvents,
  type AgentInboxReviewEvent,
  type AgentInboxReviewEventRequest,
  type AgentInboxReviewTrailEnvelope,
  type ReviewState,
} from "@/lib/agentInboxClient";

/** Human-readable, non-authoritative gloss for each state. Matches the service. */
const STATE_MEANING: Record<ReviewState, string> = {
  reviewed: "A human reviewed this scratch draft.",
  rejected: "A human rejected it as not worth further intake work.",
  needs_clarification:
    "A human requests clarification before further consideration.",
  flagged_for_canonicalization:
    "A human thinks it may merit a later, separate, Karl-gated canonicalization review. Annotation only.",
};

/** Badge tone per state. None of these tones implies approval or readiness. */
const STATE_TONE: Record<ReviewState, "neutral" | "warn" | "info" | "bad"> = {
  reviewed: "info",
  rejected: "bad",
  needs_clarification: "warn",
  flagged_for_canonicalization: "warn",
};

type TrailState =
  | { kind: "loading" }
  | { kind: "loaded"; envelope: AgentInboxReviewTrailEnvelope }
  | { kind: "unavailable"; message: string }
  | { kind: "error"; message: string };

type AppendState =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "rejected"; message: string }
  | { kind: "unavailable"; message: string };

function messageFromError(error: unknown): {
  unavailable: boolean;
  message: string;
} {
  if (error instanceof AgentInboxUnavailableError) {
    return { unavailable: true, message: error.message };
  }
  if (error instanceof AgentInboxRejectedError) {
    return {
      unavailable: false,
      message: `The intake service answered HTTP ${error.status}: ${error.message}`,
    };
  }
  return {
    unavailable: false,
    message:
      error instanceof Error
        ? error.message
        : "The intake service returned an unreadable response.",
  };
}

/** The annotation-only warning that must sit beside `flagged_for_canonicalization`. */
function CanonicalizationNotice() {
  return (
    <p className="rounded-md border border-cockpit-warn/40 bg-cockpit-warn/10 px-3 py-2 text-xs text-cockpit-warn">
      <span className="font-semibold">Flagged for canonicalization</span> is only
      a review annotation. It does not create or approve a Strategy Spec, does not
      queue research, and does not authorize execution. Canonicalization remains
      Karl-gated and separate.
    </p>
  );
}

/** One appended event, rendered verbatim. Read-only; no control edits or deletes it. */
function ReviewEventRow({ event }: { event: AgentInboxReviewEvent }) {
  const knownState = (REVIEW_STATES as readonly string[]).includes(
    event.review_state,
  )
    ? (event.review_state as ReviewState)
    : null;

  return (
    <li className="flex flex-col gap-2 rounded-md border border-cockpit-border bg-cockpit-panel-2 px-3 py-2.5">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="neutral">#{event.append_index}</Badge>
          <Badge tone={knownState ? STATE_TONE[knownState] : "neutral"}>
            {event.review_state}
          </Badge>
        </div>
        <span className="break-all font-mono text-xs text-cockpit-muted">
          {event.event_id}
        </span>
      </div>

      {knownState ? (
        <p className="text-xs text-cockpit-muted">{STATE_MEANING[knownState]}</p>
      ) : null}

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-cockpit-muted">
        <span>
          reviewer{" "}
          <span className="font-mono text-cockpit-text">
            {event.reviewer_label}
          </span>
        </span>
        <span>
          at{" "}
          <span className="font-mono text-cockpit-text">
            {event.timestamp_utc}
          </span>
        </span>
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          rationale
        </span>
        <p className="whitespace-pre-wrap text-sm text-cockpit-text">
          {event.rationale}
        </p>
      </div>

      {event.clarification_request ? (
        <div className="flex flex-col gap-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
            clarification request
          </span>
          <p className="whitespace-pre-wrap text-sm text-cockpit-text">
            {event.clarification_request}
          </p>
        </div>
      ) : null}

      {knownState === "flagged_for_canonicalization" ? (
        <CanonicalizationNotice />
      ) : null}

      <details className="text-xs text-cockpit-muted">
        <summary className="cursor-pointer select-none">
          Non-authority flags
        </summary>
        <div className="mt-2">
          <FlagGrid flags={event.non_authority_flags ?? {}} />
        </div>
      </details>
    </li>
  );
}

/** The bounded append form. Its only action posts one review annotation. */
function AppendForm({
  draftId,
  onAppended,
}: {
  draftId: string;
  onAppended: (envelope: AgentInboxReviewTrailEnvelope) => void;
}) {
  const [reviewState, setReviewState] = useState<ReviewState>("reviewed");
  const [reviewerLabel, setReviewerLabel] = useState("");
  const [rationale, setRationale] = useState("");
  const [clarification, setClarification] = useState("");
  const [append, setAppend] = useState<AppendState>({ kind: "idle" });

  const submitting = append.kind === "submitting";
  const canSubmit =
    !submitting && reviewerLabel.trim().length > 0 && rationale.trim().length > 0;

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!canSubmit) return;
      setAppend({ kind: "submitting" });

      const request: AgentInboxReviewEventRequest = {
        review_state: reviewState,
        reviewer_label: reviewerLabel.trim(),
        rationale: rationale.trim(),
      };
      const trimmedClarification = clarification.trim();
      if (trimmedClarification.length > 0) {
        request.clarification_request = trimmedClarification;
      }

      try {
        const result = await appendDraftReviewEvent(draftId, request);
        // Reset the input fields but keep the chosen state for a quick follow-up.
        setReviewerLabel("");
        setRationale("");
        setClarification("");
        setAppend({ kind: "idle" });
        onAppended(result.review_trail);
      } catch (error) {
        const { unavailable, message } = messageFromError(error);
        setAppend({ kind: unavailable ? "unavailable" : "rejected", message });
      }
    },
    [
      canSubmit,
      clarification,
      draftId,
      onAppended,
      rationale,
      reviewState,
      reviewerLabel,
    ],
  );

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex flex-col gap-1">
        <label
          htmlFor="review-state"
          className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted"
        >
          Review state
        </label>
        <select
          id="review-state"
          value={reviewState}
          onChange={(e) => setReviewState(e.target.value as ReviewState)}
          disabled={submitting}
          className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2 text-sm text-cockpit-text disabled:opacity-40"
        >
          {REVIEW_STATES.map((state) => (
            <option key={state} value={state}>
              {state}
            </option>
          ))}
        </select>
        <p className="text-xs text-cockpit-muted">
          {STATE_MEANING[reviewState]}
        </p>
      </div>

      {reviewState === "flagged_for_canonicalization" ? (
        <CanonicalizationNotice />
      ) : null}

      <div className="flex flex-col gap-1">
        <label
          htmlFor="reviewer-label"
          className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted"
        >
          Reviewer label
        </label>
        <input
          id="reviewer-label"
          type="text"
          value={reviewerLabel}
          onChange={(e) => setReviewerLabel(e.target.value)}
          maxLength={REVIEW_FIELD_LIMITS.reviewer_label}
          disabled={submitting}
          placeholder="Who is annotating this scratch draft"
          className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2 text-sm text-cockpit-text disabled:opacity-40"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label
          htmlFor="review-rationale"
          className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted"
        >
          Rationale
        </label>
        <textarea
          id="review-rationale"
          value={rationale}
          onChange={(e) => setRationale(e.target.value)}
          maxLength={REVIEW_FIELD_LIMITS.rationale}
          disabled={submitting}
          rows={3}
          placeholder="Why this review state, in the reviewer's own words"
          className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2 text-sm text-cockpit-text disabled:opacity-40"
        />
        <span className="self-end text-xs text-cockpit-muted">
          {rationale.length}/{REVIEW_FIELD_LIMITS.rationale}
        </span>
      </div>

      <div className="flex flex-col gap-1">
        <label
          htmlFor="review-clarification"
          className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted"
        >
          Clarification request <span className="normal-case">(optional)</span>
        </label>
        <textarea
          id="review-clarification"
          value={clarification}
          onChange={(e) => setClarification(e.target.value)}
          maxLength={REVIEW_FIELD_LIMITS.clarification_request}
          disabled={submitting}
          rows={2}
          placeholder="What the submitter would need to clarify, if anything"
          className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2 text-sm text-cockpit-text disabled:opacity-40"
        />
        <span className="self-end text-xs text-cockpit-muted">
          {clarification.length}/{REVIEW_FIELD_LIMITS.clarification_request}
        </span>
      </div>

      {append.kind === "rejected" ? (
        <p className="rounded-md border border-cockpit-bad/40 bg-cockpit-bad/10 px-3 py-2 text-xs text-cockpit-bad">
          {append.message}
        </p>
      ) : null}
      {append.kind === "unavailable" ? (
        <p className="rounded-md border border-cockpit-warn/40 bg-cockpit-warn/10 px-3 py-2 text-xs text-cockpit-warn">
          {append.message}
        </p>
      ) : null}

      <div className="flex flex-wrap items-center justify-between gap-2">
        <button
          type="submit"
          disabled={!canSubmit}
          className="rounded border border-cockpit-accent bg-cockpit-accent/10 px-3 py-2 text-sm font-medium text-cockpit-accent hover:bg-cockpit-accent/20 disabled:opacity-40"
        >
          {submitting ? "Appending…" : "Append scratch review event"}
        </button>
        <span className="text-xs text-cockpit-muted">
          Appends one annotation. Approves, promotes, canonicalizes, queues, and
          runs nothing.
        </span>
      </div>
    </form>
  );
}

export function ReviewTrail({ draftId }: { draftId: string }) {
  const [trail, setTrail] = useState<TrailState>({ kind: "loading" });

  const loadTrail = useCallback(async () => {
    setTrail({ kind: "loading" });
    try {
      const envelope = await getDraftReviewEvents(draftId);
      setTrail({ kind: "loaded", envelope });
    } catch (error) {
      const { unavailable, message } = messageFromError(error);
      setTrail({ kind: unavailable ? "unavailable" : "error", message });
    }
  }, [draftId]);

  useEffect(() => {
    void loadTrail();
  }, [loadTrail]);

  const onAppended = useCallback((envelope: AgentInboxReviewTrailEnvelope) => {
    setTrail({ kind: "loaded", envelope });
  }, []);

  const events = useMemo(
    () =>
      trail.kind === "loaded"
        ? [...trail.envelope.review_events].sort(
            (a, b) => a.append_index - b.append_index,
          )
        : [],
    [trail],
  );

  return (
    <Card>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <CardTitle>Review trail</CardTitle>
        <div className="flex flex-wrap items-center gap-2">
          {trail.kind === "loaded" ? (
            <Badge tone="neutral">{trail.envelope.count} events</Badge>
          ) : null}
          <Badge tone="warn">scratch only</Badge>
          <button
            type="button"
            onClick={() => void loadTrail()}
            disabled={trail.kind === "loading"}
            className="rounded border border-cockpit-border px-3 py-1 text-xs text-cockpit-muted hover:text-cockpit-text disabled:opacity-40"
          >
            {trail.kind === "loading" ? "Refreshing…" : "Refresh (read-only)"}
          </button>
        </div>
      </div>

      <p className="mb-3 text-xs text-cockpit-muted">
        Append-only human annotations over this scratch draft, read from the
        isolated service. Review state is not approval, ranking, readiness,
        canonicalization, queue admission, or execution.
      </p>

      {trail.kind === "loading" ? (
        <LoadingState message="Reading the review trail from the isolated service…" />
      ) : null}

      {trail.kind === "unavailable" ? (
        <UnavailableState title="Review trail unavailable" reason={trail.message} />
      ) : null}

      {trail.kind === "error" ? (
        <UnavailableState
          title="Review trail could not be read"
          reason={trail.message}
        />
      ) : null}

      {trail.kind === "loaded" && events.length === 0 ? (
        <EmptyState message="No review events yet. This scratch draft has not been annotated. Append the first review event below." />
      ) : null}

      {trail.kind === "loaded" && events.length > 0 ? (
        <>
          <ul className="flex flex-col gap-2">
            {events.map((event) => (
              <ReviewEventRow key={event.event_id} event={event} />
            ))}
          </ul>
          <p className="mt-3 border-t border-cockpit-border/50 pt-2 text-xs text-cockpit-muted">
            Read from{" "}
            <span className="font-mono text-cockpit-text">
              {trail.envelope.storage_source}
            </span>
            . Append-only; events are never reordered, edited, or deleted.
            canonical_authority ={" "}
            <span className="font-mono text-cockpit-text">
              {String(trail.envelope.canonical_authority)}
            </span>
            .
          </p>
        </>
      ) : null}

      <div className="mt-4 border-t border-cockpit-border/50 pt-4">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Append a review event
        </h4>
        <AppendForm draftId={draftId} onAppended={onAppended} />
      </div>
    </Card>
  );
}
