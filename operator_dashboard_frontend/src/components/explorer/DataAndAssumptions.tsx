/**
 * What data the spec requires, and what the linked offline backtests assumed.
 *
 * The assumption table lists one column per linked result population, so two
 * populations that assumed different things are visibly different rather than
 * silently merged.
 */
import { Badge } from "@/components/ui";
import {
  Cell,
  DataTable,
  FieldNote,
  NoteList,
  Row,
} from "@/components/explorer/primitives";
import { orDash } from "@/lib/explorer";
import type { SpecTimeframeAndData } from "@/lib/types";

export function DataRequirements({
  timeframeAndData,
}: {
  timeframeAndData: SpecTimeframeAndData | undefined;
}) {
  const refs = timeframeAndData?.host_data_refs ?? [];
  const confirmations = timeframeAndData?.confirmation_timeframes ?? [];
  const blockers = timeframeAndData?.missing_data_blockers ?? [];

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        {timeframeAndData?.primary_timeframe ? (
          <Badge tone="info">
            primary: {timeframeAndData.primary_timeframe}
          </Badge>
        ) : null}
        <Badge tone="neutral">
          {confirmations.length} confirmation timeframe
          {confirmations.length === 1 ? "" : "s"}
        </Badge>
        <Badge tone={blockers.length > 0 ? "bad" : "neutral"}>
          {blockers.length} missing-data blocker
          {blockers.length === 1 ? "" : "s"}
        </Badge>
      </div>

      {refs.length === 0 ? (
        <p className="text-xs text-cockpit-muted">
          The spec declares no host data references.
        </p>
      ) : (
        <DataTable columns={["stream", "timeframe", "field", "availability"]}>
          {refs.map((ref, index) => (
            <Row key={`${ref.stream}-${ref.field}-${index}`}>
              <Cell mono>{orDash(ref.stream)}</Cell>
              <Cell mono muted>
                {orDash(ref.timeframe)}
              </Cell>
              <Cell mono>{orDash(ref.field)}</Cell>
              <Cell muted>{orDash(ref.availability)}</Cell>
            </Row>
          ))}
        </DataTable>
      )}

      {timeframeAndData?.gap_handling_assumption ? (
        <p className="text-xs text-cockpit-muted">
          <span className="uppercase tracking-wider">gap handling</span>{" "}
          {timeframeAndData.gap_handling_assumption}
        </p>
      ) : null}

      <NoteList
        items={blockers}
        emptyLabel="No missing-data blocker is declared."
        tone="warn"
      />

      <FieldNote
        source="GET /api/strategies/{id}"
        fields={[
          "timeframe_and_data.primary_timeframe",
          "timeframe_and_data.confirmation_timeframes[]",
          "timeframe_and_data.host_data_refs[]",
          "timeframe_and_data.gap_handling_assumption",
          "timeframe_and_data.missing_data_blockers[]",
        ]}
      />
    </div>
  );
}

/** One linked population's committed assumption and coverage blocks. */
export interface PopulationAssumptions {
  id: string;
  backtest_assumption_summary: Record<string, unknown>;
  data_coverage_summary: Record<string, unknown>;
}

function cellText(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (Array.isArray(value)) return value.length > 0 ? value.join("; ") : "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

/** Union of keys across populations, so a key missing on one still shows. */
function unionKeys(records: Array<Record<string, unknown>>): string[] {
  const keys = new Set<string>();
  for (const record of records) {
    for (const key of Object.keys(record)) keys.add(key);
  }
  return [...keys].sort();
}

export function AssumptionsPanel({
  populations,
}: {
  populations: PopulationAssumptions[];
}) {
  if (populations.length === 0) {
    return (
      <p className="text-xs text-cockpit-muted">
        No linked result population projects a backtest assumption block.
      </p>
    );
  }

  const assumptionKeys = unionKeys(
    populations.map((p) => p.backtest_assumption_summary),
  );
  const coverageKeys = unionKeys(populations.map((p) => p.data_coverage_summary));
  const columns = ["field", ...populations.map((p) => p.id)];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Backtest assumptions
        </span>
        <DataTable columns={columns}>
          {assumptionKeys.map((key) => (
            <Row key={key}>
              <Cell mono muted>
                {key}
              </Cell>
              {populations.map((population) => (
                <Cell key={population.id} mono>
                  {cellText(population.backtest_assumption_summary[key])}
                </Cell>
              ))}
            </Row>
          ))}
        </DataTable>
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Data coverage
        </span>
        <DataTable columns={columns}>
          {coverageKeys.map((key) => (
            <Row key={key}>
              <Cell mono muted>
                {key}
              </Cell>
              {populations.map((population) => (
                <Cell key={population.id} mono>
                  {cellText(population.data_coverage_summary[key])}
                </Cell>
              ))}
            </Row>
          ))}
        </DataTable>
      </div>

      <FieldNote
        source="GET /api/research/result-populations/{id}"
        fields={["backtest_assumption_summary", "data_coverage_summary"]}
        note="One column per linked population. Assumptions record what an offline backtest presumed; they are not exchange, broker, or live-execution guarantees."
      />
    </div>
  );
}
