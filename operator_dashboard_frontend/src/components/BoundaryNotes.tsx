/**
 * Surfaces an envelope's warnings, withheld, and unavailable notes as an
 * explicit inline panel. This keeps every data view honest about what is
 * flagged, held back, or absent — rather than only listing keys in the footer.
 */
import type { ApiEnvelope } from "@/lib/types";
import { Card, CardTitle } from "@/components/ui";

function asText(v: unknown): string {
  if (typeof v === "string") return v;
  if (v !== null && typeof v === "object") {
    const message = (v as { message?: unknown }).message;
    if (typeof message === "string") return message;
    const note = (v as { note?: unknown }).note;
    if (typeof note === "string") return note;
    return JSON.stringify(v);
  }
  return String(v);
}

export function BoundaryNotes({
  envelope,
  title = "Warnings, withheld & unavailable",
}: {
  envelope: ApiEnvelope;
  title?: string;
}) {
  const warnings = envelope.warnings ?? [];
  const withheld = Object.entries(envelope.withheld ?? {});
  const unavailable = Object.entries(envelope.unavailable ?? {});

  if (warnings.length === 0 && withheld.length === 0 && unavailable.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardTitle>{title}</CardTitle>
      <div className="flex flex-col gap-3 text-xs">
        {warnings.length > 0 ? (
          <div className="flex flex-col gap-1">
            <span className="font-semibold uppercase tracking-wider text-cockpit-warn">
              Warnings
            </span>
            <ul className="flex flex-col gap-1">
              {warnings.map((w, i) => (
                <li
                  key={i}
                  className="rounded border border-cockpit-warn/30 bg-cockpit-warn/5 px-2 py-1.5 text-cockpit-text"
                >
                  {w}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {withheld.length > 0 ? (
          <div className="flex flex-col gap-1">
            <span className="font-semibold uppercase tracking-wider text-cockpit-muted">
              Withheld
            </span>
            <ul className="flex flex-col gap-1">
              {withheld.map(([k, v]) => (
                <li key={k} className="text-cockpit-muted">
                  <span className="font-mono text-cockpit-text">{k}</span>
                  {" — "}
                  {asText(v)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {unavailable.length > 0 ? (
          <div className="flex flex-col gap-1">
            <span className="font-semibold uppercase tracking-wider text-cockpit-muted">
              Unavailable
            </span>
            <ul className="flex flex-col gap-1">
              {unavailable.map(([k, v]) => (
                <li key={k} className="text-cockpit-muted">
                  <span className="font-mono text-cockpit-text">{k}</span>
                  {" — "}
                  {asText(v)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </Card>
  );
}
