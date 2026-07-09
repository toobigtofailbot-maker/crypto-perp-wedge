import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle } from "@/components/ui";
import { CountBars, type CountRow } from "@/components/viz";
import { EmptyState } from "@/components/States";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

interface QueueSummary {
  run_count?: number;
  by_status?: Record<string, number>;
  approval_needed_count?: number;
  blocked_count?: number;
  failed_count?: number;
  advisory_packet_ready_count?: number;
}

interface JobRun {
  pipeline_run_id?: string;
  request_id?: string;
  source_idea?: string;
  symbol?: string;
  timeframe?: string;
  requested_by?: string;
  status?: string;
  approval_needed?: {
    kind?: string;
    needed?: boolean;
    approval_scope?: string;
  } | null;
  blocked_reasons?: string[];
  notification_preview?: {
    dry_run_only?: boolean;
    notification_fired?: boolean;
    dispatch_enqueued?: boolean;
    preview_reason?: string;
  } | null;
}

export default function ResearchJobsPage() {
  const envelope = fixtures.researchJobs();
  const data = envelope.data as {
    summary?: QueueSummary;
    runs?: JobRun[];
    allowed_status_states?: string[];
  };
  const summary = data.summary ?? {};
  const runs = Array.isArray(data.runs) ? data.runs : [];

  const statusRows: CountRow[] = Object.entries(summary.by_status ?? {}).map(
    ([label, count]) => ({ label, count, tone: toneForStatus(label) }),
  );

  return (
    <>
      <PageHeader
        title="Research Jobs"
        breadcrumb={["Research", "Jobs"]}
        description="Read-only pipeline queue and run status. Approval and notification fields are visibility-only; this shell fires nothing."
      />

      <Card>
        <CardTitle>Queue summary ({summary.run_count ?? runs.length} runs)</CardTitle>
        {statusRows.length > 0 ? (
          <CountBars rows={statusRows} />
        ) : (
          <EmptyState message="No queue summary available." />
        )}
        <div className="mt-3 flex flex-wrap gap-2">
          <Badge tone={summary.approval_needed_count ? "warn" : "neutral"}>
            approval needed: {summary.approval_needed_count ?? 0}
          </Badge>
          <Badge tone={summary.blocked_count ? "bad" : "neutral"}>
            blocked: {summary.blocked_count ?? 0}
          </Badge>
          <Badge tone={summary.failed_count ? "bad" : "neutral"}>
            failed: {summary.failed_count ?? 0}
          </Badge>
          <Badge tone={summary.advisory_packet_ready_count ? "good" : "neutral"}>
            advisory ready: {summary.advisory_packet_ready_count ?? 0}
          </Badge>
        </div>
      </Card>

      <Card>
        <CardTitle>Runs ({runs.length})</CardTitle>
        {runs.length === 0 ? (
          <EmptyState message="No runs in the committed queue snapshot." />
        ) : (
          <ul className="flex flex-col gap-3">
            {runs.slice(0, 25).map((run, i) => (
              <li
                key={run.pipeline_run_id ?? i}
                className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-mono text-xs text-cockpit-heading">
                    {run.pipeline_run_id ?? `run-${i}`}
                  </span>
                  <Badge tone={toneForStatus(run.status)}>
                    {run.status ?? "unknown"}
                  </Badge>
                </div>
                {run.source_idea ? (
                  <p className="mt-1 text-sm text-cockpit-text">
                    {run.source_idea}
                  </p>
                ) : null}
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {run.symbol ? <Badge>{run.symbol}</Badge> : null}
                  {run.timeframe ? <Badge>{run.timeframe}</Badge> : null}
                  {run.requested_by ? (
                    <span className="text-cockpit-muted">
                      requested by {run.requested_by}
                    </span>
                  ) : null}
                </div>
                {run.approval_needed?.needed ? (
                  <p className="mt-2 text-xs text-cockpit-warn">
                    Awaiting {run.approval_needed.kind ?? "approval"} —{" "}
                    <span className="text-cockpit-muted">
                      scope: {run.approval_needed.approval_scope ?? "n/a"}
                    </span>{" "}
                    (visibility only; no approve control here)
                  </p>
                ) : null}
                {run.blocked_reasons && run.blocked_reasons.length > 0 ? (
                  <ul className="mt-2 flex flex-col gap-0.5 text-xs text-cockpit-bad">
                    {run.blocked_reasons.map((r) => (
                      <li key={r} className="font-mono">
                        blocked: {r}
                      </li>
                    ))}
                  </ul>
                ) : null}
                {run.notification_preview ? (
                  <p className="mt-2 text-[11px] text-cockpit-muted">
                    Notification preview: dry-run only ·{" "}
                    fired={String(run.notification_preview.notification_fired ?? false)}{" "}
                    · enqueued={String(run.notification_preview.dispatch_enqueued ?? false)}
                    {run.notification_preview.preview_reason
                      ? ` · reason: ${run.notification_preview.preview_reason}`
                      : ""}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        <p className="mt-3 text-xs text-cockpit-muted">
          This surface shows status only. Approvals, retries, dispatch, and
          notification firing are not wired and have no controls here.
        </p>
      </Card>

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
