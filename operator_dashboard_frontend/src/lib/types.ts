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
  title?: string | null;
  short_name?: string | null;
  status?: string | null;
  source_type?: string | null;
  instrument_family?: string | null;
  market_type?: string | null;
  primary_timeframe?: string | null;
  direction?: string | null;
  free_parameter_count?: number | null;
  max_free_parameters?: number | null;
  approval_scope?: string | null;
  not_executable?: boolean | null;
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
  data_coverage_summary?: {
    data_catalog_ref?: string | null;
    data_coverage_notes?: string[];
    data_slice_identity?: string | null;
  };
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
