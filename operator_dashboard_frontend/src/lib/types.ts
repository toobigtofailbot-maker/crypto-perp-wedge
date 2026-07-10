/**
 * TypeScript mirrors of the read-only operator dashboard API envelope
 * (`tools/operator_dashboard_api/models.py`). These describe the shape the
 * shell reads; they confer no write capability.
 */

export interface ProvenanceRef {
  path: string;
  role: string;
  note?: string | null;
  sha256?: string | null;
}

export interface ApiEnvelope<T = unknown> {
  schema_version: string;
  source: string;
  provenance: ProvenanceRef[];
  authority: Record<string, unknown>;
  warnings: string[];
  withheld: Record<string, unknown>;
  unavailable: Record<string, unknown>;
  data: T;
}

/** A projected item that carries an availability status from the API. */
export interface Statused {
  status?: string;
}

export interface QueueSummary {
  run_count?: number;
  by_status?: Record<string, number>;
  approval_needed_count?: number;
  blocked_count?: number;
  failed_count?: number;
  advisory_packet_ready_count?: number;
}

export interface ProductRunSummary {
  run_count?: number;
  advisory_packet_ready?: number;
  blocked_or_failed?: number;
  real_runner_runs?: number;
}

export interface DashboardSummary extends Statused {
  system_posture?: string;
  counts?: Record<string, number>;
  queue_summary?: QueueSummary;
  product_run_summary?: ProductRunSummary;
  paper_trading?: PaperLiveState;
  live_trading?: PaperLiveState;
}

export interface PaperLiveState {
  status?: string;
  reason?: string;
  capability_built?: boolean;
}

export interface StrategySummary {
  strategy_id?: string;
  strategy_spec_id?: string | null;
  path?: string | null;
  title?: string | null;
  short_name?: string | null;
  status?: string | null;
  source_type?: string | null;
  instrument_family?: string | null;
  market_type?: string | null;
  primary_timeframe?: string | null;
  direction?: string | null;
  /**
   * Projected from `free_parameters.count`, which committed specs do not carry;
   * it is therefore `null` on every spec. The real parameters are in
   * `StrategyDetail.free_parameters.parameters`.
   */
  free_parameter_count?: number | null;
  max_free_parameters?: number | null;
  /**
   * Projected from `review.review_scope`, which committed specs do not carry;
   * it is therefore `null` on every spec. The real value is
   * `StrategyDetail.review.approval_scope`.
   */
  approval_scope?: string | null;
  not_executable?: boolean | null;
}

/** A leaf or composed operand inside a committed strategy-spec condition. */
export interface SpecOperand {
  operand_type?: string | null;
  /** For `constant` this holds the literal value, not a name. */
  ref?: string | number | null;
  field?: string | null;
  timeframe?: string | null;
  lookback?: {
    bars?: number | null;
    bars_parameter_ref?: string | null;
  } | null;
  // `composed_operand` only.
  composition_type?: string | null;
  base_operand?: SpecOperand | null;
  parameter_operand?: SpecOperand | null;
  value_operand?: SpecOperand | null;
  center_operand?: SpecOperand | null;
  scale_operand?: SpecOperand | null;
  zero_scale_policy?: string | null;
}

export interface SpecCondition {
  condition_id?: string | null;
  condition_role?: string | null;
  left_operand?: SpecOperand | null;
  operator?: string | null;
  right_operand?: SpecOperand | null;
  units?: string | null;
  notes?: string | null;
}

export interface SpecLogicGroup {
  group_id?: string | null;
  group_role?: string | null;
  logic?: string | null;
  side?: string | null;
  conditions?: SpecCondition[];
  subgroups?: SpecLogicGroup[];
  notes?: string | null;
}

export interface SpecEntryLogic {
  direction?: string | null;
  groups?: SpecLogicGroup[];
  notes?: string | null;
}

export interface SpecExitLogic {
  groups?: SpecLogicGroup[];
  max_holding_period?: { enabled?: boolean | null; bars?: number | null } | null;
  notes?: string | null;
}

export interface SpecFilters {
  groups?: SpecLogicGroup[];
  none_declared?: boolean | null;
}

/** One declared free parameter. Values here are the swept space, not an assignment. */
export interface SpecFreeParameter {
  name?: string | null;
  label?: string | null;
  description?: string | null;
  type?: string | null;
  units?: string | null;
  default?: number | string | null;
  range?: {
    min?: number | null;
    max?: number | null;
    step?: number | null;
    inclusive_min?: boolean | null;
    inclusive_max?: boolean | null;
  } | null;
  allowed_values?: Array<number | string> | null;
  is_free_parameter?: boolean | null;
  included_in_variant_generation?: boolean | null;
  role?: string | null;
  rationale?: string | null;
  constraints?: string[] | null;
}

export interface SpecFreeParameters {
  max_free_parameters?: number | null;
  counting_rule?: string | null;
  parameters?: SpecFreeParameter[];
  no_free_parameters_declared?: boolean | null;
}

