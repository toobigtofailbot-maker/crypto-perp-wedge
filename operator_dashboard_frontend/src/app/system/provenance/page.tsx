import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

interface ArtifactPath {
  artifact_id?: string;
  artifact_type?: string;
  path?: string;
  sha256?: string;
}
interface DataProvenance {
  status?: string;
  source_refs?: string[];
  artifact_paths?: ArtifactPath[];
  freshness?: { staleness_status?: string; staleness_reason?: string };
}

export default function SystemProvenancePage() {
  const envelope = fixtures.systemDataHealth();
  const data = envelope.data as { data_provenance?: DataProvenance };
  const prov = data.data_provenance ?? {};
  const artifacts = prov.artifact_paths ?? [];
  const sourceRefs = prov.source_refs ?? [];
  const fresh = prov.freshness ?? {};

  return (
    <>
      <PageHeader
        title="Provenance"
        breadcrumb={["System", "Provenance"]}
        description="Read-only data-provenance projection. Committed artifacts remain truth."
      />

      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={toneForStatus(prov.status)}>{prov.status ?? "unknown"}</Badge>
        {fresh.staleness_status ? (
          <Badge tone={toneForStatus(fresh.staleness_status)}>
            {fresh.staleness_status}
          </Badge>
        ) : null}
        {sourceRefs.map((r) => (
          <Badge key={r}>{r}</Badge>
        ))}
      </div>

      <Card>
        <CardTitle>Source artifact inventory ({artifacts.length})</CardTitle>
        {artifacts.length === 0 ? (
          <EmptyState message="No provenance artifacts available." />
        ) : (
          <ul className="flex flex-col gap-2">
            {artifacts.map((a, i) => (
              <li
                key={a.artifact_id ?? i}
                className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-mono text-xs text-cockpit-heading">
                    {a.artifact_id ?? "—"}
                  </span>
                  {a.artifact_type ? (
                    <Badge tone="info">{a.artifact_type}</Badge>
                  ) : null}
                </div>
                {a.path ? (
                  <p className="mt-1 break-all font-mono text-[11px] text-cockpit-muted">
                    {a.path}
                  </p>
                ) : null}
                {a.sha256 ? (
                  <p className="break-all font-mono text-[11px] text-cockpit-muted">
                    sha256: {a.sha256}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Card>

      {fresh.staleness_reason ? (
        <Card className="bg-cockpit-panel-2">
          <KeyValue label="Freshness" value={fresh.staleness_reason} />
        </Card>
      ) : null}

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
