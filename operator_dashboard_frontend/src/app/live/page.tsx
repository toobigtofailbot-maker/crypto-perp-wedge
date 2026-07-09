import { PageHeader } from "@/components/PageHeader";
import { Badge, Card, CardTitle } from "@/components/ui";
import { fixtures } from "@/lib/fixtures";

export default function LiveTradingPage() {
  const summary = fixtures.dashboardSummary().data;
  const live = summary.live_trading;

  return (
    <>
      <PageHeader
        title="Live Trading"
        breadcrumb={["Live"]}
        description="Honest placeholder. No live telemetry, no positions, no controls."
      />
      <Card className="border-cockpit-bad/40">
        <CardTitle>Status</CardTitle>
        <div className="flex flex-col gap-3">
          <Badge tone="bad">{live?.status ?? "unavailable"}</Badge>
          <p className="text-sm text-cockpit-muted">
            {live?.reason ??
              "No authorized read-only live telemetry snapshot exists for this package."}
          </p>
          <ul className="flex list-disc flex-col gap-1 pl-5 text-xs text-cockpit-muted">
            <li>Capability built: {String(live?.capability_built ?? false)}</li>
            <li>No PnL, exposure, or position data is shown or fabricated.</li>
            <li>
              No start / stop / order / crossing / promotion controls exist.
            </li>
            <li>
              Live trading is not built and remains GO-gated. This page only
              states that boundary.
            </li>
          </ul>
        </div>
      </Card>
    </>
  );
}
