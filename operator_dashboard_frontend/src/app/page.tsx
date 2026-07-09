import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, KeyValue, StatCard } from "@/components/ui";
import { CountBars, type CountRow } from "@/components/viz";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

export default function CommandCenterPage() {
  const envelope = fixtures.dashboardSummary();
  const summary = envelope.data;
  const counts = summary.counts ?? {};
  const queue = summary.queue_summary ?? {};
  const product = summary.product_run_summary ?? {};
  const paper = summary.paper_trading;
  const live = summary.live_trading;

  const queueRows: CountRow[] = Object.entries(queue.by_status ?? {}).map(
    ([label, count]) => ({ label, count, tone: toneForStatus(label) }),
  );

  return (
    <>
      <PageHeader
        title="Command Center"
        breadcrumb={["Operator Dashboard"]}
        description="Local-first read-only overview of research posture, population, and queue state. Presentation only."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <StatCard label="Result Populations" value={counts.result_populations ?? 0} />
        <StatCard label="Strategies" value={counts.strategies ?? 0} />
        <StatCard label="Registered Candidates" value={counts.registered_candidates ?? 0} />
        <StatCard label="Queue Runs" value={counts.queue_runs ?? 0} />
        <StatCard label="Product Runs" value={counts.product_runs ?? 0} />
        <StatCard
          label="Candidates Admitted"
          value={counts.candidates_admitted ?? 0}
          hint="No admission is implied by this shell"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <CardTitle>Queue by status</CardTitle>
            <Link
              href="/research/jobs"
              className="text-xs text-cockpit-accent hover:underline"
            >
              View jobs →
            </Link>
          </div>
          {queueRows.length > 0 ? (
            <CountBars rows={queueRows} />
          ) : (
            <p className="text-xs text-cockpit-muted">No queue snapshot.</p>
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge tone={queue.approval_needed_count ? "warn" : "neutral"}>
              approval needed: {queue.approval_needed_count ?? 0}
            </Badge>
            <Badge tone={queue.blocked_count ? "bad" : "neutral"}>
              blocked: {queue.blocked_count ?? 0}
            </Badge>
            <Badge tone={queue.failed_count ? "bad" : "neutral"}>
              failed: {queue.failed_count ?? 0}
            </Badge>
          </div>
        </Card>

        <Card>
          <CardTitle>Product runs</CardTitle>
          <div className="flex flex-col">
            <KeyValue label="Run count" value={product.run_count ?? 0} />
            <KeyValue
              label="Advisory packets ready"
              value={product.advisory_packet_ready ?? 0}
            />
            <KeyValue
              label="Blocked or failed"
              value={product.blocked_or_failed ?? 0}
            />
            <KeyValue
              label="Real runner runs"
              value={product.real_runner_runs ?? 0}
            />
          </div>
          <p className="mt-3 text-xs text-cockpit-muted">
            Advisory packets are review-routing only; nothing here is crossed,
            promoted, or marked ready.
          </p>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>Paper Trading</CardTitle>
          <div className="flex flex-col gap-2">
            <Badge tone={toneForStatus(paper?.status)}>
              {paper?.status ?? "unavailable"}
            </Badge>
            <p className="text-sm text-cockpit-muted">
              {paper?.reason ??
                "No authorized read-only paper telemetry snapshot exists."}
            </p>
            <p className="text-xs text-cockpit-muted">
              Capability built: {String(paper?.capability_built ?? false)}
            </p>
          </div>
        </Card>
        <Card>
          <CardTitle>Live Trading</CardTitle>
          <div className="flex flex-col gap-2">
            <Badge tone={toneForStatus(live?.status)}>
              {live?.status ?? "unavailable"}
            </Badge>
            <p className="text-sm text-cockpit-muted">
              {live?.reason ??
                "No authorized read-only live telemetry snapshot exists."}
            </p>
            <p className="text-xs text-cockpit-muted">
              Capability built: {String(live?.capability_built ?? false)}
            </p>
          </div>
        </Card>
      </div>

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
