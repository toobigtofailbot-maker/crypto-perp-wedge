import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, StatCard } from "@/components/ui";
import { StackedBar, type StackSegment } from "@/components/viz";
import { EmptyState } from "@/components/States";
import { ChartCard } from "@/components/charts/ChartCard";
import { ChartProvenanceNote } from "@/components/charts/ChartProvenanceNote";
import { UnavailableChartState } from "@/components/charts/UnavailableChartState";
import { OutcomeDistributionChart } from "@/components/charts/OutcomeDistributionChart";
import {
  DrawdownDistributionChart,
  ReturnDistributionChart,
} from "@/components/charts/MetricHistogramChart";
import { DrawdownVsReturnScatter } from "@/components/charts/DrawdownVsReturnScatter";
import { toneForStatus, OUTCOME_META, OUTCOME_TONE } from "@/lib/status";
import {
  collectVariantPoints,
  pairMetrics,
  sampleMetric,
} from "@/lib/chartData";
import { fixtures } from "@/lib/fixtures";
import type { ResultPopulationSummary } from "@/lib/types";

function outcomeSegments(
  counts: Record<string, number | boolean> | undefined,
): StackSegment[] {
  if (!counts) return [];
  return Object.entries(counts)
    .filter(([k, v]) => !OUTCOME_META.has(k) && typeof v === "number")
    .map(([label, count]) => ({
      label,
      count: count as number,
      tone: OUTCOME_TONE[label] ?? "neutral",
    }));
}

const DETAIL_ENDPOINT = "GET /api/research/result-populations/{id}";

