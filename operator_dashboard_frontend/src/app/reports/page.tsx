import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardTitle } from "@/components/ui";

const REPORTS = [
  { href: "/reports/daily", label: "Daily brief", note: "Operator daily brief projection." },
  { href: "/reports/weekly", label: "Weekly report", note: "Operator weekly report projection." },
  {
    href: "/reports/strategy-review",
    label: "Strategy review",
    note: "Strategy review report (deferred panel).",
  },
  { href: "/reports/main", label: "Main report", note: "Consolidated main report (deferred panel)." },
];

export default function ReportsPage() {
  return (
    <>
      <PageHeader
        title="Reports"
        breadcrumb={["Reports"]}
        description="Read-only report projections. Committed count blocks are charted here; each report's own embedded charting stays withheld, and statistics the reports name as withheld (PSR, DSR, MinTRL) are never drawn."
      />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {REPORTS.map((r) => (
          <Link key={r.href} href={r.href}>
            <Card className="h-full transition-colors hover:border-cockpit-accent-dim">
              <CardTitle>{r.label}</CardTitle>
              <p className="text-sm text-cockpit-muted">{r.note}</p>
            </Card>
          </Link>
        ))}
      </div>
    </>
  );
}
