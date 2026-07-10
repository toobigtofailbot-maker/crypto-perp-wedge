/**
 * The honest stand-in for a chart that cannot be drawn.
 *
 * Every chart the operator asked for that has no data renders one of these
 * instead of an empty axis. Nothing here is zero-filled, interpolated, or
 * approximated — the panel says which of the three reasons applies and stops.
 */
import { Badge, Card, CardTitle } from "@/components/ui";

/**
 * - `withheld`    — the value exists upstream but is deliberately not exposed.
 * - `unavailable` — no such artifact or measurement has been produced.
 * - `deferred`    — the read-only API does not project enough data to draw it,
 *                   and widening the API is out of this package's scope.
 */
export type ChartAbsence = "withheld" | "unavailable" | "deferred";

const ABSENCE_TONE = {
  withheld: "neutral",
  unavailable: "warn",
  deferred: "info",
} as const;

const ABSENCE_BLURB: Record<ChartAbsence, string> = {
  withheld: "Data exists upstream but is not exposed to this surface.",
  unavailable: "No such artifact or measurement has been produced.",
  deferred: "The read-only API does not project the series required to draw this.",
};

export function UnavailableChartState({
  title,
  absence,
  reason,
  source,
}: {
  title: string;
  absence: ChartAbsence;
  /** The specific, repo-truthful reason this chart has no series. */
  reason: string;
  /** Where the absence is declared, e.g. an envelope key or artifact field. */
  source?: string;
}) {
  return (
    <Card className="flex flex-col border-dashed">
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <CardTitle>{title}</CardTitle>
        <div className="mb-3">
          <Badge tone={ABSENCE_TONE[absence]}>{absence}</Badge>
        </div>
      </div>

      <div className="flex min-h-[7rem] flex-col justify-center gap-2 rounded border border-dashed border-cockpit-border bg-cockpit-panel-2/40 px-4 py-5">
        <p className="text-sm text-cockpit-text">{reason}</p>
        <p className="text-xs text-cockpit-muted">{ABSENCE_BLURB[absence]}</p>
      </div>

      <p className="mt-3 text-xs text-cockpit-muted">
        No series is rendered. Nothing is inferred, zero-filled, or simulated.
        {source ? (
          <>
            {" "}
            Declared by <span className="break-all font-mono text-cockpit-text">{source}</span>.
          </>
        ) : null}
      </p>
    </Card>
  );
}
