import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, StatCard } from "@/components/ui";
import { CountBars, Funnel, type CountRow, type FunnelStageRow } from "@/components/viz";
import { EmptyState } from "@/components/States";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

export default function CandidatesPage() {
  const envelope = fixtures.candidatesFunnel();
  const data = envelope.data;
  const reg = data.candidate_registry ?? {};
  const funnel = data.product_candidate_funnel;

  const statusRows: CountRow[] = Object.entries(reg.by_status ?? {}).map(
    ([label, count]) => ({ label, count, tone: toneForStatus(label) }),
  );
  const verdictRows: CountRow[] = Object.entries(reg.by_overall_verdict ?? {}).map(
    ([label, count]) => ({ label, count, tone: toneForStatus(label) }),
  );
  const funnelRows: FunnelStageRow[] = (funnel?.stages ?? []).map((s) => ({
    label: s.label ?? s.stage ?? "stage",
    count: s.count ?? 0,
    tone: s.stage === "candidate_admitted" ? "warn" : "info",
  }));

  return (
    <>
      <PageHeader
        title="Candidate Funnel"
        breadcrumb={["Candidates"]}
        description="Read-only candidate registry rollup and product funnel. This shell admits, crosses, and promotes nothing."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Registered" value={reg.registered_count ?? 0} />
        <StatCard
          label="Admitted"
          value={reg.admitted_candidate_count ?? 0}
          hint="No admission is implied"
        />
        <StatCard
          label="Winner-only view"
          value={String(funnel?.winner_only_view ?? false)}
          hint="full denominator shown"
        />
        <StatCard
          label="Paper/Live built"
          value={String(reg.paper_live_built ?? false)}
        />
      </div>

      {funnelRows.length > 0 ? (
        <Card>
          <CardTitle>Product candidate funnel</CardTitle>
          <Funnel stages={funnelRows} />
          {funnel?.note ? (
            <p className="mt-3 text-xs text-cockpit-muted">{funnel.note}</p>
          ) : null}
        </Card>
      ) : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>Registry by status</CardTitle>
          {statusRows.length > 0 ? (
            <CountBars rows={statusRows} />
          ) : (
            <EmptyState message="No status breakdown available." />
          )}
        </Card>
        <Card>
          <CardTitle>Registry by overall verdict</CardTitle>
          {verdictRows.length > 0 ? (
            <CountBars rows={verdictRows} />
          ) : (
            <EmptyState message="No verdict breakdown available." />
          )}
        </Card>
      </div>

      <Card className="border-cockpit-warn/40">
        <CardTitle>Paper / live authority</CardTitle>
        <div className="flex flex-col gap-2">
          <Badge tone="warn">unavailable</Badge>
          <p className="text-sm text-cockpit-muted">
            No paper/live capability is built by this dashboard. This surface has
            no crossing, promotion, admission, or readiness authority — stage
            order is committed display order only.
          </p>
        </div>
      </Card>

      {data.note ? (
        <Card className="bg-cockpit-panel-2">
          <p className="text-xs text-cockpit-muted">{data.note}</p>
        </Card>
      ) : null}

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
