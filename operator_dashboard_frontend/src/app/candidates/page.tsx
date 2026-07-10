import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, StatCard } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { ChartCard } from "@/components/charts/ChartCard";
import { ChartProvenanceNote } from "@/components/charts/ChartProvenanceNote";
import {
  CategoricalCountChart,
  type CategoryBar,
} from "@/components/charts/CategoricalCountChart";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

export default function CandidatesPage() {
  const envelope = fixtures.candidatesFunnel();
  const data = envelope.data;
  const reg = data.candidate_registry ?? {};
  const funnel = data.product_candidate_funnel;

  const statusBars: CategoryBar[] = Object.entries(reg.by_status ?? {}).map(
    ([label, count]) => ({ label, count, tone: toneForStatus(label) }),
  );
  const verdictBars: CategoryBar[] = Object.entries(
    reg.by_overall_verdict ?? {},
  ).map(([label, count]) => ({ label, count, tone: toneForStatus(label) }));
  // Stage order is the committed display order from the API, preserved as-is.
  const funnelBars: CategoryBar[] = (funnel?.stages ?? []).map((s) => ({
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

      {funnelBars.length > 0 ? (
        <ChartCard
          title="Product candidate funnel"
          subtitle="Committed stage counts in committed display order. Stage order implies no promotion, admission, or ranking authority."
          footer={
            <>
              {funnel?.note ? (
                <p className="mb-3 text-xs text-cockpit-muted">{funnel.note}</p>
              ) : null}
              <ChartProvenanceNote
                source="GET /api/candidates/funnel"
                fields={["product_candidate_funnel.stages[].label", "…stages[].count"]}
                drawn={funnelBars.length}
                note="Full denominator is shown; this is not a winner-only view."
              />
            </>
          }
        >
          <CategoricalCountChart
            bars={funnelBars}
            horizontal
            ariaLabel={`Funnel bar chart across ${funnelBars.length} committed stages`}
          />
        </ChartCard>
      ) : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {statusBars.length > 0 ? (
          <ChartCard
            title="Registry by status"
            footer={
              <ChartProvenanceNote
                source="GET /api/candidates/funnel"
                fields={["candidate_registry.by_status"]}
                drawn={statusBars.length}
              />
            }
          >
            <CategoricalCountChart
              bars={statusBars}
              horizontal
              ariaLabel={`Bar chart of candidate registry counts across ${statusBars.length} statuses`}
            />
          </ChartCard>
        ) : (
          <Card>
            <CardTitle>Registry by status</CardTitle>
            <EmptyState message="No status breakdown available." />
          </Card>
        )}

        {verdictBars.length > 0 ? (
          <ChartCard
            title="Registry by overall verdict"
            footer={
              <ChartProvenanceNote
                source="GET /api/candidates/funnel"
                fields={["candidate_registry.by_overall_verdict"]}
                drawn={verdictBars.length}
                note="Verdicts are read from the committed registry; this surface issues none."
              />
            }
          >
            <CategoricalCountChart
              bars={verdictBars}
              horizontal
              ariaLabel={`Bar chart of candidate registry counts across ${verdictBars.length} overall verdicts`}
            />
          </ChartCard>
        ) : (
          <Card>
            <CardTitle>Registry by overall verdict</CardTitle>
            <EmptyState message="No verdict breakdown available." />
          </Card>
        )}
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
