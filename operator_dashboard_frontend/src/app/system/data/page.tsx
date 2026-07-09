import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { fixtures } from "@/lib/fixtures";

export default function SystemDataPage() {
  const envelope = fixtures.systemDataHealth();
  const data = envelope.data as {
    status?: string;
    system_posture?: string;
    latest_data_slice?: Record<string, unknown>;
    warnings?: string[];
  };
  const slice = data.latest_data_slice ?? {};
  const warnings = Array.isArray(data.warnings) ? data.warnings : [];

  return (
    <>
      <PageHeader
        title="Data Health"
        breadcrumb={["System", "Data"]}
        description="Read-only data-health projection over the static dashboard collector."
      />

      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={data.status === "available" ? "good" : "warn"}>
          {data.status ?? "unknown"}
        </Badge>
        {data.system_posture ? <Badge tone="info">{data.system_posture}</Badge> : null}
      </div>

      <Card>
        <CardTitle>Latest data slice</CardTitle>
        {Object.keys(slice).length === 0 ? (
          <EmptyState message="No latest data slice available." />
        ) : (
          <div className="flex flex-col">
            {Object.entries(slice).map(([k, v]) => (
              <KeyValue
                key={k}
                label={k}
                value={
                  v !== null && typeof v === "object"
                    ? JSON.stringify(v)
                    : String(v)
                }
              />
            ))}
          </div>
        )}
      </Card>

      {warnings.length > 0 ? (
        <Card>
          <CardTitle>Warnings</CardTitle>
          <ul className="flex flex-col gap-1 text-sm text-cockpit-warn">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </Card>
      ) : null}

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
