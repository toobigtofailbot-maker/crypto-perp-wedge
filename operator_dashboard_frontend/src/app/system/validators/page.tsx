import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

interface ValidationEntry {
  status?: string;
  validation_report_ref?: string;
  validation_report_sha256?: string;
  freshness?: { staleness_status?: string; staleness_reason?: string };
}
interface ProvSub {
  status?: string;
  path?: string;
  sha256?: string;
}
interface HealthData {
  latest_validation?: ValidationEntry;
  data_provenance?: {
    d3_validation_report?: ProvSub;
    d2_import_report?: ProvSub;
  };
}

export default function SystemValidatorsPage() {
  const envelope = fixtures.systemDataHealth();
  const data = envelope.data as HealthData;
  const validation = data.latest_validation ?? {};
  const prov = data.data_provenance ?? {};
  const fresh = validation.freshness ?? {};

  const reports: Array<{ label: string; entry?: ProvSub }> = [
    { label: "D3 validation report", entry: prov.d3_validation_report },
    { label: "D2 import report", entry: prov.d2_import_report },
  ];

  return (
    <>
      <PageHeader
        title="Validators"
        breadcrumb={["System", "Validators"]}
        description="Read-only latest-validation projection. This shell runs no validators."
      />

      <Card>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <CardTitle>Latest validation</CardTitle>
          <Badge tone={toneForStatus(validation.status)}>
            {validation.status ?? "unknown"}
          </Badge>
          {fresh.staleness_status ? (
            <Badge tone={toneForStatus(fresh.staleness_status)}>
              {fresh.staleness_status}
            </Badge>
          ) : null}
        </div>
        {Object.keys(validation).length === 0 ? (
          <EmptyState message="No latest validation record available." />
        ) : (
          <div className="flex flex-col">
            <KeyValue label="Report" value={validation.validation_report_ref ?? "—"} />
            <KeyValue
              label="SHA-256"
              value={validation.validation_report_sha256 ?? "—"}
            />
          </div>
        )}
        {fresh.staleness_reason ? (
          <p className="mt-2 text-xs text-cockpit-muted">{fresh.staleness_reason}</p>
        ) : null}
      </Card>

      <Card>
        <CardTitle>Validator reports</CardTitle>
        <div className="flex flex-col gap-2">
          {reports.map(({ label, entry }) => (
            <div
              key={label}
              className="flex flex-wrap items-center justify-between gap-2 rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2"
            >
              <div className="flex flex-col">
                <span className="text-sm text-cockpit-text">{label}</span>
                {entry?.path ? (
                  <span className="font-mono text-[11px] text-cockpit-muted">
                    {entry.path}
                  </span>
                ) : null}
              </div>
              <Badge tone={toneForStatus(entry?.status)}>
                {entry?.status ?? "—"}
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
