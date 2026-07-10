/**
 * Agent Inbox — the single intake surface of the operator dashboard.
 *
 * Every other route in this dashboard is read-only presentation over committed
 * fixtures. This one route additionally hosts a form, and that form posts to
 * exactly one endpoint on a separate, isolated service
 * (`tools.agent_inbox_intake`) whose only power is to write a noncanonical
 * draft packet into the repo scratch tree.
 *
 * The read-only dashboard API (`tools.operator_dashboard_api`) remains GET-only
 * and is not the write target. Its own intake-schema projection, rendered at the
 * bottom of this page, still declares `agent_inbox_write` unavailable — which is
 * accurate for that API and is not contradicted by the form above.
 */
import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Card, CardTitle, KeyValue } from "@/components/ui";
import { IntakeBoundaryPanel } from "@/components/agent-inbox/IntakeBoundaryPanel";
import { IntakeForm } from "@/components/agent-inbox/IntakeForm";
import {
  AGENT_INBOX_ORIGIN_ENV,
  AGENT_INBOX_PROXY_PATH,
  AGENT_INBOX_UPSTREAM_PATH,
} from "@/lib/agentInboxClient";
import { fixtures } from "@/lib/fixtures";

/**
 * Rendered per request so the intake service origin is read from the
 * environment at run time rather than baked in at build time. An operator can
 * start the service and reload, without rebuilding.
 */
export const dynamic = "force-dynamic";

export default function AgentInboxPage() {
  const envelope = fixtures.agentIntakeSchema();
  const data = envelope.data;
  const serviceOrigin = process.env[AGENT_INBOX_ORIGIN_ENV]?.trim() || null;

  return (
    <>
      <PageHeader
        title="Agent Inbox"
        breadcrumb={["Agent Inbox"]}
        description="Submit an idea to the isolated scratch intake service and review the draft packet it returns. Draft only; human review decides everything after."
      />

      <IntakeBoundaryPanel />

      <IntakeForm
        serviceConfigured={serviceOrigin !== null}
        serviceOrigin={serviceOrigin}
      />

      <Card className="bg-cockpit-panel-2">
        <CardTitle>Two services, one boundary</CardTitle>
        <p className="mb-3 text-sm text-cockpit-muted">
          The form above posts to the isolated Agent Inbox intake service, which
          is a separate application. The read-only dashboard API that supplies
          every other route on this site exposes no write endpoint at all, and
          continues to report the fact below. The browser reaches the intake
          service through a same-origin passthrough, because that service ships
          no CORS headers and this dashboard may not modify it.
        </p>
        <div className="flex flex-col">
          <KeyValue
            label="Dashboard API allowed methods"
            value={(data.allowed_methods ?? ["GET"]).join(", ")}
          />
          <KeyValue
            label="Dashboard API draft endpoint"
            value={String(data.draft_endpoint_available ?? false)}
          />
          <KeyValue
            label="Intake service"
            value="tools.agent_inbox_intake (isolated)"
          />
          <KeyValue
            label="Intake service endpoint"
            value={`POST ${AGENT_INBOX_UPSTREAM_PATH}`}
          />
          <KeyValue
            label="Same-origin passthrough"
            value={`POST ${AGENT_INBOX_PROXY_PATH}`}
          />
          <KeyValue
            label={AGENT_INBOX_ORIGIN_ENV}
            value={serviceOrigin ?? "not set"}
          />
        </div>
      </Card>

      <BoundaryNotes
        envelope={envelope}
        title="Read-only dashboard API: warnings, withheld & unavailable"
      />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
