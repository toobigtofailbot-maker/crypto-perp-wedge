import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Card, CardTitle, KeyValue, StatCard } from "@/components/ui";
import { fixtures } from "@/lib/fixtures";

export default function CandidatesPage() {
  const envelope = fixtures.candidatesFunnel();
  const data = envelope.data as {
    candidate_registry?: {
      registered_count?: number;
      by_status?: Record<string, number>;
      by_overall_verdict?: Record<string, number>;
      admitted_candidate_count?: number;
      paper_live_built?: boolean;
    };
    note?: string;
  };
  const reg = data.candidate_registry ?? {};

  return (
    <>
      <PageHeader
        title="Candidate Funnel"
        breadcrumb={["Candidates"]}
        description="Read-only candidate registry rollup. This shell admits, crosses, and promotes nothing."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <StatCard label="Registered" value={reg.registered_count ?? 0} />
        <StatCard
          label="Admitted"
          value={reg.admitted_candidate_count ?? 0}
          hint="No admission is implied"
        />
        <StatCard
          label="Paper/Live built"
          value={String(reg.paper_live_built ?? false)}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>By status</CardTitle>
          <div className="flex flex-col">
            {Object.entries(reg.by_status ?? {}).map(([k, v]) => (
              <KeyValue key={k} label={k} value={v} />
            ))}
          </div>
        </Card>
        <Card>
          <CardTitle>By overall verdict</CardTitle>
          <div className="flex flex-col">
            {Object.entries(reg.by_overall_verdict ?? {}).map(([k, v]) => (
              <KeyValue key={k} label={k} value={v} />
            ))}
          </div>
        </Card>
      </div>

      {data.note ? (
        <Card className="bg-cockpit-panel-2">
          <p className="text-xs text-cockpit-muted">{data.note}</p>
        </Card>
      ) : null}

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
