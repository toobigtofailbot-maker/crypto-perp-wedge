/**
 * Strategy Explorer — read-only drilldown on one committed strategy spec.
 *
 * Opens a spec and shows what it declares, what evidence names it, and how that
 * evidence behaved. Nothing here executes, approves, promotes, ranks, or
 * recommends, and nothing here writes. Where the read-only API projects no data,
 * the section says so rather than drawing an empty axis.
 */
import type { Metadata } from "next";
import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { UnavailableState } from "@/components/States";
import { ChartCard } from "@/components/charts/ChartCard";
import { ChartProvenanceNote } from "@/components/charts/ChartProvenanceNote";
import { UnavailableChartState } from "@/components/charts/UnavailableChartState";
import { OutcomeDistributionChart } from "@/components/charts/OutcomeDistributionChart";
import {
  DrawdownDistributionChart,
  ReturnDistributionChart,
} from "@/components/charts/MetricHistogramChart";
import { DrawdownVsReturnScatter } from "@/components/charts/DrawdownVsReturnScatter";
import {
  ExplorerSection,
  SectionNav,
  UnavailablePanel,
} from "@/components/explorer/primitives";
import { SpecLogicPanel } from "@/components/explorer/SpecLogicPanel";
import { FreeParameterTable } from "@/components/explorer/FreeParameterTable";
import { VariantGrid } from "@/components/explorer/VariantGrid";
import { EvidencePanel } from "@/components/explorer/EvidencePanel";
import { SourceArtifacts } from "@/components/explorer/SourceArtifacts";
import { BoundaryPanel } from "@/components/explorer/BoundaryPanel";
import {
  AssumptionsPanel,
  DataRequirements,
} from "@/components/explorer/DataAndAssumptions";
import { toneForStatus, OUTCOME_TONE } from "@/lib/status";
import {
  collectVariantPoints,
  outcomeCategoryCounts,
  pairMetrics,
  sampleMetric,
} from "@/lib/chartData";
import {
  linkedPopulation,
  orDash,
  populationsForStrategy,
} from "@/lib/explorer";
import { fixtures } from "@/lib/fixtures";

const RP_ENDPOINT = "GET /api/research/result-populations/{id}";
const SPEC_ENDPOINT = "GET /api/strategies/{id}";

const SECTIONS = [
  { id: "identity", label: "Identity" },
  { id: "evidence", label: "Evidence" },
  { id: "variants", label: "Variants" },
  { id: "performance", label: "Performance" },
  { id: "robustness", label: "Robustness" },
  { id: "logic", label: "Logic" },
  { id: "parameters", label: "Parameters" },
  { id: "data", label: "Data & assumptions" },
  { id: "provenance", label: "Provenance" },
  { id: "boundary", label: "Boundary" },
];

/** Prerender the committed specs. Unknown ids still render an honest absence. */
export function generateStaticParams() {
  return (fixtures.strategies().data.items ?? []).map((strategy) => ({
    strategy_id: strategy.strategy_id ?? "",
  }));
}

export const metadata: Metadata = {
  title: "Strategy Explorer",
};

