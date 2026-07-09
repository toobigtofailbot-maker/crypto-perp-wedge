import { PageHeader } from "@/components/PageHeader";
import { PlaceholderCard } from "@/components/States";

export default function StrategyReviewReportPage() {
  return (
    <>
      <PageHeader
        title="Strategy Review"
        breadcrumb={["Reports", "Strategy Review"]}
        description="Strategy review report. Scaffold only in this shell."
      />
      <PlaceholderCard title="Strategy review report">
        The strategy review report panel is built by a later dashboard package.
        No review verdicts are fabricated here.
      </PlaceholderCard>
    </>
  );
}
