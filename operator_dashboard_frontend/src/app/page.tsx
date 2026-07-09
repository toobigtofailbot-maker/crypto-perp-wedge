import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle, StatCard } from "@/components/ui";
import { fixtures } from "@/lib/fixtures";

export default function CommandCenterPage() {
  const envelope = fixtures.dashboardSummary();
  const summary = envelope.data;
  const counts = summary.counts ?? {};
  const paper = summary.paper_trading;
  const live = summary.live_trading;

  return (
    <>
      <PageHeader
        title="Command Center"
        breadcrumb={["Operator Dashboard"]}
        description="Local-first read-only overview of research posture and counts. Presentation only."
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
          <CardTitle>Paper Trading</CardTitle>
          <div className="flex flex-col gap-2">
            <Badge tone="warn">{paper?.status ?? "unavailable"}</Badge>
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
            <Badge tone="warn">{live?.status ?? "unavailable"}</Badge>
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

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
