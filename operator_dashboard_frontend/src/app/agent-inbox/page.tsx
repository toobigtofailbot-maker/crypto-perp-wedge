import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { fixtures } from "@/lib/fixtures";

export default function AgentInboxPage() {
  const envelope = fixtures.agentIntakeSchema();
  const data = envelope.data;
  const fields = data.future_intake_fields_preview ?? [];

  return (
    <>
      <PageHeader
        title="Agent Inbox"
        breadcrumb={["Agent Inbox"]}
        description="Read-only intake schema preview. Intake writes are a later, separately authorized package."
      />

      <Card className="border-cockpit-warn/40">
        <CardTitle>Intake status</CardTitle>
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="warn">{data.status ?? "unavailable"}</Badge>
            <Badge>{data.schema_status ?? "future_placeholder_only"}</Badge>
          </div>
          <p className="text-sm text-cockpit-muted">{data.reason}</p>
          <div className="flex flex-col">
            <KeyValue
              label="Draft endpoint available"
              value={String(data.draft_endpoint_available ?? false)}
            />
            <KeyValue
              label="Agent Inbox write created"
              value={String(data.agent_inbox_write_created ?? false)}
            />
            <KeyValue
              label="Allowed methods"
              value={(data.allowed_methods ?? ["GET"]).join(", ")}
            />
          </div>
        </div>
      </Card>

      <Card>
        <CardTitle>Intended intake fields (preview only)</CardTitle>
        <p className="mb-3 text-xs text-cockpit-muted">
          These field names are a schema preview. No input is captured, and no
          submit target exists. There is intentionally no form on this page.
        </p>
        <ul className="grid grid-cols-1 gap-1 md:grid-cols-2">
          {fields.map((f) => (
            <li
              key={f}
              className="rounded border border-dashed border-cockpit-border px-3 py-1.5 font-mono text-xs text-cockpit-muted"
            >
              {f}
            </li>
          ))}
        </ul>
      </Card>

      <Card className="bg-cockpit-panel-2">
        <p className="text-xs text-cockpit-muted">
          Boundary: <span className="font-semibold text-cockpit-text">POST
          /api/agent/intake-draft is intentionally not implemented.</span> Any
          scratch-only intake write belongs to a later isolated Agent Inbox
          package and is out of scope for this read-only shell.
        </p>
      </Card>

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
