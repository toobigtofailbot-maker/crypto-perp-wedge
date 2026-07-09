import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Card, CardTitle, KeyValue } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { fixtures } from "@/lib/fixtures";

export default function SystemProvenancePage() {
  const envelope = fixtures.systemDataHealth();
  const data = envelope.data as {
    data_provenance?: Record<string, unknown>;
  };
  const prov = data.data_provenance ?? {};

  return (
    <>
      <PageHeader
        title="Provenance"
        breadcrumb={["System", "Provenance"]}
        description="Read-only data-provenance projection. Committed artifacts remain truth."
      />
      <Card>
        <CardTitle>Data provenance</CardTitle>
        {Object.keys(prov).length === 0 ? (
          <EmptyState message="No data-provenance record available." />
        ) : (
          <div className="flex flex-col">
            {Object.entries(prov).map(([k, v]) => (
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
      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
