import { PageHeader } from "@/components/PageHeader";
import { Badge, Card, CardTitle } from "@/components/ui";
import { fixtures } from "@/lib/fixtures";

export default function PaperTradingPage() {
  const summary = fixtures.dashboardSummary().data;
  const paper = summary.paper_trading;

  return (
    <>
      <PageHeader
        title="Paper Trading"
        breadcrumb={["Paper"]}
        description="Honest placeholder. No paper telemetry, no positions, no controls."
      />
      <Card className="border-cockpit-warn/40">
        <CardTitle>Status</CardTitle>
        <div className="flex flex-col gap-3">
          <Badge tone="warn">{paper?.status ?? "unavailable"}</Badge>
          <p className="text-sm text-cockpit-muted">
            {paper?.reason ??
              "No authorized read-only paper telemetry snapshot exists for this package."}
          </p>
          <ul className="flex list-disc flex-col gap-1 pl-5 text-xs text-cockpit-muted">
            <li>Capability built: {String(paper?.capability_built ?? false)}</li>
            <li>No PnL, exposure, or position data is shown or fabricated.</li>
            <li>No start / stop / order / crossing controls exist.</li>
            <li>
              Paper telemetry surfaces require a later, separately authorized
              read-only snapshot package and remain GO-gated.
            </li>
          </ul>
        </div>
      </Card>
    </>
  );
}
