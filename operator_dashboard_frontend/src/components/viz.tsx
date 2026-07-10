/**
 * CSS-only read-only visual summaries for the operator cockpit.
 *
 * These are presentational primitives (labelled count bars and a stacked bar)
 * built entirely from Tailwind utilities and inline width percentages. They
 * render committed counts only — no chart dependency, no data generation, no
 * interactivity.
 */
import type { Tone } from "@/lib/status";

const BAR_CLASS: Record<Tone, string> = {
  neutral: "bg-cockpit-muted/50",
  good: "bg-cockpit-good",
  warn: "bg-cockpit-warn",
  bad: "bg-cockpit-bad",
  info: "bg-cockpit-info",
};

const DOT_CLASS: Record<Tone, string> = {
  neutral: "bg-cockpit-muted/60",
  good: "bg-cockpit-good",
  warn: "bg-cockpit-warn",
  bad: "bg-cockpit-bad",
  info: "bg-cockpit-info",
};

function pct(value: number, max: number): number {
  if (max <= 0) return 0;
  return Math.max(0, Math.min(100, (value / max) * 100));
}

export interface CountRow {
  label: string;
  count: number;
  tone?: Tone;
}

/**
 * A list of labelled rows, each with a proportional bar sized against the
 * largest row. Rows with a zero count are shown but muted, so distributions
 * stay honest about empty buckets. `hideZero` drops empty buckets entirely.
 */
export function CountBars({
  rows,
  hideZero = false,
}: {
  rows: CountRow[];
  hideZero?: boolean;
}) {
  const visible = hideZero ? rows.filter((r) => r.count > 0) : rows;
  const max = visible.reduce((m, r) => Math.max(m, r.count), 0);
  if (visible.length === 0) {
    return (
      <p className="text-xs text-cockpit-muted">No non-zero buckets.</p>
    );
  }
  return (
    <div className="flex flex-col gap-2">
      {visible.map((r) => (
        <div
          key={r.label}
          className="grid grid-cols-[9rem_1fr_2.5rem] items-center gap-2 text-xs"
        >
          <span
            className={`truncate ${r.count > 0 ? "text-cockpit-text" : "text-cockpit-muted"}`}
            title={r.label}
          >
            {r.label}
          </span>
          <span className="h-2 w-full overflow-hidden rounded-full bg-cockpit-panel-2">
            <span
              className={`block h-full rounded-full ${BAR_CLASS[r.tone ?? "info"]}`}
              style={{ width: `${pct(r.count, max)}%` }}
            />
          </span>
          <span className="text-right font-mono text-cockpit-text">
            {r.count}
          </span>
        </div>
      ))}
    </div>
  );
}

export interface StackSegment {
  label: string;
  count: number;
  tone?: Tone;
}

/**
 * A single horizontal stacked bar with a legend beneath. Useful for compact
 * outcome distributions where the total is meaningful.
 */
export function StackedBar({
  segments,
  total,
}: {
  segments: StackSegment[];
  total?: number;
}) {
  const sum = total ?? segments.reduce((s, seg) => s + seg.count, 0);
  const nonZero = segments.filter((s) => s.count > 0);
  return (
    <div className="flex flex-col gap-2">
      <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-cockpit-panel-2">
        {nonZero.map((seg) => (
          <span
            key={seg.label}
            className={BAR_CLASS[seg.tone ?? "info"]}
            style={{ width: `${pct(seg.count, sum)}%` }}
            title={`${seg.label}: ${seg.count}`}
          />
        ))}
      </div>
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs">
        {segments.map((seg) => (
          <li key={seg.label} className="flex items-center gap-1.5">
            <span
              className={`inline-block h-2 w-2 rounded-sm ${DOT_CLASS[seg.tone ?? "info"]}`}
            />
            <span className="text-cockpit-muted">{seg.label}</span>
            <span className="font-mono text-cockpit-text">{seg.count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
