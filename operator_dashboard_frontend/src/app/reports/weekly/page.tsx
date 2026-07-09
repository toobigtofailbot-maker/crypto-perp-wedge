import { PageHeader } from "@/components/PageHeader";
import { ReportView } from "@/components/ReportView";
import { fixtures } from "@/lib/fixtures";

export default function WeeklyReportPage() {
  const envelope = fixtures.reportsWeekly();
  return (
    <>
      <PageHeader
        title="Weekly Report"
        breadcrumb={["Reports", "Weekly"]}
        description="Read-only weekly-report projection over committed reporting artifacts."
      />
      <ReportView envelope={envelope} />
    </>
  );
}