export default function StrategyDetailPage({
  params,
}: {
  params: { strategy_id: string };
}) {
  const id = decodeURIComponent(params.strategy_id);

  // Lifecycle status survives only on the list endpoint: the detail reader
  // overwrites `status` with the envelope status. Read each from its source.
  const summary = (fixtures.strategies().data.items ?? []).find(
    (s) => s.strategy_id === id,
  );
  const envelope = fixtures.strategyDetail(id);
  const spec = envelope?.data;

  if (!envelope || !spec) {
    return (
      <>
        <PageHeader
          title={id}
          breadcrumb={["Strategies", id]}
          description="No committed strategy spec carries this id."
        />
        <Link
          href="/strategies"
          className="text-xs text-cockpit-accent hover:underline"
        >
          ← All strategies
        </Link>
        <UnavailableState
          title="Strategy unavailable"
          reason={`${id} is not present as a committed artifact. The read-only API answers GET /api/strategies/${id} with an "unavailable" envelope rather than a 404, and this page renders that absence verbatim. Nothing is substituted.`}
        />
      </>
    );
  }

  const linked = populationsForStrategy(fixtures.resultPopulationDetails(), id);
  const populations = linked.map(linkedPopulation);
  const points = collectVariantPoints(linked);

  const returns = sampleMetric(points, "return_pct");
  const drawdowns = sampleMetric(points, "drawdown");
  const scatter = pairMetrics(points, "drawdown", "return_pct");
  const outcomeCounts = outcomeCategoryCounts(points);

  const outcomeStacks = linked.map((e) => ({
    id: e.data.result_population_id ?? "—",
    counts: Object.fromEntries(
      outcomeCategoryCounts(collectVariantPoints([e])).map((c) => [
        c.label,
        c.count,
      ]),
    ),
  }));

  const variantManifestIds = [
    ...new Set(
      populations
        .map((p) => p.variant_manifest_id)
        .filter((v): v is string => Boolean(v)),
    ),
  ];

  return (
    <>
      <PageHeader
        title={spec.title ?? id}
        breadcrumb={["Strategies", id]}
        description="Read-only inspection of one committed strategy spec and the offline result populations that name it in their lineage. A strategy spec is a planning artifact: not executable, not a candidate, not approved, not ranked."
      />

      <Link
        href="/strategies"
        className="text-xs text-cockpit-accent hover:underline"
      >
        ← All strategies
      </Link>

      <SectionNav sections={SECTIONS} />

      {/* 1 — Identity ------------------------------------------------- */}
      <ExplorerSection
        id="identity"
        title="Strategy identity"
        aside={
          <>
            {summary?.status ? (
              <Badge tone={toneForStatus(summary.status)}>
                {summary.status}
              </Badge>
            ) : null}
            {spec.not_executable ? (
              <Badge tone="warn">not executable</Badge>
            ) : null}
            {spec.direction ? <Badge>{spec.direction}</Badge> : null}
            {spec.primary_timeframe ? (
              <Badge tone="info">{spec.primary_timeframe}</Badge>
            ) : null}
          </>
        }
      >
        <div className="grid grid-cols-1 gap-x-8 md:grid-cols-2">
          <div className="flex flex-col">
            <KeyValue label="Strategy ID" value={orDash(spec.strategy_id)} />
            <KeyValue label="Short name" value={orDash(spec.short_name)} />
            <KeyValue label="Title" value={orDash(spec.title)} />
            <KeyValue
              label="Lifecycle status"
              value={orDash(summary?.status)}
            />
            <KeyValue label="Source type" value={orDash(spec.source_type)} />
            <KeyValue
              label="Approval scope"
              value={orDash(spec.review?.approval_scope)}
            />
          </div>
          <div className="flex flex-col">
            <KeyValue
              label="Instrument family"
              value={orDash(spec.instrument_family)}
            />
            <KeyValue label="Market type" value={orDash(spec.market_type)} />
            <KeyValue
              label="Primary timeframe"
              value={orDash(spec.primary_timeframe)}
            />
            <KeyValue label="Direction" value={orDash(spec.direction)} />
            <KeyValue
              label="Max free parameters"
              value={orDash(spec.max_free_parameters)}
            />
            <KeyValue
              label="Not executable"
              value={orDash(spec.not_executable)}
            />
          </div>
        </div>
        <p className="mt-3 text-xs text-cockpit-muted">
          Lifecycle status is read from{" "}
          <span className="font-mono text-cockpit-text">GET /api/strategies</span>
          . On{" "}
          <span className="font-mono text-cockpit-text">{SPEC_ENDPOINT}</span>{" "}
          the reader overwrites{" "}
          <span className="font-mono text-cockpit-text">status</span> with the
          envelope status ({orDash(spec.status)}), so the spec&apos;s own status
          is not available there.
        </p>
      </ExplorerSection>

      {/* 2 — Evidence ------------------------------------------------- */}
      <ExplorerSection
        id="evidence"
        title="Evidence & result-population linkage"
        subtitle="Committed offline result populations whose lineage names this spec, with the denominator reconciliation each artifact asserts."
      >
        {populations.length > 0 ? (
          <EvidencePanel
            populations={populations}
            identityHashes={linked.map((e) => ({
              id: e.data.result_population_id ?? "—",
              result_population_identity_hash:
                e.data.result_population_identity_hash ?? null,
              input_identity_hash: e.data.input_identity_hash ?? null,
            }))}
          />
        ) : (
          <UnavailablePanel
            title="No linked result population"
            absence="unavailable"
            reason={`No committed result population names "${id}" as its parent strategy spec. No evidence has been produced for this spec.`}
            source="result_population.lineage.strategy_spec_id"
          />
        )}
      </ExplorerSection>

      {/* 3 — Variants ------------------------------------------------- */}
      <ExplorerSection
        id="variants"
        title="Variant grid"
        subtitle="Every committed variant result row across the linked populations, printed as committed."
      >
        {points.length > 0 ? (
          <VariantGrid points={points} variantManifestIds={variantManifestIds} />
        ) : (
          <UnavailablePanel
            title="No variant rows"
            absence="unavailable"
            reason="No linked result population projects a variant result row."
            source="variant_result_rows[]"
          />
        )}
      </ExplorerSection>

      {/* 4 — Performance ---------------------------------------------- */}
      <ExplorerSection
        id="performance"
        title="Performance visuals"
        subtitle="Drawn only from committed per-variant scalar metrics. The API projects no time series, so no curve is drawn."
      >
        <div className="flex flex-col gap-4">
          {outcomeStacks.length > 0 ? (
            <ChartCard
              title="Outcome distribution by linked population"
              subtitle="Committed outcome category per variant row, stacked across the full committed denominator."
              footer={
                <ChartProvenanceNote
                  source={RP_ENDPOINT}
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
                populations={outcomeStacks}
                categoryTones={OUTCOME_TONE}
                ariaLabel={`Stacked outcome distribution across ${outcomeStacks.length} result populations linked to ${id}`}
              />
            </ChartCard>
          ) : null}

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {returns.values.length > 0 ? (
              <ChartCard
                title="Per-variant return distribution"
                subtitle="Offline research backtest returns for this spec's committed variants. No bin is preferred."
                footer={
                  <ChartProvenanceNote
                    source={RP_ENDPOINT}
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

            {drawdowns.values.length > 0 ? (
              <ChartCard
                title="Per-variant max-drawdown distribution"
                subtitle="Scalar max drawdown recorded per variant. This is not a drawdown curve."
                footer={
                  <ChartProvenanceNote
                    source={RP_ENDPOINT}
                    fields={["variant_result_rows[].metrics.drawdown"]}
                    derived={["equal-width histogram bins"]}
                    drawn={drawdowns.values.length}
                    missing={drawdowns.missing}
                  />
                }
              >
                <DrawdownDistributionChart
                  values={drawdowns.values}
                  binCount={8}
                />
              </ChartCard>
            ) : (
              <UnavailableChartState
                title="Per-variant max-drawdown distribution"
                absence="unavailable"
                reason="No linked variant row carries a drawdown value."
                source="variant_result_rows[].metrics.drawdown"
              />
            )}
          </div>

          {scatter.pairs.length > 0 ? (
            <ChartCard
              title="Max drawdown vs return"
              subtitle="One dot per committed variant row. No quadrant is preferred."
              footer={
                <ChartProvenanceNote
                  source={RP_ENDPOINT}
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
                height={240}
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

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <UnavailableChartState
              title="Equity curve"
              absence="deferred"
              reason="No per-bar or per-trade equity series is projected for a strategy spec or its result populations."
              source="tools/operator_dashboard_api/readers.py::_variant_rows"
            />
            <UnavailableChartState
              title="Drawdown curve"
              absence="deferred"
              reason="Only a scalar max drawdown per variant is committed. No drawdown-over-time series exists to draw."
              source="variant_result_rows[].metrics.drawdown"
            />
            <UnavailableChartState
              title="Return series over time"
              absence="deferred"
              reason="Returns are committed as one scalar per variant, not as a series indexed by time."
              source="variant_result_rows[].metrics.return_pct"
            />
          </div>

          {outcomeCounts.length > 0 ? (
            <p className="text-xs text-cockpit-muted">
              Outcome tally across all linked populations:{" "}
              {outcomeCounts.map((c) => `${c.label} ${c.count}`).join(" · ")}
            </p>
          ) : null}
        </div>
      </ExplorerSection>

      {/* 5 — WFO / OOS / robustness / Monte Carlo ---------------------- */}
      <ExplorerSection
        id="robustness"
        title="Walk-forward, OOS, robustness & Monte Carlo"
        subtitle="None of these are projected by the read-only API. Nothing is fabricated to fill the section."
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <UnavailableChartState
            title="Walk-forward (WFO) / OOS"
            absence="deferred"
            reason="The read-only API projects no walk-forward folds, windows, per-fold statistics, or out-of-sample split for a strategy spec."
            source="tools/operator_dashboard_api/readers.py"
          />
          <UnavailableChartState
            title="Monte Carlo"
            absence="deferred"
            reason="No Monte Carlo paths, resamples, or path-dependent distributions are projected at any endpoint."
            source="tools/operator_dashboard_api/readers.py"
          />
          <UnavailableChartState
            title="Robustness statistics"
            absence="withheld"
            reason="PSR, DSR, and MinTRL are named as withheld in the committed report artifacts and are not exposed as values."
            source="report.withheld_statistics"
          />
          <UnavailablePanel
            title="Review state of linked evidence"
            absence="unavailable"
            reason={
              populations.length > 0
                ? `Every linked population projects review_status = ${[
                    ...new Set(
                      populations.map((p) => p.review_status ?? "—"),
                    ),
                  ].join(", ")}. No robustness review has been recorded.`
                : "No linked population exists to carry a review state."
            }
            source="result_population.review.review_status"
          />
        </div>
      </ExplorerSection>

      {/* 6 — Logic ---------------------------------------------------- */}
      <ExplorerSection
        id="logic"
        title="Declared logic"
        subtitle="Transcribed from the spec's committed operand tree. Not evaluated, not simulated, not executable."
      >
        <div className="flex flex-col gap-5">
          <SpecLogicPanel
            label="Entry logic"
            groups={spec.entry_logic?.groups}
            notes={spec.entry_logic?.notes}
            emptyLabel="The spec declares no entry groups."
          />
          <SpecLogicPanel
            label="Exit logic"
            groups={spec.exit_logic?.groups}
            notes={spec.exit_logic?.notes}
            emptyLabel="The spec declares no exit groups."
          />
          {spec.exit_logic?.max_holding_period ? (
            <p className="text-xs text-cockpit-muted">
              <span className="uppercase tracking-wider">
                max holding period
              </span>{" "}
              enabled={orDash(spec.exit_logic.max_holding_period.enabled)} · bars=
              {orDash(spec.exit_logic.max_holding_period.bars)}
            </p>
          ) : null}
          <SpecLogicPanel
            label="Filters"
            groups={spec.filters?.groups}
            notes={
              spec.filters?.none_declared === true
                ? "The spec declares filters.none_declared = true."
                : undefined
            }
            emptyLabel="The spec declares no filter groups."
          />
        </div>
      </ExplorerSection>

      {/* 7 — Free parameters ------------------------------------------ */}
      <ExplorerSection
        id="parameters"
        title="Free parameters"
        subtitle="The parameter space the spec declares. Not a per-variant assignment."
      >
        <FreeParameterTable
          freeParameters={spec.free_parameters}
          apiProjectedCount={spec.free_parameter_count}
        />
      </ExplorerSection>

      {/* 8 — Data & assumptions --------------------------------------- */}
      <ExplorerSection
        id="data"
        title="Data requirements & backtest assumptions"
        subtitle="What the spec needs, and what each linked offline backtest presumed."
      >
        <div className="flex flex-col gap-5">
          <DataRequirements timeframeAndData={spec.timeframe_and_data} />
          <AssumptionsPanel
            populations={linked.map((e) => ({
              id: e.data.result_population_id ?? "—",
              backtest_assumption_summary:
                e.data.backtest_assumption_summary ?? {},
              data_coverage_summary: e.data.data_coverage_summary ?? {},
            }))}
          />
        </div>
      </ExplorerSection>

      {/* 9 — Provenance ----------------------------------------------- */}
      <ExplorerSection
        id="provenance"
        title="Provenance & source artifacts"
        subtitle="Paths and digests, shown as text. This surface performs no filesystem navigation."
      >
        <SourceArtifacts
          specPath={spec.path}
          envelopeProvenance={envelope.provenance ?? []}
          provenance={spec.provenance}
        />
      </ExplorerSection>

      {/* 10 — Boundary ------------------------------------------------ */}
      <ExplorerSection
        id="boundary"
        title="Boundary & non-authority"
        subtitle="Read from the committed artifacts' own declaration flags."
      >
        <BoundaryPanel
          nonExecutionDeclaration={spec.non_execution_declaration}
          review={spec.review}
          populationDeclarations={linked.map((e) => ({
            id: e.data.result_population_id ?? "—",
            declaration: e.data.non_authority_declaration ?? {},
          }))}
        />
      </ExplorerSection>

      <Card>
        <CardTitle>Linked artifacts</CardTitle>
        <div className="flex flex-col">
          {populations.length === 0 ? (
            <p className="text-xs text-cockpit-muted">
              No linked result population.
            </p>
          ) : (
            populations.map((population) => (
              <KeyValue
                key={population.result_population_id}
                label={population.result_population_id}
                value={`${orDash(population.result_row_count)} / ${orDash(
                  population.committed_denominator,
                )} committed rows`}
              />
            ))
          )}
        </div>
      </Card>

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
