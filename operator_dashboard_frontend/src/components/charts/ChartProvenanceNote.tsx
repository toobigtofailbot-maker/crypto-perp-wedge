/**
 * The footnote under every rendered chart: which envelope it came from, which
 * committed fields it read, what was derived for display, how many rows were
 * actually drawn, and what the chart does not mean.
 *
 * `missing` is surfaced rather than swallowed — a chart drawn from 60 of 66
 * rows says so.
 */

export function ChartProvenanceNote({
  source,
  fields,
  derived,
  drawn,
  missing,
  note,
}: {
  /** The API envelope or endpoint the values came from. */
  source: string;
  /** Committed fields read verbatim. */
  fields: string[];
  /** Display-only quantities computed from those fields. */
  derived?: string[];
  /** Rows actually plotted. */
  drawn?: number;
  /** Rows dropped because the value was absent or non-finite. */
  missing?: number;
  /** Any extra repo-truthful caveat. */
  note?: string;
}) {
  return (
    <div className="flex flex-col gap-1 border-t border-cockpit-border/50 pt-2 text-xs text-cockpit-muted">
      <p>
        <span className="uppercase tracking-wider">source</span>{" "}
        <span className="font-mono text-cockpit-text">{source}</span>
      </p>
      <p>
        <span className="uppercase tracking-wider">fields</span>{" "}
        <span className="font-mono text-cockpit-text">{fields.join(", ")}</span>
      </p>
      {derived && derived.length > 0 ? (
        <p>
          <span className="uppercase tracking-wider">derived</span>{" "}
          <span className="font-mono text-cockpit-text">
            {derived.join(", ")}
          </span>{" "}
          (display only)
        </p>
      ) : null}
      {typeof drawn === "number" ? (
        <p>
          <span className="uppercase tracking-wider">rows</span>{" "}
          <span className="font-mono text-cockpit-text">{drawn}</span> drawn
          {typeof missing === "number" && missing > 0 ? (
            <>
              {", "}
              <span className="font-mono text-cockpit-warn">{missing}</span>{" "}
              dropped for absent values (not zero-filled)
            </>
          ) : null}
        </p>
      ) : null}
      {note ? <p>{note}</p> : null}
      <p>
        Descriptive only. This chart ranks nothing, recommends nothing, and
        confers no readiness, promotion, admission, or execution authority.
      </p>
    </div>
  );
}
