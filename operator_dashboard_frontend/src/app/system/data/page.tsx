import { PageHeader } from "@/components/PageHeader";
import { ProvenanceFooter } from "@/components/ProvenanceFooter";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { EmptyState } from "@/components/States";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

interface Freshness {
  staleness_status?: string;
  staleness_reason?: string;
}
interface D4Slice {
  status?: string;
  dataset_id?: string;
  venue?: string;
  symbol?: string;
  market_type?: string;
  timeframe?: string;
  row_count?: number;
  expected_row_count?: number;
  timestamp_range?: { start_utc?: string; end_utc?: string };
  gap_facts?: { gap_count?: number; missing_bar_count?: number };
  duplicate_facts?: { duplicate_group_count?: number; duplicate_row_count?: number };
  freshness?: Freshness;
}
interface HealthData {
  status?: string;
  system_posture?: string;
  data_provenance?: { d4_slice?: D4Slice };
  paper_runtime?: { status?: string; message?: string };
  live_mode?: { status?: string; message?: string };
  warnings?: unknown[];
}

const warningText = (w: unknown): string => {
  if (typeof w === "string") return w;
  if (w !== null && typeof w === "object") {
    const message = (w as { message?: unknown }).message;
    return typeof message === "string" ? message : JSON.stringify(w);
  }
  return String(w);
};

export default function SystemDataPage() {
  const envelope = fixtures.systemDataHealth();
  const data = envelope.data as HealthData;
  const slice = data.data_provenance?.d4_slice ?? {};
  const gap = slice.gap_facts ?? {};
  const dup = slice.duplicate_facts ?? {};
  const fresh = slice.freshness ?? {};
  const range = slice.timestamp_range ?? {};
  const warnings = Array.isArray(data.warnings) ? data.warnings : [];
  const rowsMatch = slice.row_count === slice.expected_row_count;

  return (
    <>
      <PageHeader
        title="Data Health"
        breadcrumb={["System", "Data"]}
        description="Read-only data-health projection over the static dashboard collector."
      />

      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={toneForStatus(data.status)}>{data.status ?? "unknown"}</Badge>
        {data.system_posture ? <Badge tone="info">{data.system_posture}</Badge> : null}
        {fresh.staleness_status ? (
          <Badge tone={toneForStatus(fresh.staleness_status)}>
            {fresh.staleness_status}
          </Badge>
        ) : null}
      </div>

      <Card>
        <CardTitle>Committed data slice</CardTitle>
        {Object.keys(slice).length === 0 ? (
          <EmptyState message="No committed data slice available." />
        ) : (
          <div className="flex flex-col">
            <KeyValue label="Dataset" value={slice.dataset_id ?? "—"} />
            <KeyValue
              label="Venue / symbol"
              value={`${slice.venue ?? "—"} · ${slice.symbol ?? "—"}`}
            />
            <KeyValue label="Market type" value={slice.market_type ?? "—"} />
            <KeyValue label="Timeframe" value={slice.timeframe ?? "—"} />
            <KeyValue
              label="Rows / expected"
              value={`${slice.row_count ?? "—"} / ${slice.expected_row_count ?? "—"}`}
            />
            <KeyValue
              label="Range"
              value={`${range.start_utc ?? "—"} → ${range.end_utc ?? "—"}`}
            />
          </div>
        )}
        <div className="mt-3 flex flex-wrap gap-2 text-xs">
          <Badge tone={rowsMatch ? "good" : "warn"}>
            rows {rowsMatch ? "match expected" : "differ from expected"}
          </Badge>
          <Badge tone={(gap.gap_count ?? 0) === 0 ? "good" : "warn"}>
            gaps: {gap.gap_count ?? "—"}
          </Badge>
          <Badge tone={(dup.duplicate_row_count ?? 0) === 0 ? "good" : "warn"}>
            duplicates: {dup.duplicate_row_count ?? "—"}
          </Badge>
        </div>
        {fresh.staleness_reason ? (
          <p className="mt-2 text-xs text-cockpit-muted">
            {fresh.staleness_reason}
          </p>
        ) : null}
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>Paper runtime</CardTitle>
          <Badge tone={toneForStatus(data.paper_runtime?.status)}>
            {data.paper_runtime?.status ?? "unknown"}
          </Badge>
          <p className="mt-2 text-xs text-cockpit-muted">
            {data.paper_runtime?.message ?? "No paper runtime."}
          </p>
        </Card>
        <Card>
          <CardTitle>Live mode</CardTitle>
          <Badge tone={toneForStatus(data.live_mode?.status)}>
            {data.live_mode?.status ?? "unknown"}
          </Badge>
          <p className="mt-2 text-xs text-cockpit-muted">
            {data.live_mode?.message ?? "No live mode."}
          </p>
        </Card>
      </div>

      {warnings.length > 0 ? (
        <Card>
          <CardTitle>Warnings</CardTitle>
          <ul className="flex flex-col gap-1 text-sm text-cockpit-warn">
            {warnings.map((w, i) => (
              <li key={i}>{warningText(w)}</li>
            ))}
          </ul>
        </Card>
      ) : null}

      <ProvenanceFooter envelope={envelope} />
    </>
  );
}
