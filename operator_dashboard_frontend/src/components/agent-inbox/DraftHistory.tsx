"use client";

/**
 * Read-only history of scratch draft packets already written by the isolated
 * Agent Inbox intake service (WP-INBOX-DRAFT-HISTORY-02B over the 02A
 * `GET /api/agent/drafts` and `GET /api/agent/drafts/{draft_id}` endpoints).
 *
 * Everything here is a GET. The one control that hits the network — "Refresh" —
 * re-reads the list and submits nothing; it cannot create, edit, delete,
 * approve, review, promote, run, or queue a draft, and neither can opening one.
 * Opening a draft fetches the stored packet whole and renders it verbatim via
 * `DraftPacketView`. Nothing is persisted client-side: no localStorage,
 * sessionStorage, or cookie is written, so a reload simply re-reads the service.
 *
 * When the service is unconfigured or unreachable this says so plainly and never
 * synthesizes drafts; an empty history renders an honest empty state, not a
 * simulated one. The list is orientation only — not evidence, approval, ranking,
 * readiness, recommendation, or execution input.
 */

import { useCallback, useEffect, useState } from "react";
import { Badge, Card, CardTitle } from "@/components/ui";
import { EmptyState, LoadingState, UnavailableState } from "@/components/States";
import { DraftPacketView } from "@/components/agent-inbox/DraftPacketView";
import {
  AgentInboxRejectedError,
  AgentInboxUnavailableError,
  getIntakeDraft,
  getIntakeDrafts,
  type AgentInboxDraftListEnvelope,
  type AgentInboxDraftPacket,
  type AgentInboxDraftSummary,
} from "@/lib/agentInboxClient";

type ListState =
  | { kind: "loading" }
  | { kind: "loaded"; envelope: AgentInboxDraftListEnvelope }
  | { kind: "unavailable"; message: string }
  | { kind: "error"; message: string };

type DetailState =
  | { kind: "closed" }
  | { kind: "loading"; draftId: string }
  | { kind: "loaded"; packet: AgentInboxDraftPacket }
  | { kind: "unavailable"; draftId: string; message: string }
  | { kind: "error"; draftId: string; message: string };

function orDash(value: string | null | undefined): string {
  return value === null || value === undefined || value === "" ? "—" : value;
}

/** One row of the list. A button, because opening a draft is the only action. */
function DraftRow({
  draft,
  selected,
  onOpen,
}: {
  draft: AgentInboxDraftSummary;
  selected: boolean;
  onOpen: (draftId: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onOpen(draft.draft_id)}
      aria-pressed={selected}
      className={`flex w-full flex-col gap-2 rounded-md border px-3 py-2.5 text-left transition-colors ${
        selected
          ? "border-cockpit-accent bg-cockpit-accent/10"
          : "border-cockpit-border bg-cockpit-panel-2 hover:border-cockpit-accent/60"
      }`}
    >
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <span className="text-sm font-medium text-cockpit-text">
          {orDash(draft.title)}
        </span>
        <span className="break-all font-mono text-xs text-cockpit-muted">
          {draft.draft_id}
        </span>
      </div>

      {draft.hypothesis_preview ? (
        <p className="text-xs text-cockpit-muted">{draft.hypothesis_preview}</p>
      ) : null}

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-cockpit-muted">
        <span>
          created{" "}
          <span className="font-mono text-cockpit-text">{draft.created_at}</span>
        </span>
        <span>
          submitter{" "}
          <span className="font-mono text-cockpit-text">
            {orDash(draft.submitter_label)}
          </span>
        </span>
        <span>
          market{" "}
          <span className="font-mono text-cockpit-text">
            {orDash(draft.market_hint)}
          </span>
        </span>
        <span>
          timeframe{" "}
          <span className="font-mono text-cockpit-text">
            {orDash(draft.timeframe_hint)}
          </span>
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        <Badge tone={draft.blocker_count > 0 ? "bad" : "neutral"}>
          {draft.blocker_count} blockers
        </Badge>
        <Badge tone={draft.warning_count > 0 ? "warn" : "neutral"}>
          {draft.warning_count} warnings
        </Badge>
        <Badge tone="neutral">{draft.open_question_count} open questions</Badge>
        <Badge tone={draft.fabricated ? "bad" : "neutral"}>
          fabricated: {String(draft.fabricated)}
        </Badge>
        {draft.non_authority.scratch_only ? (
          <Badge tone="warn">scratch only</Badge>
        ) : null}
        {draft.non_authority.noncanonical ? (
          <Badge tone="warn">noncanonical</Badge>
        ) : null}
      </div>
    </button>
  );
}

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

