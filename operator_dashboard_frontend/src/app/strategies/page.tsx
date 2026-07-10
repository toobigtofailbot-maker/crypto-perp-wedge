/**
 * Strategy index — the entry point into the Strategy Explorer.
 *
 * Helps an operator pick a spec to open by showing, per spec, what evidence
 * exists for it. The facet summaries are static tallies, not filters: this page
 * holds no state and offers no control.
 */
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
import { evidenceForStrategy } from "@/lib/explorer";
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

/** A static tally, rendered as text. Not a filter — nothing here is clickable. */
function FacetSummary({
  label,
  bars,
}: {
  label: string;
  bars: CategoryBar[];
}) {
  return (
    <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-xs">
      <span className="uppercase tracking-wider text-cockpit-muted">
        {label}
      </span>
      {bars.length === 0 ? (
        <span className="text-cockpit-muted">—</span>
      ) : (
        bars.map((bar) => (
          <span
            key={bar.label}
            className="inline-flex items-center gap-1 rounded border border-cockpit-border bg-cockpit-panel-2 px-1.5 py-0.5"
          >
            <span className="text-cockpit-text">{bar.label}</span>
            <span className="font-mono text-cockpit-muted">{bar.count}</span>
          </span>
        ))
      )}
    </div>
  );
}

export default function StrategiesPage() {
  const envelope = fixtures.strategies();
  const items = envelope.data.items ?? [];
  const details = fixtures.resultPopulationDetails();

  const notExecutable = items.filter((s) => s.not_executable).length;

  const evidence = new Map(
    items.map((s) => [
      s.strategy_id ?? "",
      evidenceForStrategy(details, s.strategy_id ?? ""),
    ]),
  );
  const withEvidence = [...evidence.values()].filter(
    (e) => e.population_count > 0,
  ).length;
  const totalVariantRows = [...evidence.values()].reduce(
    (total, e) => total + e.variant_row_count,
    0,
  );

  const timeframeBars = facetBars(items, "primary_timeframe");
  const directionBars = facetBars(items, "direction");
  const statusBars = facetBars(items, "status");
  const sourceBars = facetBars(items, "source_type");

  return (
    <>
      <PageHeader
        title="Strategies"
        breadcrumb={["Strategies"]}
        description="Committed strategy-spec summaries. Open one to inspect its declared logic, its linked evidence, and how that evidence behaved. Strategy specs are planning artifacts and are not executable."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard
          label="Strategy Specs"
          value={envelope.data.count ?? items.length}
        />
        <StatCard
          label="Not Executable"
          value={notExecutable}
          hint="planning artifacts only"
        />
        <StatCard
          label="With Linked Evidence"
          value={`${withEvidence} / ${items.length}`}
          hint="≥1 committed result population"
        />
        <StatCard
          label="Committed Variant Rows"
          value={totalVariantRows}
          hint="across all linked populations"
        />
      </div>

      <Card>
        <CardTitle>Static tallies</CardTitle>
        <div className="flex flex-col gap-2">
          <FacetSummary label="status" bars={statusBars} />
          <FacetSummary label="source type" bars={sourceBars} />
          <FacetSummary label="timeframe" bars={timeframeBars} />
          <FacetSummary label="direction" bars={directionBars} />
        </div>
        <p className="mt-3 text-xs text-cockpit-muted">
          These are counts, not filters. This surface holds no state and offers
          no control.
        </p>
      </Card>

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
            {items.map((s) => {
              const found = evidence.get(s.strategy_id ?? "");
              const populations = found?.population_count ?? 0;
              const rows = found?.variant_row_count ?? 0;
              return (
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
                          max free params:{" "}
                          <span className="font-mono text-cockpit-text">
                            {s.max_free_parameters ?? "—"}
                          </span>
                        </span>
                      </div>

                      <div className="flex flex-wrap items-center gap-2 border-t border-cockpit-border/50 pt-2 text-xs">
                        <span className="uppercase tracking-wider text-cockpit-muted">
                          evidence
                        </span>
                        {populations > 0 ? (
                          <>
                            <Badge tone="good">
                              {populations} result population
                              {populations === 1 ? "" : "s"}
                            </Badge>
                            <Badge tone="neutral">{rows} variant rows</Badge>
                          </>
                        ) : (
                          <Badge tone="warn">no linked result population</Badge>
                        )}
                        {s.path ? (
                          <span className="font-mono text-cockpit-muted">
                            {s.path}
                          </span>
                        ) : null}
                      </div>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
        <p className="mt-3 text-xs text-cockpit-muted">
          Evidence counts are derived from{" "}
          <span className="font-mono text-cockpit-text">
            GET /api/research/result-populations/{"{id}"}
          </span>{" "}
          by matching{" "}
          <span className="font-mono text-cockpit-text">
            parent_strategy_spec_id
          </span>
          . An evidence badge counts artifacts; it is not a quality, readiness,
          or approval signal, and no spec is ranked above another.
        </p>
      </Card>

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
