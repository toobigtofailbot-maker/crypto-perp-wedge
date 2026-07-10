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
  CandidatesFunnelData,
  DashboardSummary,
  ListData,
  ResultPopulationDetail,
  ResultPopulationSummary,
  StrategyDetail,
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

// Detail projections of `GET /api/research/result-populations/{id}`, one file
// per committed artifact, captured verbatim from the same unchanged API. These
// carry the per-variant `metrics` block that the list endpoint does not project.
import rp2134 from "@/lib/fixtures/result_populations/RP-2134.json";
import rp2592 from "@/lib/fixtures/result_populations/RP-2592.json";
import rp3731 from "@/lib/fixtures/result_populations/RP-3731.json";
import rp4492 from "@/lib/fixtures/result_populations/RP-4492.json";
import rp6236 from "@/lib/fixtures/result_populations/RP-6236.json";
import rp6688 from "@/lib/fixtures/result_populations/RP-6688.json";
import rp7134 from "@/lib/fixtures/result_populations/RP-7134.json";
import rp7520 from "@/lib/fixtures/result_populations/RP-7520.json";

// Detail projections of `GET /api/strategies/{id}`, one file per committed
// strategy spec, captured verbatim from the same unchanged API. These carry the
// spec body — provenance, logic, free parameters, review — that the list
// endpoint does not project.
import strat0001 from "@/lib/fixtures/strategies/STRAT-SPEC-0001.json";
import strat0002 from "@/lib/fixtures/strategies/STRAT-SPEC-0002.json";
import strat0003 from "@/lib/fixtures/strategies/STRAT-SPEC-0003.json";
import strat0004 from "@/lib/fixtures/strategies/STRAT-SPEC-0004.json";
import strat0005 from "@/lib/fixtures/strategies/STRAT-SPEC-0005.json";
import strat0006 from "@/lib/fixtures/strategies/STRAT-SPEC-0006.json";

function asEnvelope<T>(raw: unknown): ApiEnvelope<T> {
  return raw as ApiEnvelope<T>;
}

const RESULT_POPULATION_DETAILS: readonly unknown[] = [
  rp2134,
  rp2592,
  rp3731,
  rp4492,
  rp6236,
  rp6688,
  rp7134,
  rp7520,
];

const STRATEGY_DETAILS: readonly unknown[] = [
  strat0001,
  strat0002,
  strat0003,
  strat0004,
  strat0005,
  strat0006,
];

export const fixtures = {
  dashboardSummary: () => asEnvelope<DashboardSummary>(dashboardSummary),
  researchJobs: () => asEnvelope<Record<string, unknown>>(researchJobs),
  resultPopulations: () =>
    asEnvelope<ListData<ResultPopulationSummary>>(resultPopulations),
  strategies: () => asEnvelope<ListData<StrategySummary>>(strategies),
  candidatesFunnel: () => asEnvelope<CandidatesFunnelData>(candidatesFunnel),
  reportsDaily: () => asEnvelope<Record<string, unknown>>(reportsDaily),
  reportsWeekly: () => asEnvelope<Record<string, unknown>>(reportsWeekly),
  systemDataHealth: () => asEnvelope<Record<string, unknown>>(systemDataHealth),
  agentIntakeSchema: () => asEnvelope<AgentIntakeSchema>(agentIntakeSchema),

  /** Every committed result-population detail envelope, in artifact-id order. */
  resultPopulationDetails: (): ApiEnvelope<ResultPopulationDetail>[] =>
    RESULT_POPULATION_DETAILS.map((raw) =>
      asEnvelope<ResultPopulationDetail>(raw),
    ),

  /** A single detail envelope, or undefined when no such artifact is committed. */
  resultPopulationDetail: (
    id: string,
  ): ApiEnvelope<ResultPopulationDetail> | undefined =>
    fixtures
      .resultPopulationDetails()
      .find((e) => e.data.result_population_id === id),

  /** Every committed strategy-spec detail envelope, in artifact-id order. */
  strategyDetails: (): ApiEnvelope<StrategyDetail>[] =>
    STRATEGY_DETAILS.map((raw) => asEnvelope<StrategyDetail>(raw)),

  /**
   * A single strategy detail envelope, or undefined when no such artifact is
   * committed. The live API answers an unknown id with an `unavailable`
   * envelope rather than a 404; callers render that absence, not an error.
   */
  strategyDetail: (id: string): ApiEnvelope<StrategyDetail> | undefined =>
    fixtures.strategyDetails().find((e) => e.data.strategy_id === id),
};