export function DraftHistory({
  serviceConfigured,
}: {
  serviceConfigured: boolean;
}) {
  const [list, setList] = useState<ListState>({ kind: "loading" });
  const [detail, setDetail] = useState<DetailState>({ kind: "closed" });

  const loadList = useCallback(async () => {
    setList({ kind: "loading" });
    try {
      const envelope = await getIntakeDrafts();
      setList({ kind: "loaded", envelope });
    } catch (error) {
      const { unavailable, message } = messageFromError(error);
      setList({ kind: unavailable ? "unavailable" : "error", message });
    }
  }, []);

  const openDraft = useCallback(async (draftId: string) => {
    setDetail({ kind: "loading", draftId });
    try {
      const packet = await getIntakeDraft(draftId);
      setDetail({ kind: "loaded", packet });
    } catch (error) {
      const { unavailable, message } = messageFromError(error);
      setDetail(
        unavailable
          ? { kind: "unavailable", draftId, message }
          : { kind: "error", draftId, message },
      );
    }
  }, []);

  useEffect(() => {
    if (!serviceConfigured) return;
    void loadList();
  }, [serviceConfigured, loadList]);

  const selectedDraftId =
    detail.kind === "loading"
      ? detail.draftId
      : detail.kind === "loaded"
        ? detail.packet.draft_id
        : detail.kind === "unavailable" || detail.kind === "error"
          ? detail.draftId
          : null;

  if (!serviceConfigured) {
    return (
      <div className="flex flex-col gap-4">
        <SectionHeading />
        <UnavailableState
          title="Draft history not configured"
          reason="AGENT_INBOX_SERVICE_ORIGIN is not set, so this dashboard has no origin for the isolated Agent Inbox intake service. No history can be read, and none is simulated."
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <SectionHeading
        onRefresh={() => void loadList()}
        refreshing={list.kind === "loading"}
      />

      <Card>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <CardTitle>Submitted scratch drafts</CardTitle>
          {list.kind === "loaded" ? (
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="neutral">{list.envelope.count} drafts</Badge>
              {list.envelope.scratch_only ? (
                <Badge tone="warn">scratch only</Badge>
              ) : null}
            </div>
          ) : null}
        </div>

        {list.kind === "loading" ? (
          <LoadingState message="Reading draft history from the isolated service…" />
        ) : null}

        {list.kind === "unavailable" ? (
          <UnavailableState title="Draft history unavailable" reason={list.message} />
        ) : null}

        {list.kind === "error" ? (
          <UnavailableState title="Draft history could not be read" reason={list.message} />
        ) : null}

        {list.kind === "loaded" && list.envelope.drafts.length === 0 ? (
          <EmptyState message="No scratch drafts have been submitted yet. Submit an idea above, then refresh to see it here." />
        ) : null}

        {list.kind === "loaded" && list.envelope.drafts.length > 0 ? (
          <>
            <div className="flex flex-col gap-2">
              {list.envelope.drafts.map((draft) => (
                <DraftRow
                  key={draft.draft_id}
                  draft={draft}
                  selected={draft.draft_id === selectedDraftId}
                  onOpen={openDraft}
                />
              ))}
            </div>
            <p className="mt-3 border-t border-cockpit-border/50 pt-2 text-xs text-cockpit-muted">
              Read from{" "}
              <span className="font-mono text-cockpit-text">
                {list.envelope.storage_source}
              </span>
              . This list is orientation only — not evidence, approval, ranking,
              readiness, recommendation, or execution input.
            </p>
          </>
        ) : null}
      </Card>

      {detail.kind !== "closed" ? (
        <DraftDetail detail={detail} onClose={() => setDetail({ kind: "closed" })} />
      ) : null}
    </div>
  );
}

function SectionHeading({
  onRefresh,
  refreshing = false,
}: {
  onRefresh?: () => void;
  refreshing?: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2">
      <div className="flex flex-col gap-1">
        <h2 className="text-sm font-semibold text-cockpit-heading">
          Draft history
        </h2>
        <p className="text-xs text-cockpit-muted">
          Previously submitted scratch draft packets, read from the isolated
          service. Read-only; human review decides everything after.
        </p>
      </div>
      {onRefresh ? (
        <button
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
          className="rounded border border-cockpit-border px-3 py-1.5 text-sm text-cockpit-muted hover:text-cockpit-text disabled:opacity-40"
        >
          {refreshing ? "Refreshing…" : "Refresh history (read-only)"}
        </button>
      ) : null}
    </div>
  );
}

function DraftDetail({
  detail,
  onClose,
}: {
  detail: Exclude<DetailState, { kind: "closed" }>;
  onClose: () => void;
}) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-cockpit-heading">
          Draft detail{" "}
          <span className="font-mono text-xs text-cockpit-muted">
            {detail.kind === "loaded" ? detail.packet.draft_id : detail.draftId}
          </span>
        </h3>
        <button
          type="button"
          onClick={onClose}
          className="rounded border border-cockpit-border px-3 py-1.5 text-sm text-cockpit-muted hover:text-cockpit-text"
        >
          Close detail
        </button>
      </div>

      {detail.kind === "loading" ? (
        <LoadingState message="Reading the stored packet from the isolated service…" />
      ) : null}

      {detail.kind === "unavailable" ? (
        <UnavailableState title="Draft unavailable" reason={detail.message} />
      ) : null}

      {detail.kind === "error" ? (
        <UnavailableState title="Draft could not be read" reason={detail.message} />
      ) : null}

      {detail.kind === "loaded" ? (
        <DraftPacketView packet={detail.packet} />
      ) : null}
    </div>
  );
}