export interface SpecHostDataRef {
  stream?: string | null;
  timeframe?: string | null;
  field?: string | null;
  availability?: string | null;
}

export interface SpecTimeframeAndData {
  primary_timeframe?: string | null;
  confirmation_timeframes?: string[] | null;
  host_data_refs?: SpecHostDataRef[];
  gap_handling_assumption?: string | null;
  missing_data_blockers?: string[] | null;
}

export interface SpecProvenance {
  source_type?: string | null;
  source_refs?: string[] | null;
  prepared_by?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  rationale?: string | null;
  source_constraints?: string[] | null;
  unresolved_claims?: string[] | null;
}

export interface SpecReview {
  human_review_required?: boolean | null;
  reviewer?: string | null;
  reviewed_at?: string | null;
  review_notes?: string[] | null;
  approval_scope?: string | null;
  non_authority_acknowledgement?: Record<string, boolean>;
}

/**
 * Detail projection for one committed strategy spec, from
 * `GET /api/strategies/{id}`.
 *
 * A strategy spec is a planning artifact. It is not executable, not a
 * candidate, not approved for anything beyond variant planning, and carries no
 * performance claim. `status` on this projection is the *envelope* status
 * (`available` / `unavailable`), not the spec's lifecycle status — the reader
 * overwrites it. Lifecycle status survives only on `GET /api/strategies`.
 */
export interface StrategyDetail extends StrategySummary {
  provenance?: SpecProvenance;
  non_execution_declaration?: Record<string, boolean>;
  timeframe_and_data?: SpecTimeframeAndData;
  entry_logic?: SpecEntryLogic;
  exit_logic?: SpecExitLogic;
  filters?: SpecFilters;
  free_parameters?: SpecFreeParameters;
  review?: SpecReview;
}

export interface ResultPopulationSummary {
  result_population_id?: string;
  path?: string | null;
  parent_strategy_spec_id?: string | null;
  committed_denominator?: number | null;
  result_row_count?: number | null;
  outcome_counts?: Record<string, number | boolean>;
  validator_status?: string | null;
  review_status?: string | null;
  execution_mode?: string | null;
  offline_only?: boolean | null;
  no_runtime_contact?: boolean | null;
  no_paper_live_contact?: boolean | null;
}

export interface ListData<T> extends Statused {
  count?: number;
  items?: T[];
}

/**
 * Per-variant metrics as committed in a result-population artifact and
 * projected verbatim by `GET /api/research/result-populations/{id}`.
 *
 * These are offline research backtest outputs. They are not performance
 * claims, rankings, readiness signals, or candidate authority. Any field may
 * be absent; absent means absent and is never substituted with zero.
 */
export interface VariantMetrics {
  drawdown?: number | null;
  exposure?: number | null;
  fees?: number | null;
  funding?: number | null;
  pnl?: number | null;
  return_pct?: number | null;
  sharpe?: number | null;
  slippage?: number | null;
  trade_count?: number | null;
  win_rate?: number | null;
}

export interface VariantResultRow {
  variant_id?: string | null;
  row_id?: string | null;
  outcome_category?: string | null;
  attempted?: boolean | null;
  metrics?: VariantMetrics;
  non_success?: Record<string, unknown>;
  error?: Record<string, unknown>;
}

/** Detail projection for a single committed result population. */
export interface ResultPopulationDetail extends ResultPopulationSummary, Statused {
  variant_manifest_id?: string | null;
  sweep_plan_id?: string | null;
  result_population_identity_hash?: string | null;
  input_identity_hash?: string | null;
  append_only_ledger?: Record<string, unknown>;
  /**
   * Committed coverage block. Kept open-ended, like
   * `backtest_assumption_summary`: consumers render whatever keys the artifact
   * carries rather than a subset fixed here.
   */
  data_coverage_summary?: Record<string, unknown>;
  backtest_assumption_summary?: Record<string, unknown>;
  error_summary?: Record<string, unknown>;
  non_authority_declaration?: Record<string, unknown>;
  review?: Record<string, unknown>;
  variant_result_rows?: VariantResultRow[];
}

export interface CandidateRegistryRollup {
  registered_count?: number;
  by_status?: Record<string, number>;
  by_overall_verdict?: Record<string, number>;
  admitted_candidate_count?: number;
  paper_live_built?: boolean;
}

export interface FunnelStage {
  stage?: string;
  label?: string;
  count?: number;
}

export interface ProductCandidateFunnel {
  available?: boolean;
  candidate_admitted_count?: number;
  winner_only_view?: boolean;
  note?: string;
  stages?: FunnelStage[];
}

export interface CandidatesFunnelData extends Statused {
  candidate_registry?: CandidateRegistryRollup;
  product_candidate_funnel?: ProductCandidateFunnel;
  note?: string;
}

export interface AgentIntakeSchema extends Statused {
  schema_status?: string;
  draft_endpoint_available?: boolean;
  agent_inbox_write_created?: boolean;
  allowed_methods?: string[];
  future_intake_fields_preview?: string[];
  reason?: string;
}
