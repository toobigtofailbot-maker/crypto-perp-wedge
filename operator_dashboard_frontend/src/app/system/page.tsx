import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardTitle } from "@/components/ui";

const SECTIONS = [
  { href: "/system/data", label: "Data", note: "Data health and provenance status." },
  { href: "/system/validators", label: "Validators", note: "Latest validation status." },
  { href: "/system/provenance", label: "Provenance", note: "Data provenance detail." },
  { href: "/system/blockers", label: "Blockers", note: "System blockers (deferred panel)." },
];

export default function SystemPage() {
  return (
    <>
      <PageHeader
        title="System / Data"
        breadcrumb={["System"]}
        description="Read-only system and data-health surfaces."
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
