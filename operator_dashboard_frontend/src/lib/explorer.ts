/**
 * Display-only derivations for the Strategy Explorer.
 *
 * Everything here reads values the read-only API already projected and reshapes
 * them for presentation: it counts, joins, formats, and checks one committed
 * number against another. It never invents a metric, fills an absent value, or
 * infers a parameter assignment that no artifact records.
 *
 * A strategy spec is a planning artifact. Nothing in this module ranks,
 * recommends, approves, or asserts readiness.
 */

import type {
  ApiEnvelope,
  ResultPopulationDetail,
  SpecCondition,
  SpecFreeParameters,
  SpecLogicGroup,
  SpecOperand,
} from "@/lib/types";

/* ------------------------------------------------------------------ *
 * Strategy-spec condition grammar
 * ------------------------------------------------------------------ */

/**
 * Committed comparison operators, rendered as symbols where a symbol is exact
 * and as words where it is not. An unknown operator is shown verbatim rather
 * than guessed at.
 */
const OPERATOR_LABEL: Record<string, string> = {
  lt: "<",
  lte: "≤",
  gt: ">",
  gte: "≥",
  crosses_above: "crosses above",
  crosses_below: "crosses below",
};

export function operatorLabel(operator: string | null | undefined): string {
  if (!operator) return "?";
  return OPERATOR_LABEL[operator] ?? operator;
}

/** Render a committed lookback as `(20)` or `(fast_lookback_bars)`. */
function lookbackLabel(lookback: SpecOperand["lookback"]): string {
  if (!lookback) return "";
  if (typeof lookback.bars === "number") return `(${lookback.bars})`;
  if (lookback.bars_parameter_ref) return `(${lookback.bars_parameter_ref})`;
  return "";
}

/**
 * Render one committed operand as text.
 *
 * `composed_operand` is expanded structurally, exactly as the spec declares it —
 * a `z_score` shows its value, center, and scale operands rather than being
 * collapsed into a symbol the artifact never wrote.
 */
export function formatOperand(operand: SpecOperand | null | undefined): string {
  if (!operand) return "—";

  switch (operand.operand_type) {
    case "constant":
      return String(operand.ref ?? "—");

    case "parameter_ref":
      return String(operand.ref ?? "—");

    case "data_ref":
    case "indicator_ref": {
      const name = String(operand.ref ?? "—");
      return `${name}${lookbackLabel(operand.lookback)}`;
    }

    case "composed_operand": {
      switch (operand.composition_type) {
        case "scale_by_one_minus_parameter":
          return `${formatOperand(operand.base_operand)} × (1 − ${formatOperand(operand.parameter_operand)})`;
        case "scale_by_one_plus_parameter":
          return `${formatOperand(operand.base_operand)} × (1 + ${formatOperand(operand.parameter_operand)})`;
        case "z_score":
          return `z_score(value=${formatOperand(operand.value_operand)}, center=${formatOperand(operand.center_operand)}, scale=${formatOperand(operand.scale_operand)})`;
        default:
          return `${operand.composition_type ?? "composed"}(…)`;
      }
    }

    default:
      return String(operand.ref ?? operand.operand_type ?? "—");
  }
}

/** Render a committed condition as `left <op> right`. */
export function formatCondition(condition: SpecCondition): string {
  return [
    formatOperand(condition.left_operand),
    operatorLabel(condition.operator),
    formatOperand(condition.right_operand),
  ].join(" ");
}

/** Flatten a group tree into `[group, depth]` pairs, preserving order. */
export function flattenGroups(
  groups: SpecLogicGroup[] | undefined,
  depth = 0,
): Array<{ group: SpecLogicGroup; depth: number }> {
  const out: Array<{ group: SpecLogicGroup; depth: number }> = [];
  for (const group of groups ?? []) {
    out.push({ group, depth });
    out.push(...flattenGroups(group.subgroups, depth + 1));
  }
  return out;
}

/** Total committed conditions across a group tree. */
export function conditionCount(groups: SpecLogicGroup[] | undefined): number {
  return flattenGroups(groups).reduce(
    (total, { group }) => total + (group.conditions?.length ?? 0),
    0,
  );
}

/* ------------------------------------------------------------------ *
 * Free parameters
 * ------------------------------------------------------------------ */

/**
 * Count the committed free-parameter entries.
 *
 * This is a derived display value, not the API's `free_parameter_count` — that
 * field reads `free_parameters.count`, which committed specs do not carry, so
 * the API projects `null` for every spec. The count below follows the spec's
 * own `counting_rule`: `parameters` holds only `is_free_parameter=true` entries.
 * Callers must label it as derived.
 */
export function derivedFreeParameterCount(
  freeParameters: SpecFreeParameters | undefined,
): number {
  return (freeParameters?.parameters ?? []).filter(
    (p) => p.is_free_parameter !== false,
  ).length;
}

/* ------------------------------------------------------------------ *
 * Evidence linkage and denominator reconciliation
 * ------------------------------------------------------------------ */

/** One committed reconciliation check, and whether the artifact satisfies it. */
export interface ReconciliationCheck {
  label: string;
  /** `null` when a side of the comparison is absent — never coerced to false. */
  holds: boolean | null;
  detail: string;
}

