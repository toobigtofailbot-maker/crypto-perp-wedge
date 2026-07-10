/**
 * Every committed variant result row linked to a strategy spec.
 *
 * Metrics are printed exactly as committed — no unit is reinterpreted, no
 * absent value becomes a zero, and no row is ranked, scored, or highlighted as
 * preferable. These are offline research backtest outputs, not performance
 * claims, readiness signals, or candidate authority.
 *
 * The parameter assignment behind each `variant_id` is deliberately absent: the
 * read-only API projects `variant_id`, `row_id`, `outcome_category`,
 * `attempted`, `metrics`, `non_success`, and `error`, and the committed result
 * population stores only an `assignment_hash`. The values themselves live in the
 * parent variant manifest, which no read-only endpoint projects. They are not
 * guessed from the spec's declared parameter space.
 */
import { Badge } from "@/components/ui";
import { Cell, DataTable, FieldNote, Row } from "@/components/explorer/primitives";
import { formatNumber } from "@/lib/chartData";
import type { MetricKey, VariantPoint } from "@/lib/chartData";
import { OUTCOME_TONE } from "@/lib/status";

/** Committed metric keys, printed under their exact field names. */
const METRIC_COLUMNS: MetricKey[] = [
  "return_pct",
  "drawdown",
  "sharpe",
  "win_rate",
  "trade_count",
  "pnl",
  "fees",
  "funding",
  "slippage",
  "exposure",
];

const COLUMNS = [
  "result_population_id",
  "variant_id",
  "row_id",
  "outcome_category",
  ...METRIC_COLUMNS,
];

function MetricCell({ value }: { value: number | null | undefined }) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return (
      <Cell mono muted>
        —
      </Cell>
    );
  }
  return <Cell mono>{formatNumber(value, 4)}</Cell>;
}

export function VariantGrid({
  points,
  variantManifestIds,
}: {
  points: VariantPoint[];
  /** Parent variant manifests that hold the parameter assignments. */
  variantManifestIds: string[];
}) {
  const missingByMetric = METRIC_COLUMNS.map((metric) => ({
    metric,
    missing: points.filter((p) => typeof p.metrics[metric] !== "number").length,
  })).filter((entry) => entry.missing > 0);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="neutral">
          {points.length} committed variant row{points.length === 1 ? "" : "s"}
        </Badge>
        <Badge tone="neutral">offline research only</Badge>
        <Badge tone="warn">not ranked</Badge>
      </div>

      <DataTable columns={COLUMNS}>
        {points.map((point) => (
          <Row key={`${point.result_population_id}-${point.row_id}`}>
            <Cell mono muted>
              {point.result_population_id}
            </Cell>
            <Cell mono>{point.variant_id}</Cell>
            <Cell mono muted>
              {point.row_id}
            </Cell>
            <Cell>
              {point.outcome_category ? (
                <Badge tone={OUTCOME_TONE[point.outcome_category] ?? "neutral"}>
                  {point.outcome_category}
                </Badge>
              ) : (
                <span className="text-cockpit-muted">—</span>
              )}
            </Cell>
            {METRIC_COLUMNS.map((metric) => (
              <MetricCell key={metric} value={point.metrics[metric]} />
            ))}
          </Row>
        ))}
      </DataTable>

      <div className="rounded border border-dashed border-cockpit-border bg-cockpit-panel-2/40 px-3 py-2.5">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
            Per-variant parameter values
          </span>
          <Badge tone="warn">unavailable</Badge>
        </div>
        <p className="text-xs text-cockpit-text">
          The read-only API projects no parameter assignment for a variant row.
          The committed result population stores only an{" "}
          <span className="font-mono">assignment_hash</span>; the values live in
          the parent variant manifest
          {variantManifestIds.length > 0 ? (
            <>
              {" "}
              (
              <span className="font-mono text-cockpit-text">
                {variantManifestIds.join(", ")}
              </span>
              )
            </>
          ) : null}
          , which no read-only endpoint exposes. They are not reconstructed from
          the spec&apos;s declared parameter space.
        </p>
      </div>

      <FieldNote
        source="GET /api/research/result-populations/{id}"
        fields={[
          "variant_result_rows[].variant_id",
          "variant_result_rows[].row_id",
          "variant_result_rows[].outcome_category",
          "variant_result_rows[].metrics",
        ]}
        note={
          missingByMetric.length > 0
            ? `Absent metrics render as an em dash and are never zero-filled: ${missingByMetric
                .map((entry) => `${entry.metric} missing on ${entry.missing}`)
                .join(", ")}.`
            : "Every committed row carries every projected metric. Values are printed as committed; no unit is reinterpreted."
        }
      />
    </div>
  );
}
