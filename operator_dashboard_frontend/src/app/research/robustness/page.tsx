import { PageHeader } from "@/components/PageHeader";
import { PlaceholderCard } from "@/components/States";

export default function ResearchRobustnessPage() {
  return (
    <>
      <PageHeader
        title="Robustness"
        breadcrumb={["Research", "Robustness"]}
        description="Robustness overview. Scaffold only in this shell."
      />
      <PlaceholderCard title="Robustness views">
        Monte-Carlo, walk-forward, and robustness heatmap panels are built by a
        later dashboard package. No robustness metrics are fabricated here.
      </PlaceholderCard>
    </>
  );
}
