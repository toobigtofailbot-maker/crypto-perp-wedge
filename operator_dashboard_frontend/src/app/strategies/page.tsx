import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { fixtures } from "@/lib/fixtures";

export default function StrategiesPage() {
  const envelope = fixtures.strategies();
  const items = envelope.data.items ?? [];

  return (
    <>
      <PageHeader
        title="Strategies"
        breadcrumb={["Strategies"]}
        description="Committed strategy-spec summaries. Strategy specs are planning artifacts and are not executable."
      />

      <Card>
        <CardTitle>Strategy specs ({envelope.data.count ?? items.length})</CardTitle>
        {items.length === 0 ? (
          <EmptyState message="No committed strategy specs found." />
        ) : (
          <ul className="flex flex-col gap-2">
            {items.map((s) => (
              <li key={s.strategy_id}>
                <Link
                  href={`/strategies/${encodeURIComponent(s.strategy_id ?? "")}`}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-cockpit-border bg-cockpit-panel-2 px-3 py-2 transition-colors hover:border-cockpit-accent-dim">
                    <div className="flex flex-col">
                      <span className="text-sm text-cockpit-heading">
                        {s.title ?? s.short_name ?? s.strategy_id}
                      </span>
                      <span className="font-mono text-xs text-cockpit-muted">
                        {s.strategy_id}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {s.primary_timeframe ? (
                        <Badge>{s.primary_timeframe}</Badge>
                      ) : null}
                      {s.status ? <Badge tone="info">{s.status}</Badge> : null}
                      {s.not_executable ? (
                        <Badge tone="warn">not executable</Badge>
                      ) : null}
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