export default function ResultPopulationsPage() {
  const envelope = fixtures.resultPopulations();
  const items: ResultPopulationSummary[] = envelope.data.items ?? [];

  const totalCommitted = items.reduce(
    (s, rp) => s + (rp.committed_denominator ?? 0),
    0,
  );
  const totalRows = items.reduce((s, rp) => s + (rp.result_row_count ?? 0), 0);

  // Charted from the committed outcome_counts block on the list endpoint.
  const populations = items.map((rp) => ({
    id: rp.result_population_id ?? "—",
    counts: Object.fromEntries(
      outcomeSegments(rp.outcome_counts).map((s) => [s.label, s.count]),
    ),
  }));

  // Charted from the per-variant metrics block on the detail endpoint. Every
  // value below is a committed number read verbatim; nothing is simulated.
  const points = collectVariantPoints(fixtures.resultPopulationDetails());
  const returns = sampleMetric(points, "return_pct");
  const drawdowns = sampleMetric(points, "drawdown");
  const scatter = pairMetrics(points, "drawdown", "return_pct");

  return (
    <>
      <PageHeader
        title="Result Populations"
        breadcrumb={["Research", "Result Populations"]}
        description="Committed result-population summaries and the per-variant metrics committed alongside them. Offline research backtest outputs only — nothing here is a performance claim, a ranking, or a readiness signal."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Populations" value={envelope.data.count ?? items.length} />
        <StatCard label="Committed denominator" value={totalCommitted} />
        <StatCard
          label="Result rows"
          value={totalRows}
          hint={
            totalRows === totalCommitted
              ? "matches committed denominator"
              : "differs from committed denominator"
          }
        />
        <StatCard
          label="Charted variant rows"
          value={points.length}
          hint="full denominator, no winner slice"
        />
      </div>

      {populations.length > 0 ? (
        <ChartCard
          title="Outcome distribution by population"
          subtitle="Committed outcome counts per population, stacked across the full committed denominator."
          footer={
            <ChartProvenanceNote
              source="GET /api/research/result-populations"
              fields={["result_population_id", "outcome_counts"]}
              derived={["stacked segment order"]}
              drawn={populations.length}
              note="Bookkeeping keys (counts_sum, counts_sum_equals_committed_denominator) are excluded from the stack."
            />
          }
        >
          <OutcomeDistributionChart
            populations={populations}
            categoryTones={OUTCOME_TONE}
            ariaLabel={`Stacked outcome distribution across ${populations.length} committed result populations`}
          />
        </ChartCard>
      ) : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {returns.values.length > 0 ? (
          <ChartCard
            title="Per-variant return distribution"
            subtitle="How committed return_pct is spread across every variant row, offline research runs only."
            badges={<Badge tone="neutral">descriptive</Badge>}
            footer={
              <ChartProvenanceNote
                source={DETAIL_ENDPOINT}
                fields={["variant_result_rows[].metrics.return_pct"]}
                derived={["equal-width histogram bins"]}
                drawn={returns.values.length}
                missing={returns.missing}
                note="An empty bin means no variant landed in that range."
              />
            }
          >
            <ReturnDistributionChart values={returns.values} />
          </ChartCard>
        ) : (
          <UnavailableChartState
            title="Per-variant return distribution"
            absence="unavailable"
            reason="No committed variant row carries a return_pct value."
            source="variant_result_rows[].metrics.return_pct"
          />
        )}

        {drawdowns.values.length > 0 ? (
          <ChartCard
            title="Per-variant max-drawdown distribution"
            subtitle="Scalar max drawdown committed per variant. This is not a drawdown curve over time."
            badges={<Badge tone="neutral">descriptive</Badge>}
            footer={
              <ChartProvenanceNote
                source={DETAIL_ENDPOINT}
                fields={["variant_result_rows[].metrics.drawdown"]}
                derived={["equal-width histogram bins"]}
                drawn={drawdowns.values.length}
                missing={drawdowns.missing}
              />
            }
          >
            <DrawdownDistributionChart values={drawdowns.values} />
          </ChartCard>
        ) : (
          <UnavailableChartState
            title="Per-variant max-drawdown distribution"
            absence="unavailable"
            reason="No committed variant row carries a drawdown value."
            source="variant_result_rows[].metrics.drawdown"
          />
        )}
      </div>

      {scatter.pairs.length > 0 ? (
        <ChartCard
          title="Max drawdown vs return, per variant"
          subtitle="Two committed numbers plotted against each other. No quadrant is preferred and no variant is selected."
          footer={
            <ChartProvenanceNote
              source={DETAIL_ENDPOINT}
              fields={[
                "variant_result_rows[].metrics.drawdown",
                "variant_result_rows[].metrics.return_pct",
              ]}
              drawn={scatter.pairs.length}
              missing={scatter.missing}
              note="Rows missing either value are omitted, not placed at the origin."
            />
          }
        >
          <DrawdownVsReturnScatter
            points={scatter.pairs.map((p) => ({
              x: p.x,
              y: p.y,
              label: `${p.point.result_population_id} · ${p.point.variant_id}`,
            }))}
          />
        </ChartCard>
      ) : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <UnavailableChartState
          title="Equity curve"
          absence="deferred"
          reason="The read-only API projects no per-bar or per-trade equity series for a result population. Only committed scalar metrics per variant are exposed."
          source="tools/operator_dashboard_api/readers.py::_variant_rows"
        />
        <UnavailableChartState
          title="Per-trade return distribution"
          absence="withheld"
          reason={
            (envelope.withheld?.per_trade_distributions as string | undefined) ??
            "Per-trade distributions are withheld by the API."
          }
          source="envelope.withheld.per_trade_distributions"
        />
      </div>

      <Card>
        <CardTitle>Populations ({envelope.data.count ?? items.length})</CardTitle>
        {items.length === 0 ? (
          <EmptyState message="No committed result populations found." />
        ) : (
          <ul className="flex flex-col gap-3">
            {items.map((rp) => {
              const segments = outcomeSegments(rp.outcome_counts);
              const rowsMatch =
                rp.result_row_count === rp.committed_denominator;
              return (
                <li
                  key={rp.result_population_id}
                  className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-col">
                      <span className="font-mono text-sm text-cockpit-heading">
                        {rp.result_population_id}
                      </span>
                      <span className="font-mono text-xs text-cockpit-muted">
                        {rp.parent_strategy_spec_id ?? "—"}
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge tone={toneForStatus(rp.validator_status)}>
                        validator: {rp.validator_status ?? "—"}
                      </Badge>
                      <Badge tone={toneForStatus(rp.review_status)}>
                        review: {rp.review_status ?? "—"}
                      </Badge>
                    </div>
                  </div>

                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                    <Badge tone={rowsMatch ? "good" : "warn"}>
                      rows {rp.result_row_count ?? "—"} /{" "}
                      {rp.committed_denominator ?? "—"} committed
                    </Badge>
                    {rp.execution_mode ? (
                      <Badge tone="info">{rp.execution_mode}</Badge>
                    ) : null}
                    {rp.offline_only ? <Badge>offline only</Badge> : null}
                    {rp.no_runtime_contact ? <Badge>no runtime</Badge> : null}
                    {rp.no_paper_live_contact ? (
                      <Badge>no paper/live</Badge>
                    ) : null}
                  </div>

                  {segments.length > 0 ? (
                    <div className="mt-3">
                      <StackedBar segments={segments} />
                    </div>
                  ) : null}
                </li>
              );
            })}
          </ul>
        )}
        <p className="mt-3 text-xs text-cockpit-muted">
          Per-trade distributions are withheld by the API; committed outcome
          counts and committed per-variant metrics are shown.
        </p>
      </Card>

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
