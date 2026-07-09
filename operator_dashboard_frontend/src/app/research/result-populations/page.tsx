import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, StatCard } from "@/components/ui";
import { StackedBar, type StackSegment } from "@/components/viz";
import { EmptyState } from "@/components/States";
import { toneForStatus, type Tone } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";
import type { ResultPopulationSummary } from "@/lib/types";

// Derived / meta keys inside outcome_counts that are not themselves outcomes.
const OUTCOME_META = new Set([
  "counts_sum",
  "counts_sum_equals_committed_denominator",
]);

const OUTCOME_TONE: Record<string, Tone> = {
  successful: "good",
  failed: "bad",
  errored: "bad",
  aborted: "bad",
  invalid: "bad",
  excluded: "warn",
  filtered: "warn",
  not_attempted: "warn",
  data_unavailable: "warn",
};

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

export default function ResultPopulationsPage() {
  const envelope = fixtures.resultPopulations();
  const items: ResultPopulationSummary[] = envelope.data.items ?? [];

  const totalCommitted = items.reduce(
    (s, rp) => s + (rp.committed_denominator ?? 0),
    0,
  );
  const totalRows = items.reduce((s, rp) => s + (rp.result_row_count ?? 0), 0);

  // Aggregate outcome distribution across every population.
  const aggregate: Record<string, number> = {};
  for (const rp of items) {
    for (const seg of outcomeSegments(rp.outcome_counts)) {
      aggregate[seg.label] = (aggregate[seg.label] ?? 0) + seg.count;
    }
  }
  const aggregateSegments: StackSegment[] = Object.entries(aggregate).map(
    ([label, count]) => ({ label, count, tone: OUTCOME_TONE[label] ?? "neutral" }),
  );

  return (
    <>
      <PageHeader
        title="Result Populations"
        breadcrumb={["Research", "Result Populations"]}
        description="Committed result-population summaries. Per-trade distributions are withheld; only committed fields are projected."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
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
      </div>

      {aggregateSegments.length > 0 ? (
        <Card>
          <CardTitle>Aggregate outcome distribution</CardTitle>
          <StackedBar segments={aggregateSegments} />
        </Card>
      ) : null}

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
          Per-trade distributions are withheld by the API; only committed
          outcome counts are shown.
        </p>
      </Card>

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
