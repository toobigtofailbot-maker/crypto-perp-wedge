import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { fixtures } from "@/lib/fixtures";

export default function ResultPopulationsPage() {
  const envelope = fixtures.resultPopulations();
  const items = envelope.data.items ?? [];

  return (
    <>
      <PageHeader
        title="Result Populations"
        breadcrumb={["Research", "Result Populations"]}
        description="Committed result-population summaries. Per-trade distributions are withheld; only committed fields are projected."
      />

      <Card>
        <CardTitle>Populations ({envelope.data.count ?? items.length})</CardTitle>
        {items.length === 0 ? (
          <EmptyState message="No committed result populations found." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-b border-cockpit-border text-left text-xs uppercase tracking-wider text-cockpit-muted">
                  <th className="py-2 pr-3">ID</th>
                  <th className="py-2 pr-3">Strategy Spec</th>
                  <th className="py-2 pr-3">Rows</th>
                  <th className="py-2 pr-3">Validator</th>
                  <th className="py-2 pr-3">Review</th>
                </tr>
              </thead>
              <tbody>
                {items.map((rp) => (
                  <tr
                    key={rp.result_population_id}
                    className="border-b border-cockpit-border/50"
                  >
                    <td className="py-2 pr-3 font-mono text-xs">
                      {rp.result_population_id}
                    </td>
                    <td className="py-2 pr-3 font-mono text-xs text-cockpit-muted">
                      {rp.parent_strategy_spec_id ?? "—"}
                    </td>
                    <td className="py-2 pr-3 font-mono">
                      {rp.result_row_count ?? "—"}
                    </td>
                    <td className="py-2 pr-3">
                      <Badge tone={rp.validator_status === "PASS" ? "good" : "neutral"}>
                        {rp.validator_status ?? "—"}
                      </Badge>
                    </td>
                    <td className="py-2 pr-3 text-xs text-cockpit-muted">
                      {rp.review_status ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
