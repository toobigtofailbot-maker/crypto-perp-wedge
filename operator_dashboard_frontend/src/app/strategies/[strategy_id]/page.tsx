import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { PlaceholderCard, UnavailableState } from "@/components/States";
import { ChartCard } from "@/components/charts/ChartCard";
import { ChartProvenanceNote } from "@/components/charts/ChartProvenanceNote";
import { UnavailableChartState } from "@/components/charts/UnavailableChartState";
import { OutcomeDistributionChart } from "@/components/charts/OutcomeDistributionChart";
import { ReturnDistributionChart } from "@/components/charts/MetricHistogramChart";
import { DrawdownVsReturnScatter } from "@/components/charts/DrawdownVsReturnScatter";
import { toneForStatus, OUTCOME_TONE } from "@/lib/status";
import {
  collectVariantPoints,
  outcomeCategoryCounts,
  pairMetrics,
  sampleMetric,
} from "@/lib/chartData";
import { fixtures } from "@/lib/fixtures";

const DETAIL_ENDPOINT = "GET /api/research/result-populations/{id}";

export default function StrategyDetailPage({
  params,
}: {
  params: { strategy_id: string };
}) {
  const id = decodeURIComponent(params.strategy_id);
  const items = fixtures.strategies().data.items ?? [];
  const strategy = items.find((s) => s.strategy_id === id);

  // Committed result populations whose lineage names this strategy spec.
  const linked = fixtures
    .resultPopulationDetails()
    .filter((e) => e.data.parent_strategy_spec_id === id);

  const points = collectVariantPoints(linked);
  const returns = sampleMetric(points, "return_pct");
  const scatter = pairMetrics(points, "drawdown", "return_pct");
  const outcomeCounts = outcomeCategoryCounts(points);

  const populations = linked.map((e) => ({
    id: e.data.result_population_id ?? "—",
    counts: Object.fromEntries(
      outcomeCategoryCounts(collectVariantPoints([e])).map((c) => [
        c.label,
        c.count,
      ]),
    ),
  }));

  return (
    <>
      <PageHeader
        title={strategy?.title ?? id}
        breadcrumb={["Strategies", id]}
        description="Read-only strategy summary and the committed offline result populations that name it in their lineage. Nothing here is executable, ranked, or approved."
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

      {linked.length > 0 ? (
        <>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="info">
              {linked.length} linked result population
              {linked.length === 1 ? "" : "s"}
            </Badge>
            <Badge tone="neutral">{points.length} committed variant rows</Badge>
            <Badge tone="neutral">offline research only</Badge>
          </div>

          <ChartCard
            title="Outcome distribution by linked population"
            subtitle="Committed outcome category per variant row, stacked across the full committed denominator."
            footer={
              <ChartProvenanceNote
                source={DETAIL_ENDPOINT}
                fields={[
                  "parent_strategy_spec_id",
                  "variant_result_rows[].outcome_category",
                ]}
                derived={["count per outcome category"]}
                drawn={points.length}
              />
            }
          >
            <OutcomeDistributionChart
              populations={populations}
              categoryTones={OUTCOME_TONE}
              ariaLabel={`Stacked outcome distribution across ${populations.length} result populations linked to ${id}`}
            />
          </ChartCard>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {returns.values.length > 0 ? (
              <ChartCard
                title="Per-variant return distribution"
                subtitle="Offline research backtest returns for this strategy's committed variants."
                footer={
                  <ChartProvenanceNote
                    source={DETAIL_ENDPOINT}
                    fields={["variant_result_rows[].metrics.return_pct"]}
                    derived={["equal-width histogram bins"]}
                    drawn={returns.values.length}
                    missing={returns.missing}
                  />
                }
              >
                <ReturnDistributionChart values={returns.values} binCount={8} />
              </ChartCard>
            ) : (
              <UnavailableChartState
                title="Per-variant return distribution"
                absence="unavailable"
                reason="No linked variant row carries a return_pct value."
                source="variant_result_rows[].metrics.return_pct"
              />
            )}

            {scatter.pairs.length > 0 ? (
              <ChartCard
                title="Max drawdown vs return"
                subtitle="One dot per committed variant row. No quadrant is preferred."
                footer={
                  <ChartProvenanceNote
                    source={DETAIL_ENDPOINT}
                    fields={[
                      "variant_result_rows[].metrics.drawdown",
                      "variant_result_rows[].metrics.return_pct",
                    ]}
                    drawn={scatter.pairs.length}
                    missing={scatter.missing}
                  />
                }
              >
                <DrawdownVsReturnScatter
                  points={scatter.pairs.map((p) => ({
                    x: p.x,
                    y: p.y,
                    label: `${p.point.result_population_id} · ${p.point.variant_id}`,
                  }))}
                  height={220}
                />
              </ChartCard>
            ) : (
              <UnavailableChartState
                title="Max drawdown vs return"
                absence="unavailable"
                reason="No linked variant row carries both a drawdown and a return_pct value."
                source="variant_result_rows[].metrics"
              />
            )}
          </div>

          <Card>
            <CardTitle>Linked result populations</CardTitle>
            <div className="flex flex-col">
              {linked.map((e) => (
                <KeyValue
                  key={e.data.result_population_id}
                  label={e.data.result_population_id ?? "—"}
                  value={`${e.data.result_row_count ?? "—"} / ${e.data.committed_denominator ?? "—"} committed rows`}
                />
              ))}
            </div>
            <p className="mt-3 text-xs text-cockpit-muted">
              Outcome tally:{" "}
              {outcomeCounts
                .map((c) => `${c.label} ${c.count}`)
                .join(" · ")}
            </p>
          </Card>
        </>
      ) : (
        <UnavailableChartState
          title="Result-population charts"
          absence="unavailable"
          reason={`No committed result population names "${id}" as its parent strategy spec, so there are no variant rows to chart.`}
          source="result_population.lineage.strategy_spec_id"
        />
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <UnavailableChartState
          title="Walk-forward (WFO)"
          absence="deferred"
          reason="The read-only API projects no walk-forward folds, windows, or per-fold statistics for a strategy spec."
          source="tools/operator_dashboard_api/readers.py"
        />
        <UnavailableChartState
          title="Robustness / Monte Carlo"
          absence="withheld"
          reason="Robustness statistics (PSR, DSR, MinTRL) are named as withheld in the committed report artifacts and are not exposed as values. Monte Carlo paths are not projected at all."
          source="report.withheld_statistics"
        />
        <UnavailableChartState
          title="Equity curve"
          absence="deferred"
          reason="No per-bar or per-trade equity series is projected for a strategy spec or its result populations."
          source="tools/operator_dashboard_api/readers.py::_variant_rows"
        />
        <PlaceholderCard title="Artifacts" />
      </div>
    </>
  );
}
