import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardTitle } from "@/components/ui";

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
  return (
    <>
      <PageHeader
        title="Research Lab"
        breadcrumb={["Research"]}
        description="Read-only research surfaces. Analytical panels are filled by later packages."
      />
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
