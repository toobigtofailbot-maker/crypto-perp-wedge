import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { Badge, Card, CardTitle, StatCard } from "@/components/ui";
import { CountBars, type CountRow } from "@/components/viz";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

const SECTIONS = [
  { href: "/research/jobs", label: "Jobs", note: "Pipeline queue and run status." },
  {
    href: "/research/result-populations",
    label: "Result Populations",
    note: "Committed result-population summaries.",
  },
  { href: "/research/families", label: "Families", note: "Strategy family grouping (deferred panel)." },
  { href: "/research/blockers", label: "Blockers", note: "Research blockers (deferred panel)." },
  { href: "/research/robustness", label: "Robustness", note: "Robustness views (deferred panel)." },
];

export default function ResearchPage() {
  const summary = fixtures.dashboardSummary().data;
  const counts = summary.counts ?? {};
  const queue = summary.queue_summary ?? {};
  const queueRows: CountRow[] = Object.entries(queue.by_status ?? {}).map(
    ([label, count]) => ({ label, count, tone: toneForStatus(label) }),
  );

  return (
    <>
      <PageHeader
        title="Research Lab"
        breadcrumb={["Research"]}
        description="Read-only research surfaces. Deferred analytical panels are filled by later packages."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Queue Runs" value={counts.queue_runs ?? 0} />
        <StatCard label="Product Runs" value={counts.product_runs ?? 0} />
        <StatCard label="Result Populations" value={counts.result_populations ?? 0} />
        <StatCard label="Strategies" value={counts.strategies ?? 0} />
      </div>

      <Card>
        <div className="mb-3 flex items-center justify-between">
          <CardTitle>Pipeline state distribution</CardTitle>
          <Link
            href="/research/jobs"
            className="text-xs text-cockpit-accent hover:underline"
          >
            View jobs →
          </Link>
        </div>
        {queueRows.length > 0 ? (
          <CountBars rows={queueRows} />
        ) : (
          <p className="text-xs text-cockpit-muted">No queue snapshot.</p>
        )}
        <div className="mt-3 flex flex-wrap gap-2">
          <Badge tone={queue.approval_needed_count ? "warn" : "neutral"}>
            approval needed: {queue.approval_needed_count ?? 0}
          </Badge>
          <Badge tone={queue.blocked_count ? "bad" : "neutral"}>
            blocked: {queue.blocked_count ?? 0}
          </Badge>
          <Badge tone={queue.advisory_packet_ready_count ? "good" : "neutral"}>
            advisory ready: {queue.advisory_packet_ready_count ?? 0}
          </Badge>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {SECTIONS.map((s) => (
          <Link key={s.href} href={s.href}>
            <Card className="h-full transition-colors hover:border-cockpit-accent-dim">
              <CardTitle>{s.label}</CardTitle>
              <p className="text-sm text-cockpit-muted">{s.note}</p>
            </Card>
          </Link>
        ))}
      </div>
    </>
  );
}
