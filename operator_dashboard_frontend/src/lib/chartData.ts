/**
 * Display-only transformations that shape already-committed values into chart
 * series. These derive nothing that is not already present: they bin, sort,
 * total, and label. They never interpolate, extrapolate, zero-fill an absent
 * measurement, or synthesise a series that the API did not project.
 *
 * A missing value is dropped and counted in `missing`, so every chart can state
 * how many rows it actually drew.
 */

import type {
  ApiEnvelope,
  ResultPopulationDetail,
  VariantMetrics,
} from "@/lib/types";

/** A numeric metric available on a committed variant result row. */
export type MetricKey = keyof VariantMetrics;

/** One committed variant row, flattened with the population it belongs to. */
export interface VariantPoint {
  result_population_id: string;
  strategy_spec_id: string | null;
  variant_id: string;
  row_id: string;
  outcome_category: string | null;
  metrics: VariantMetrics;
}

/** A numeric sample drawn from committed rows, with what had to be skipped. */
export interface Sample {
  values: number[];
  /** Rows considered. */
  total: number;
  /** Rows whose metric was absent or non-finite, and were therefore dropped. */
  missing: number;
}

/** A single histogram bin over real observations. */
export interface Bin {
  start: number;
  end: number;
  count: number;
  label: string;
}

/** A labelled categorical count, for bar charts over committed tallies. */
export interface CategoryCount {
  label: string;
  count: number;
}

function isFiniteNumber(v: unknown): v is number {
  return typeof v === "number" && Number.isFinite(v);
}

/** Flatten committed detail envelopes into one variant row per entry. */
export function collectVariantPoints(
  envelopes: ApiEnvelope<ResultPopulationDetail>[],
): VariantPoint[] {
  const points: VariantPoint[] = [];
  for (const envelope of envelopes) {
    const rp = envelope.data;
    if (rp.status !== "available") continue;
    for (const row of rp.variant_result_rows ?? []) {
      points.push({
        result_population_id: rp.result_population_id ?? "—",
        strategy_spec_id: rp.parent_strategy_spec_id ?? null,
        variant_id: row.variant_id ?? "—",
        row_id: row.row_id ?? "—",
        outcome_category: row.outcome_category ?? null,
        metrics: row.metrics ?? {},
      });
    }
  }
  return points;
}

/** Draw one metric across variant rows, reporting rows that carried no value. */
export function sampleMetric(
  points: VariantPoint[],
  metric: MetricKey,
): Sample {
  const values: number[] = [];
  for (const point of points) {
    const v = point.metrics[metric];
    if (isFiniteNumber(v)) values.push(v);
  }
  return {
    values,
    total: points.length,
    missing: points.length - values.length,
  };
}

/**
 * Bin real observations into `binCount` equal-width bins spanning [min, max].
 *
 * An empty bin means no observation fell in that range — which is a fact about
 * the data, not a fabricated zero. A sample with no values yields no bins at
 * all, so callers must render an empty state rather than an axis of zeroes.
 */
export function histogram(values: number[], binCount = 12): Bin[] {
  if (values.length === 0 || binCount < 1) return [];

  const min = Math.min(...values);
  const max = Math.max(...values);

  // A degenerate range (every observation identical) is one exact bin.
  if (min === max) {
    return [
      { start: min, end: max, count: values.length, label: formatNumber(min) },
    ];
  }

  const width = (max - min) / binCount;
  const bins: Bin[] = Array.from({ length: binCount }, (_, i) => {
    const start = min + i * width;
    const end = i === binCount - 1 ? max : start + width;
    return { start, end, count: 0, label: formatNumber(start) };
  });

  for (const v of values) {
    // The final bin is closed on the right so `max` lands inside it.
    const raw = Math.floor((v - min) / width);
    const index = Math.min(raw, binCount - 1);
    bins[index].count += 1;
  }

  return bins;
}

/** Pair two metrics for a scatter, keeping only rows where both are present. */
export function pairMetrics(
  points: VariantPoint[],
  x: MetricKey,
  y: MetricKey,
): { pairs: Array<{ x: number; y: number; point: VariantPoint }>; missing: number } {
  const pairs: Array<{ x: number; y: number; point: VariantPoint }> = [];
  for (const point of points) {
    const xv = point.metrics[x];
    const yv = point.metrics[y];
    if (isFiniteNumber(xv) && isFiniteNumber(yv)) {
      pairs.push({ x: xv, y: yv, point });
    }
  }
  return { pairs, missing: points.length - pairs.length };
}

/**
 * Turn a committed count record into bar-chart categories.
 *
 * Zero buckets are preserved by default: a committed tally of zero is a real
 * observation. `hideZero` drops them where the empty buckets add only noise.
 */
export function countCategories(
  counts: Record<string, number | boolean> | undefined,
  options: { hideZero?: boolean; exclude?: ReadonlySet<string> } = {},
): CategoryCount[] {
  if (!counts) return [];
  const { hideZero = false, exclude } = options;
  return Object.entries(counts)
    .filter(([k, v]) => typeof v === "number" && !exclude?.has(k))
    .map(([label, count]) => ({ label, count: count as number }))
    .filter((row) => !hideZero || row.count > 0);
}

/** Tally committed variant rows by their committed outcome category. */
export function outcomeCategoryCounts(points: VariantPoint[]): CategoryCount[] {
  const tally = new Map<string, number>();
  for (const point of points) {
    const key = point.outcome_category ?? "unlabelled";
    tally.set(key, (tally.get(key) ?? 0) + 1);
  }
  return [...tally.entries()]
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count);
}

/** Compact fixed-precision formatting for axis ticks and tooltips. */
export function formatNumber(value: number, digits = 3): string {
  if (!Number.isFinite(value)) return "—";
  if (value !== 0 && Math.abs(value) < 1e-3) return value.toExponential(1);
  return Number(value.toFixed(digits)).toString();
}

/** Render a ratio as a percentage string for display only. */
export function formatPercent(value: number, digits = 1): string {
  if (!Number.isFinite(value)) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}
