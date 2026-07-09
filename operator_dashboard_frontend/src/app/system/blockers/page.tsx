import { PageHeader } from "@/components/PageHeader";
import { PlaceholderCard } from "@/components/States";

export default function SystemBlockersPage() {
  return (
    <>
      <PageHeader
        title="System Blockers"
        breadcrumb={["System", "Blockers"]}
        description="System blocker inventory. Scaffold only in this shell."
      />
      <PlaceholderCard title="System blockers">
        The system blocker inventory panel is built by a later dashboard package.
        No blocker data is fabricated here.
      </PlaceholderCard>
    </>
  );
}
