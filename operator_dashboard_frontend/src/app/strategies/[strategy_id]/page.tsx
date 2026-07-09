import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { PlaceholderCard, UnavailableState } from "@/components/States";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

export default function StrategyDetailPage({
  params,
}: {
  params: { strategy_id: string };
}) {
  const id = decodeURIComponent(params.strategy_id);
  const items = fixtures.strategies().data.items ?? [];
  const strategy = items.find((s) => s.strategy_id === id);

  return (
    <>
      <PageHeader
        title={strategy?.title ?? id}
        breadcrumb={["Strategies", id]}
        description="Read-only strategy summary. Deep variant / WFO / robustness / artifact panels are later packages."
      />

      <Link
        href="/strategies"
        className="text-xs text-cockpit-accent hover:underline"
      >
        ← All strategies
      </Link>

      {strategy ? (
        <Card>
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <CardTitle>Summary</CardTitle>
            {strategy.status ? (
              <Badge tone={toneForStatus(strategy.status)}>
                {strategy.status}
              </Badge>
            ) : null}
            {strategy.not_executable ? (
              <Badge tone="warn">not executable</Badge>
            ) : null}
          </div>
          <div className="flex flex-col">
            <KeyValue label="Strategy ID" value={strategy.strategy_id ?? "—"} />
            <KeyValue label="Short name" value={strategy.short_name ?? "—"} />
            <KeyValue label="Source type" value={strategy.source_type ?? "—"} />
            <KeyValue
              label="Instrument family"
              value={strategy.instrument_family ?? "—"}
            />
            <KeyValue label="Market type" value={strategy.market_type ?? "—"} />
            <KeyValue
              label="Primary timeframe"
              value={strategy.primary_timeframe ?? "—"}
            />
            <KeyValue label="Direction" value={strategy.direction ?? "—"} />
            <KeyValue
              label="Free parameters"
              value={strategy.free_parameter_count ?? "n/a"}
            />
            <KeyValue
              label="Max free parameters"
              value={strategy.max_free_parameters ?? "—"}
            />
            <KeyValue
              label="Approval scope"
              value={strategy.approval_scope ?? "—"}
            />
            <KeyValue
              label="Not executable"
              value={String(strategy.not_executable ?? "—")}
            />
          </div>
        </Card>
      ) : (
        <UnavailableState
          title="Strategy not in fixture"
          reason={`No committed strategy summary for "${id}" is present in the shell fixtures. The live read-only API exposes GET /api/strategies/{id}; wiring it is deferred to a later panel package.`}
        />
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <PlaceholderCard title="Variants" />
        <PlaceholderCard title="Walk-forward (WFO)" />
        <PlaceholderCard title="Robustness" />
        <PlaceholderCard title="Artifacts" />
      </div>
    </>
  );
}
