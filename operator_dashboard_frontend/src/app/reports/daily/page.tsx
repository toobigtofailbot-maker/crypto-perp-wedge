import { PageHeader } from "@/components/PageHeader";
import { ReportView } from "@/components/ReportView";
import { fixtures } from "@/lib/fixtures";

export default function DailyReportPage() {
  const envelope = fixtures.reportsDaily();
  return (
    <>
      <PageHeader
        title="Daily Brief"
        breadcrumb={["Reports", "Daily"]}
        description="Read-only daily-brief projection over committed reporting artifacts."
      />
      <ReportView envelope={envelope} />
    </>
  );
}
