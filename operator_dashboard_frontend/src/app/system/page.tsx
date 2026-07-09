import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { toneForStatus } from "@/lib/status";
import { fixtures } from "@/lib/fixtures";

const SECTIONS = [
  { href: "/system/data", label: "Data", note: "Data health and slice facts." },
  { href: "/system/validators", label: "Validators", note: "Latest validation status." },
  { href: "/system/provenance", label: "Provenance", note: "Source artifact inventory." },
  { href: "/system/blockers", label: "Blockers", note: "System blockers (deferred panel)." },
];

interface HealthData {
  status?: string;
  system_posture?: string;
  data_provenance?: { d4_slice?: Record<string, unknown> };
  paper_runtime?: { status?: string };
  live_mode?: { status?: string };
}

export default function SystemPage() {
  const data = fixtures.systemDataHealth().data as HealthData;
  const slice = data.data_provenance?.d4_slice ?? {};
  const gapFacts = (slice.gap_facts as { gap_count?: number } | undefined) ?? {};
  const dupFacts =
    (slice.duplicate_facts as { duplicate_row_count?: number } | undefined) ?? {};

  return (
    <>
      <PageHeader
        title="System / Data"
        breadcrumb={["System"]}
        description="Read-only system and data-health surfaces."
      />

      <Card>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <CardTitle>Health summary</CardTitle>
          <Badge tone={toneForStatus(data.status)}>{data.status ?? "unknown"}</Badge>
          {data.system_posture ? (
            <Badge tone="info">{data.system_posture}</Badge>
          ) : null}
        </div>
        <div className="flex flex-col">
          <KeyValue label="Data slice status" value={String(slice.status ?? "—")} />
          <KeyValue label="Rows" value={String(slice.row_count ?? "—")} />
          <KeyValue label="Gaps" value={String(gapFacts.gap_count ?? "—")} />
          <KeyValue
            label="Duplicate rows"
            value={String(dupFacts.duplicate_row_count ?? "—")}
          />
          <KeyValue
            label="Paper runtime"
            value={data.paper_runtime?.status ?? "—"}
          />
          <KeyValue label="Live mode" value={data.live_mode?.status ?? "—"} />
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
