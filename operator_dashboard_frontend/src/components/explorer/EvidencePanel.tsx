/**
 * Result-population linkage and denominator reconciliation for a strategy spec.
 *
 * The reconciliation checks compare committed numbers against each other. They
 * assert nothing about whether the evidence is sufficient, favourable, or
 * approved — a passing check means two committed counts agree, and nothing more.
 * A check whose inputs are absent renders as unknown, never as passing.
 */
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import {
  Cell,
  DataTable,
  FieldNote,
  Row,
} from "@/components/explorer/primitives";
import { OUTCOME_META } from "@/lib/status";
import { orDash, shortHash } from "@/lib/explorer";
import type { LinkedPopulation, ReconciliationCheck } from "@/lib/explorer";

function CheckBadge({ holds }: { holds: boolean | null }) {
  if (holds === null) return <Badge tone="neutral">not projected</Badge>;
  return holds ? (
    <Badge tone="good">consistent</Badge>
  ) : (
    <Badge tone="bad">mismatch</Badge>
  );
}

function ChecksList({ checks }: { checks: ReconciliationCheck[] }) {
  return (
    <ul className="flex flex-col gap-1.5">
      {checks.map((check) => (
        <li
          key={check.label}
          className="flex flex-wrap items-center justify-between gap-2 rounded border border-cockpit-border/60 bg-cockpit-panel-2 px-2 py-1.5 text-xs"
        >
          <span className="text-cockpit-text">{check.label}</span>
          <span className="flex min-w-0 flex-wrap items-center gap-2">
            <span className="break-all font-mono text-cockpit-muted">
              {check.detail}
            </span>
            <CheckBadge holds={check.holds} />
          </span>
        </li>
      ))}
    </ul>
  );
}

function OutcomeCounts({ counts }: { counts: Record<string, number> }) {
  const buckets = Object.entries(counts).filter(([key]) => !OUTCOME_META.has(key));
  if (buckets.length === 0) {
    return (
      <p className="text-xs text-cockpit-muted">
        No outcome buckets are projected for this population.
      </p>
    );
  }
  return (
    <div className="flex flex-wrap gap-1.5">
      {buckets.map(([bucket, count]) => (
        <span
          key={bucket}
          className="inline-flex items-center gap-1.5 rounded border border-cockpit-border bg-cockpit-panel-2 px-2 py-0.5 text-xs"
        >
          <span className="font-mono text-cockpit-muted">{bucket}</span>
          <span className="font-mono text-cockpit-text">{count}</span>
        </span>
      ))}
    </div>
  );
}

function PopulationCard({ population }: { population: LinkedPopulation }) {
  return (
    <Card className="bg-cockpit-panel-2">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <CardTitle>{population.result_population_id}</CardTitle>
        <div className="mb-3 flex flex-wrap gap-2">
          {population.validator_status ? (
            <Badge
              tone={population.validator_status === "passed" ? "good" : "warn"}
            >
              validator: {population.validator_status}
            </Badge>
          ) : null}
          {population.review_status ? (
            <Badge tone="warn">review: {population.review_status}</Badge>
          ) : null}
          {population.offline_only ? (
            <Badge tone="neutral">offline only</Badge>
          ) : null}
        </div>
      </div>

      <div className="flex flex-col">
        <KeyValue
          label="Committed denominator"
          value={orDash(population.committed_denominator)}
        />
        <KeyValue
          label="Result row count"
          value={orDash(population.result_row_count)}
        />
        <KeyValue
          label="Variant rows projected"
          value={population.projected_row_count}
        />
        <KeyValue
          label="Execution mode"
          value={orDash(population.execution_mode)}
        />
        <KeyValue
          label="Variant manifest"
          value={orDash(population.variant_manifest_id)}
        />
        <KeyValue label="Sweep plan" value={orDash(population.sweep_plan_id)} />
      </div>

      <div className="mt-3 flex flex-col gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Outcome distribution
        </span>
        <OutcomeCounts counts={population.outcome_counts} />
      </div>

      <div className="mt-3 flex flex-col gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Denominator reconciliation
        </span>
        <ChecksList checks={population.checks} />
      </div>

      {population.path ? (
        <p className="mt-3 font-mono text-xs text-cockpit-muted">
          {population.path}
        </p>
      ) : null}
    </Card>
  );
}

export function EvidencePanel({
  populations,
  identityHashes,
}: {
  populations: LinkedPopulation[];
  /** `{result_population_id, result_population_identity_hash, input_identity_hash}` */
  identityHashes: Array<{
    id: string;
    result_population_identity_hash: string | null;
    input_identity_hash: string | null;
  }>;
}) {
  const totalDenominator = populations.reduce(
    (total, p) => total + (p.committed_denominator ?? 0),
    0,
  );
  const totalRows = populations.reduce((total, p) => total + p.projected_row_count, 0);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="info">
          {populations.length} linked result population
          {populations.length === 1 ? "" : "s"}
        </Badge>
        <Badge tone="neutral">{totalDenominator} committed denominator</Badge>
        <Badge tone="neutral">{totalRows} variant rows</Badge>
      </div>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        {populations.map((population) => (
          <PopulationCard
            key={population.result_population_id}
            population={population}
          />
        ))}
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Identity hashes
        </span>
        <DataTable
          columns={[
            "result_population_id",
            "result_population_identity_hash",
            "input_identity_hash",
          ]}
        >
          {identityHashes.map((entry) => (
            <Row key={entry.id}>
              <Cell mono>{entry.id}</Cell>
              <Cell mono muted>
                {shortHash(entry.result_population_identity_hash)}
              </Cell>
              <Cell mono muted>
                {shortHash(entry.input_identity_hash)}
              </Cell>
            </Row>
          ))}
        </DataTable>
      </div>

      <FieldNote
        source="GET /api/research/result-populations/{id}"
        fields={[
          "parent_strategy_spec_id",
          "committed_denominator",
          "result_row_count",
          "outcome_counts",
          "validator_status",
          "review_status",
          "execution_mode",
          "result_population_identity_hash",
          "input_identity_hash",
        ]}
        note="A consistent check means two committed counts agree. It is not a quality, readiness, or approval signal. Linkage is by lineage.strategy_spec_id only."
      />
    </div>
  );
}
