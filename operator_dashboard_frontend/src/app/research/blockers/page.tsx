import { PageHeader } from "@/components/PageHeader";
import { PlaceholderCard } from "@/components/States";

export default function ResearchBlockersPage() {
  return (
    <>
      <PageHeader
        title="Research Blockers"
        breadcrumb={["Research", "Blockers"]}
        description="Blocker inventory view. Scaffold only in this shell."
      />
      <PlaceholderCard title="Blockers">
        The research blocker inventory and triage panel is built by a later
        dashboard package over the read-only API. No blocker data is fabricated
        here.
      </PlaceholderCard>
    </>
  );
}
