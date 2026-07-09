import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Card, CardTitle, KeyValue } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { fixtures } from "@/lib/fixtures";

export default function ResearchJobsPage() {
  const envelope = fixtures.researchJobs();
  const data = envelope.data as {
    summary?: Record<string, unknown>;
    runs?: Array<Record<string, unknown>>;
  };
  const summary = data.summary ?? {};
  const runs = Array.isArray(data.runs) ? data.runs : [];

  const fmt = (v: unknown): string =>
    v !== null && typeof v === "object" ? JSON.stringify(v) : String(v);

  return (
    <>
      <PageHeader
        title="Research Jobs"
        breadcrumb={["Research", "Jobs"]}
        description="Read-only pipeline queue and run status. Notification fields are dry-run preview metadata only."
      />

      <Card>
        <CardTitle>Queue summary</CardTitle>
        <div className="flex flex-col">
          {Object.keys(summary).length === 0 ? (
            <EmptyState message="No queue summary available." />
          ) : (
            Object.entries(summary).map(([k, v]) => (
              <KeyValue key={k} label={k} value={fmt(v)} />
            ))
          )}
        </div>
      </Card>

      <Card>
        <CardTitle>Runs ({runs.length})</CardTitle>
        {runs.length === 0 ? (
          <EmptyState message="No runs in the committed queue snapshot." />
        ) : (
          <ul className="flex flex-col gap-2">
            {runs.slice(0, 25).map((run, i) => (
              <li
                key={i}
                className="rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2 font-mono text-xs text-cockpit-text"
              >
                {String(run.pipeline_run_id ?? `run-${i}`)}
                <span className="text-cockpit-muted">
                  {" "}
                  · {String(run.symbol ?? "")} {String(run.timeframe ?? "")} ·{" "}
                  {String(run.status ?? "unknown")}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
