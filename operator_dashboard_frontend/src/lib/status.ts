/**
 * Display-only helpers that map read-only status strings to a cockpit tone and
 * derive simple frontend aggregations. These confer no authority — they only
 * decide how an already-committed value is coloured or summed for presentation.
 */

export type Tone = "neutral" | "good" | "warn" | "bad" | "info";

const GOOD = new Set([
  "pass",
  "passed",
  "available",
  "complete",
  "completed",
  "fresh",
  "ok",
  "advisory_packet_ready",
  "reported",
]);
const WARN = new Set([
  "warn",
  "warning",
  "unavailable",
  "not_available",
  "not_reviewed",
  "awaiting_prereg_approval",
  "awaiting_execute_approval",
  "pending",
  "queued",
  "running",
  "stale",
  "not_started",
  "draft",
]);
const BAD = new Set([
  "fail",
  "failed",
  "blocked",
  "error",
  "errored",
  "no-go",
  "no_go",
  "oos_gate_fail",
]);

/**
 * Map an arbitrary read-only status string to a cockpit tone. Case-insensitive.
 * Unknown values fall back to "neutral" so nothing is fabricated as green.
 */
export function toneForStatus(status: string | null | undefined): Tone {
  if (!status) return "neutral";
  const key = status.trim().toLowerCase();
  if (GOOD.has(key)) return "good";
  if (BAD.has(key)) return "bad";
  if (WARN.has(key)) return "warn";
  return "neutral";
}

/**
 * Keys inside a committed `outcome_counts` block that are bookkeeping, not
 * outcome buckets. They must never be charted as a category.
 */
export const OUTCOME_META: ReadonlySet<string> = new Set([
  "counts_sum",
  "counts_sum_equals_committed_denominator",
]);

/** Tone per committed outcome category, so a failure never renders healthy. */
export const OUTCOME_TONE: Record<string, Tone> = {
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

/** Humanise a snake_case key for labels (display only). */
export function humanize(key: string): string {
  return key.replace(/_/g, " ");
}

/** Sum the numeric values of a record, ignoring non-numbers. */
export function sumCounts(record: Record<string, number> | undefined): number {
  if (!record) return 0;
  return Object.values(record).reduce(
    (acc, v) => (typeof v === "number" ? acc + v : acc),
    0,
  );
}
