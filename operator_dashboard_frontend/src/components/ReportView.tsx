/**
 * Compact read-only renderer for a report envelope
 * (tools.lab_reporting.report_model.build_report_data). Shows headline counts
 * and which report sections are present. Full charting is withheld by the API
 * and rendered by a later panel package.
 */
import type { ApiEnvelope } from "@/lib/types";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle, KeyValue, StatCard } from "@/components/ui";
import { EmptyState } from "@/components/States";

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

export function ReportView({ envelope }: { envelope: ApiEnvelope<ReportData> }) {
  const data = envelope.data;
  const report = data.report ?? {};
  const counts = (report.counts as Record<string, unknown> | undefined) ?? {};
  // Report counts mix scalar headline totals with nested breakdown groups
  // (e.g. by_overall_state). Render scalars as stat tiles and nested groups as
  // key/value rows so no object is passed to React as a child.
  const scalarCounts = Object.entries(counts).filter(
    ([, v]) => typeof v === "number" || typeof v === "string",
  ) as Array<[string, number | string]>;
  const groupCounts = Object.entries(counts).filter(
    ([, v]) => v !== null && typeof v === "object",
  ) as Array<[string, Record<string, unknown>]>;

  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="info">{data.report_kind ?? "report"}</Badge>
        <Badge tone={data.status === "available" ? "good" : "warn"}>
          {data.status ?? "unknown"}
        </Badge>
        <span className="text-xs text-cockpit-muted">
          charting withheld by API
        </span>
      </div>

      {scalarCounts.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {scalarCounts.map(([k, v]) => (
            <StatCard key={k} label={k} value={v} />
          ))}
        </div>
      ) : null}

      {groupCounts.map(([groupKey, group]) => (
        <Card key={groupKey}>
          <CardTitle>{groupKey}</CardTitle>
          <div className="flex flex-col">
            {Object.entries(group).map(([k, v]) => (
              <KeyValue
                key={k}
                label={k}
                value={
                  v !== null && typeof v === "object"
                    ? JSON.stringify(v)
                    : String(v)
                }
              />
            ))}
          </div>
        </Card>
      ))}

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

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
