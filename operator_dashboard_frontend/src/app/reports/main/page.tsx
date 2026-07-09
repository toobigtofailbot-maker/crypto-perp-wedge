import { PageHeader } from "@/components/PageHeader";
import { PlaceholderCard } from "@/components/States";

export default function MainReportPage() {
  return (
    <>
      <PageHeader
        title="Main Report"
        breadcrumb={["Reports", "Main"]}
        description="Consolidated main report. Scaffold only in this shell."
      />
      <PlaceholderCard title="Main report">
        The consolidated main report panel is built by a later dashboard package.
      </PlaceholderCard>
    </>
  );
}
