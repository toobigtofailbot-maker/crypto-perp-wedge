/**
 * Compact read-only renderer for a report envelope
 * (tools.lab_reporting.report_model.build_report_data). Shows headline counts,
 * the overall-state distribution, section sizes, withheld statistics, and
 * caveats. Full charting is withheld by the API and is not fabricated here.
 */
import type { ApiEnvelope } from "@/lib/types";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { BoundaryNotes } from "@/components/BoundaryNotes";
import { Badge, Card, CardTitle, KeyValue, StatCard } from "@/components/ui";
import { CountBars, type CountRow } from "@/components/viz";
import { EmptyState } from "@/components/States";
import { toneForStatus } from "@/lib/status";

interface ReportData {
  status?: string;
  report_kind?: string;
  report?: Record<string, unknown>;
}

const SECTION_KEYS = [
  "completed_runs",
  "blocked_runs",
  "no_gos",
  "open_decision_surfaces",
  "validation_status",
  "candidate_review_readiness",
  "artifact_links",
  "caveats",
];

function asStringArray(v: unknown): string[] {
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string") : [];
}

export function ReportView({ envelope }: { envelope: ApiEnvelope<ReportData> }) {
  const data = envelope.data;
  const report = data.report ?? {};
  const counts = (report.counts as Record<string, unknown> | undefined) ?? {};

  // Report counts mix scalar headline totals with nested breakdown groups
  // (e.g. by_overall_state). Render scalars as stat tiles and the by_state
  // group as a distribution bar; other nested groups as key/value rows.
  const scalarCounts = Object.entries(counts).filter(
    ([, v]) => typeof v === "number" || typeof v === "string",
  ) as Array<[string, number | string]>;
  const groupCounts = Object.entries(counts).filter(
    ([, v]) => v !== null && typeof v === "object",
  ) as Array<[string, Record<string, unknown>]>;

  const withheldStats = asStringArray(report.withheld_statistics);
  const caveats = asStringArray(report.caveats);
  const edgeSearchHold =
    typeof report.edge_search_hold === "string" ? report.edge_search_hold : null;
  const charting = report.charting as
    | { enabled?: boolean; note?: string }
    | undefined;

  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="info">{data.report_kind ?? "report"}</Badge>
        <Badge tone={toneForStatus(data.status)}>
          {data.status ?? "unknown"}
        </Badge>
        <Badge tone="neutral">descriptive only · no notifications fired</Badge>
      </div>

      {scalarCounts.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {scalarCounts.map(([k, v]) => (
            <StatCard key={k} label={k} value={v} />
          ))}
        </div>
      ) : null}

      {groupCounts.map(([groupKey, group]) => {
        const numericRows = Object.entries(group).filter(
          ([, v]) => typeof v === "number",
        ) as Array<[string, number]>;
        if (numericRows.length > 0) {
          const rows: CountRow[] = numericRows.map(([label, count]) => ({
            label,
            count,
            tone: toneForStatus(label),
          }));
          return (
            <Card key={groupKey}>
              <CardTitle>{groupKey}</CardTitle>
              <CountBars rows={rows} hideZero />
            </Card>
          );
        }
        return (
          <Card key={groupKey}>
            <CardTitle>{groupKey}</CardTitle>
            <div className="flex flex-col">
              {Object.entries(group).map(([k, v]) => (
                <KeyValue key={k} label={k} value={String(v)} />
              ))}
            </div>
          </Card>
        );
      })}

      <Card>
        <CardTitle>Sections present</CardTitle>
        {SECTION_KEYS.some((k) => k in report) ? (
          <div className="flex flex-col">
            {SECTION_KEYS.filter((k) => k in report).map((k) => {
              const v = report[k];
              const size = Array.isArray(v)
                ? `${v.length} item(s)`
                : v && typeof v === "object"
                  ? `${Object.keys(v).length} field(s)`
                  : String(v);
              return <KeyValue key={k} label={k} value={size} />;
            })}
          </div>
        ) : (
          <EmptyState message="No report sections present." />
        )}
      </Card>

      {edgeSearchHold ? (
        <Card className="border-cockpit-warn/40">
          <CardTitle>Edge-search hold</CardTitle>
          <p className="text-sm text-cockpit-muted">{edgeSearchHold}</p>
        </Card>
      ) : null}

      {withheldStats.length > 0 ? (
        <Card>
          <CardTitle>Withheld statistics</CardTitle>
          <div className="flex flex-wrap gap-2">
            {withheldStats.map((s) => (
              <Badge key={s} tone="neutral">
                {s}
              </Badge>
            ))}
          </div>
          <p className="mt-2 text-xs text-cockpit-muted">
            Shown explicitly rather than fabricated.
          </p>
        </Card>
      ) : null}

      {caveats.length > 0 ? (
        <Card className="bg-cockpit-panel-2">
          <CardTitle>Caveats</CardTitle>
          <ul className="flex list-disc flex-col gap-1 pl-5 text-xs text-cockpit-muted">
            {caveats.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </Card>
      ) : null}

      {charting && charting.enabled === false ? (
        <p className="text-xs text-cockpit-muted">
          Charting withheld by API: {charting.note ?? "table-based output only."}
        </p>
      ) : null}

      <BoundaryNotes envelope={envelope} />

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
