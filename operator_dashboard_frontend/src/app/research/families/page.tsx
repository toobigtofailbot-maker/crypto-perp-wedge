import { PageHeader } from "@/components/PageHeader";
import { PlaceholderCard } from "@/components/States";

export default function ResearchFamiliesPage() {
  return (
    <>
      <PageHeader
        title="Strategy Families"
        breadcrumb={["Research", "Families"]}
        description="Family grouping view. Scaffold only in this shell."
      />
      <PlaceholderCard title="Family grouping">
        Strategy-family grouping and cross-family comparison panels are built by a
        later dashboard package. No family data is fabricated here.
      </PlaceholderCard>
    </>
  );
}