export interface LinkedPopulation {
  result_population_id: string;
  path: string | null;
  committed_denominator: number | null;
  result_row_count: number | null;
  /** Variant rows the API actually projected. */
  projected_row_count: number;
  outcome_counts: Record<string, number>;
  validator_status: string | null;
  review_status: string | null;
  execution_mode: string | null;
  offline_only: boolean | null;
  variant_manifest_id: string | null;
  sweep_plan_id: string | null;
  checks: ReconciliationCheck[];
}

function numberOrNull(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

/**
 * Compare two committed counts. Absent on either side yields `null` (unknown),
 * which renders as "not projected" — never as a passing or failing check.
 */
function compareCounts(
  label: string,
  left: number | null,
  right: number | null,
  leftName: string,
  rightName: string,
): ReconciliationCheck {
  if (left === null || right === null) {
    return {
      label,
      holds: null,
      detail: `${leftName}=${left ?? "—"} · ${rightName}=${right ?? "—"}`,
    };
  }
  return {
    label,
    holds: left === right,
    detail: `${leftName}=${left} · ${rightName}=${right}`,
  };
}

/**
 * Project one linked result population into the Explorer's evidence view,
 * including the denominator reconciliation the artifact itself asserts.
 */
export function linkedPopulation(
  envelope: ApiEnvelope<ResultPopulationDetail>,
): LinkedPopulation {
  const rp = envelope.data;
  const rawCounts = rp.outcome_counts ?? {};

  const denominator = numberOrNull(rp.committed_denominator);
  const rowCount = numberOrNull(rp.result_row_count);
  const projected = (rp.variant_result_rows ?? []).length;
  const countsSum = numberOrNull(rawCounts.counts_sum);

  // The artifact's own assertion. Absent means unknown, not false.
  const committedFlag = rawCounts.counts_sum_equals_committed_denominator;
  const assertedEqual = typeof committedFlag === "boolean" ? committedFlag : null;

  const outcome_counts: Record<string, number> = {};
  for (const [key, value] of Object.entries(rawCounts)) {
    if (typeof value === "number") outcome_counts[key] = value;
  }

  const checks: ReconciliationCheck[] = [
    compareCounts(
      "Rows match denominator",
      rowCount,
      denominator,
      "result_row_count",
      "committed_denominator",
    ),
    compareCounts(
      "Projected rows match row count",
      projected,
      rowCount,
      "variant_result_rows",
      "result_row_count",
    ),
    compareCounts(
      "Outcome counts sum to denominator",
      countsSum,
      denominator,
      "counts_sum",
      "committed_denominator",
    ),
    {
      label: "Artifact asserts counts_sum = denominator",
      holds: assertedEqual,
      detail: `outcome_counts.counts_sum_equals_committed_denominator=${
        assertedEqual === null ? "—" : assertedEqual
      }`,
    },
  ];

  return {
    result_population_id: rp.result_population_id ?? "—",
    path: rp.path ?? null,
    committed_denominator: denominator,
    result_row_count: rowCount,
    projected_row_count: projected,
    outcome_counts,
    validator_status: rp.validator_status ?? null,
    review_status: rp.review_status ?? null,
    execution_mode: rp.execution_mode ?? null,
    offline_only: rp.offline_only ?? null,
    variant_manifest_id: rp.variant_manifest_id ?? null,
    sweep_plan_id: rp.sweep_plan_id ?? null,
    checks,
  };
}

/** Committed result populations whose lineage names this strategy spec. */
export function populationsForStrategy(
  envelopes: ApiEnvelope<ResultPopulationDetail>[],
  strategyId: string,
): ApiEnvelope<ResultPopulationDetail>[] {
  return envelopes.filter((e) => e.data.parent_strategy_spec_id === strategyId);
}

/** What evidence exists for a spec, for an at-a-glance indicator on the list. */
export interface EvidenceAvailability {
  population_count: number;
  variant_row_count: number;
  /** True when at least one linked population projects at least one variant row. */
  has_variant_rows: boolean;
}

export function evidenceForStrategy(
  envelopes: ApiEnvelope<ResultPopulationDetail>[],
  strategyId: string,
): EvidenceAvailability {
  const linked = populationsForStrategy(envelopes, strategyId);
  const variant_row_count = linked.reduce(
    (total, e) => total + (e.data.variant_result_rows ?? []).length,
    0,
  );
  return {
    population_count: linked.length,
    variant_row_count,
    has_variant_rows: variant_row_count > 0,
  };
}

/* ------------------------------------------------------------------ *
 * Formatting
 * ------------------------------------------------------------------ */

/** Render an absent value as an em dash rather than as `null` or `0`. */
export function orDash(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  return String(value);
}

/** Shorten a `sha256:...` digest for display, keeping it recognisable. */
export function shortHash(hash: string | null | undefined, keep = 12): string {
  if (!hash) return "—";
  const [prefix, digest] = hash.includes(":")
    ? [hash.slice(0, hash.indexOf(":")), hash.slice(hash.indexOf(":") + 1)]
    : ["", hash];
  if (digest.length <= keep) return hash;
  const head = `${digest.slice(0, keep)}…`;
  return prefix ? `${prefix}:${head}` : head;
}
