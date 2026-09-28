"""Framework-neutral CPW research-domain seams."""

from .contracts import (
    LAB_NON_AUTHORITY_FLAGS,
    LOCKED_TIMEFRAMES,
    PREREG_APPROVAL_EXTRA_FALSE_FIELDS,
    PREREG_APPROVAL_REQUIRED_FIELDS,
    PREREG_APPROVAL_SCHEMA_VERSION,
    PREREG_APPROVAL_SCOPE,
    PREREG_APPROVAL_STATEMENT,
    PREREG_NON_AUTHORITY_ASSERTIONS,
    TRIAL_STATUSES,
)
from .formalization import (
    assess_capabilities,
    build_strategy_spec,
    detect_features,
    formalize_reasoned_strategy_draft,
)
from .preregistration import (
    build_approval_marker,
    build_approval_requirement,
    build_approval_template,
    build_preregistration_packet,
    validate_bound_requirement,
    validate_prereg_approval,
)
from .scientific_accounting import (
    build_bridge_ledger_rows,
    compare_result_populations,
    validate_declared_trials,
    validate_trial_denominator,
    validate_variant_denominator,
)

__all__ = [
    "LAB_NON_AUTHORITY_FLAGS",
    "LOCKED_TIMEFRAMES",
    "PREREG_APPROVAL_EXTRA_FALSE_FIELDS",
    "PREREG_APPROVAL_REQUIRED_FIELDS",
    "PREREG_APPROVAL_SCHEMA_VERSION",
    "PREREG_APPROVAL_SCOPE",
    "PREREG_APPROVAL_STATEMENT",
    "PREREG_NON_AUTHORITY_ASSERTIONS",
    "TRIAL_STATUSES",
    "assess_capabilities",
    "build_approval_marker",
    "build_approval_requirement",
    "build_approval_template",
    "build_bridge_ledger_rows",
    "build_preregistration_packet",
    "build_strategy_spec",
    "compare_result_populations",
    "detect_features",
    "formalize_reasoned_strategy_draft",
    "validate_bound_requirement",
    "validate_declared_trials",
    "validate_prereg_approval",
    "validate_trial_denominator",
    "validate_variant_denominator",
]
