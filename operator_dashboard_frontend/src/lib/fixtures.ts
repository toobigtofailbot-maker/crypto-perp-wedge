/**
 * API-shaped fixture accessors.
 *
 * These JSON files were generated from the merged read-only API
 * (`tools.operator_dashboard_api.app`) via FastAPI TestClient and committed
 * verbatim. The shell renders them so it stays local-first with no runtime,
 * paper, or live contact. Committed repo artifacts remain truth; these
 * fixtures are a derived read-only projection.
 */

import type {
  AgentIntakeSchema,
  ApiEnvelope,
  DashboardSummary,
  ListData,
  ResultPopulationSummary,
  StrategySummary,
} from "@/lib/types";

import dashboardSummary from "@/lib/fixtures/dashboard_summary.json";
import researchJobs from "@/lib/fixtures/research_jobs.json";
import resultPopulations from "@/lib/fixtures/result_populations.json";
import strategies from "@/lib/fixtures/strategies.json";
import candidatesFunnel from "@/lib/fixtures/candidates_funnel.json";
import reportsDaily from "@/lib/fixtures/reports_daily.json";
import reportsWeekly from "@/lib/fixtures/reports_weekly.json";
import systemDataHealth from "@/lib/fixtures/system_data_health.json";
import agentIntakeSchema from "@/lib/fixtures/agent_intake_schema.json";

function asEnvelope<T>(raw: unknown): ApiEnvelope<T> {
  return raw as ApiEnvelope<T>;
}

export const fixtures = {
  dashboardSummary: () => asEnvelope<DashboardSummary>(dashboardSummary),
  researchJobs: () => asEnvelope<Record<string, unknown>>(researchJobs),
  resultPopulations: () =>
    asEnvelope<ListData<ResultPopulationSummary>>(resultPopulations),
  strategies: () => asEnvelope<ListData<StrategySummary>>(strategies),
  candidatesFunnel: () => asEnvelope<Record<string, unknown>>(candidatesFunnel),
  reportsDaily: () => asEnvelope<Record<string, unknown>>(reportsDaily),
  reportsWeekly: () => asEnvelope<Record<string, unknown>>(reportsWeekly),
  systemDataHealth: () => asEnvelope<Record<string, unknown>>(systemDataHealth),
  agentIntakeSchema: () => asEnvelope<AgentIntakeSchema>(agentIntakeSchema),
};
