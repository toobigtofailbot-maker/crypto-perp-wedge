/**
 * Renders an API envelope's source, provenance, warnings, withheld, and
 * unavailable fields so every projection stays honest about where it came from
 * and what it is not.
 */
import type { ApiEnvelope } from "@/lib/types";
import { Card, CardTitle } from "@/components/ui";

export function ProvenanceFooter({ envelope }: { envelope: ApiEnvelope }) {
  const withheldKeys = Object.keys(envelope.withheld ?? {});
  const unavailableKeys = Object.keys(envelope.unavailable ?? {});

  return (
    <Card className="bg-cockpit-panel-2">
      <CardTitle>Provenance &amp; boundary</CardTitle>
      <dl className="flex flex-col gap-2 text-xs text-cockpit-muted">
        <div>
          <dt className="inline font-semibold text-cockpit-text">Source: </dt>
          <dd className="inline">{envelope.source}</dd>
        </div>
        <div>
          <dt className="inline font-semibold text-cockpit-text">
            Schema: {" "}
          </dt>
          <dd className="inline font-mono">{envelope.schema_version}</dd>
        </div>
        {envelope.provenance.length > 0 ? (
          <div>
            <dt className="font-semibold text-cockpit-text">Artifacts</dt>
            <dd>
              <ul className="mt-1 flex flex-col gap-0.5">
                {envelope.provenance.map((p, i) => (
                  <li key={`${p.path}-${i}`} className="font-mono">
                    {p.path}
                    <span className="text-cockpit-muted"> · {p.role}</span>
                  </li>
                ))}
              </ul>
            </dd>
          </div>
        ) : null}
        {envelope.warnings.length > 0 ? (
          <div>
            <dt className="font-semibold text-cockpit-warn">Warnings</dt>
            <dd>
              <ul className="mt-1 flex flex-col gap-0.5">
                {envelope.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </dd>
          </div>
        ) : null}
        {withheldKeys.length > 0 ? (
          <div>
            <dt className="inline font-semibold text-cockpit-text">
              Withheld:{" "}
            </dt>
            <dd className="inline">{withheldKeys.join(", ")}</dd>
          </div>
        ) : null}
        {unavailableKeys.length > 0 ? (
          <div>
            <dt className="inline font-semibold text-cockpit-text">
              Unavailable:{" "}
            </dt>
            <dd className="inline">{unavailableKeys.join(", ")}</dd>
          </div>
        ) : null}
      </dl>
    </Card>
  );
}
