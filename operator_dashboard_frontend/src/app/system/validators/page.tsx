import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Card, CardTitle, KeyValue } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { fixtures } from "@/lib/fixtures";

export default function SystemValidatorsPage() {
  const envelope = fixtures.systemDataHealth();
  const data = envelope.data as {
    latest_validation?: Record<string, unknown>;
  };
  const validation = data.latest_validation ?? {};

  return (
    <>
      <PageHeader
        title="Validators"
        breadcrumb={["System", "Validators"]}
        description="Read-only latest-validation projection. This shell runs no validators."
      />
      <Card>
        <CardTitle>Latest validation</CardTitle>
        {Object.keys(validation).length === 0 ? (
          <EmptyState message="No latest validation record available." />
        ) : (
          <div className="flex flex-col">
            {Object.entries(validation).map(([k, v]) => (
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
