import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, StatCard } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { ChartCard } from "@/components/charts/ChartCard";
import { ChartProvenanceNote } from "@/components/charts/ChartProvenanceNote";
import {
  CategoricalCountChart,
  type CategoryBar,
} from "@/components/charts/CategoricalCountChart";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";
import type { StrategySummary } from "@/lib/types";

/** Tally committed specs by one committed facet. Display-only aggregation. */
function facetBars(
  items: StrategySummary[],
  facet: keyof StrategySummary,
): CategoryBar[] {
  const tally = new Map<string, number>();
  for (const item of items) {
    const value = item[facet];
    if (typeof value !== "string" || value.length === 0) continue;
    tally.set(value, (tally.get(value) ?? 0) + 1);
  }
  return [...tally.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([label, count]) => ({ label, count, tone: "info" as const }));
}

export default function StrategiesPage() {
  const envelope = fixtures.strategies();
  const items = envelope.data.items ?? [];
  const notExecutable = items.filter((s) => s.not_executable).length;

  const timeframeBars = facetBars(items, "primary_timeframe");
  const directionBars = facetBars(items, "direction");

  return (
    <>
      <PageHeader
        title="Strategies"
        breadcrumb={["Strategies"]}
        description="Committed strategy-spec summaries. Strategy specs are planning artifacts and are not executable."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <StatCard label="Strategy Specs" value={envelope.data.count ?? items.length} />
        <StatCard
          label="Not Executable"
          value={notExecutable}
          hint="planning artifacts only"
        />
        <StatCard
          label="Executable"
          value={items.length - notExecutable}
          hint="none in this shell"
        />
      </div>

      {items.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <ChartCard
            title="Specs by primary timeframe"
            footer={
              <ChartProvenanceNote
                source="GET /api/strategies"
                fields={["items[].primary_timeframe"]}
                derived={["count per distinct value"]}
                drawn={items.length}
              />
            }
          >
            <CategoricalCountChart
              bars={timeframeBars}
              horizontal
              ariaLabel={`Bar chart of committed strategy specs across ${timeframeBars.length} primary timeframes`}
            />
          </ChartCard>
          <ChartCard
            title="Specs by direction"
            footer={
              <ChartProvenanceNote
                source="GET /api/strategies"
                fields={["items[].direction"]}
                derived={["count per distinct value"]}
                drawn={items.length}
                note="Strategy specs are planning artifacts and are not executable."
              />
            }
          >
            <CategoricalCountChart
              bars={directionBars}
              horizontal
              ariaLabel={`Bar chart of committed strategy specs across ${directionBars.length} directions`}
            />
          </ChartCard>
        </div>
      ) : null}

      <Card>
        <CardTitle>Strategy specs ({envelope.data.count ?? items.length})</CardTitle>
        {items.length === 0 ? (
          <EmptyState message="No committed strategy specs found." />
        ) : (
          <ul className="flex flex-col gap-2">
            {items.map((s) => (
              <li key={s.strategy_id}>
                <Link
                  href={`/strategies/${encodeURIComponent(s.strategy_id ?? "")}`}
                >
                  <div className="flex flex-col gap-2 rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2.5 transition-colors hover:border-cockpit-accent-dim">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="flex flex-col">
                        <span className="text-sm text-cockpit-heading">
                          {s.title ?? s.short_name ?? s.strategy_id}
                        </span>
                        <span className="font-mono text-xs text-cockpit-muted">
                          {s.strategy_id}
                          {s.short_name ? ` · ${s.short_name}` : ""}
                        </span>
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        {s.status ? (
                          <Badge tone={toneForStatus(s.status)}>{s.status}</Badge>
                        ) : null}
                        {s.not_executable ? (
                          <Badge tone="warn">not executable</Badge>
                        ) : null}
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      {s.source_type ? <Badge>{s.source_type}</Badge> : null}
                      {s.instrument_family ? (
                        <Badge>{s.instrument_family}</Badge>
                      ) : null}
                      {s.market_type ? <Badge>{s.market_type}</Badge> : null}
                      {s.primary_timeframe ? (
                        <Badge tone="info">{s.primary_timeframe}</Badge>
                      ) : null}
                      {s.direction ? <Badge>{s.direction}</Badge> : null}
                      <span className="text-cockpit-muted">
                        free params:{" "}
                        <span className="font-mono text-cockpit-text">
                          {s.free_parameter_count ?? "n/a"}
                        </span>
                        {typeof s.max_free_parameters === "number"
                          ? ` / max ${s.max_free_parameters}`
                          : ""}
                      </span>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
