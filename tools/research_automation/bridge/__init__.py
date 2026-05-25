"""Local-only AUTO bridge primitives."""

from tools.research_automation.bridge.candidate_artifact import (
    BridgeCandidateArtifactDraft,
    BridgeCandidateArtifactError,
    create_candidate_artifact_draft,
    sha256_draft_payload,
)
from tools.research_automation.bridge.intake import (
    BridgeIntakeError,
    BridgeIntakeRecord,
    BridgeRunContext,
    BridgeSourceRef,
    create_intake_record,
    sha256_bytes,
)
from tools.research_automation.bridge.transform import (
    BridgeNormalizedRecord,
    BridgeTransformError,
    normalize_bridge_payload,
    sha256_json_payload,
)
from tools.research_automation.bridge.validate import (
    BridgeValidationError,
    BridgeValidationIssue,
    BridgeValidationResult,
    assert_valid_normalized_record,
    validate_normalized_record,
)

__all__ = [
    "BridgeCandidateArtifactDraft",
    "BridgeCandidateArtifactError",
    "BridgeIntakeError",
    "BridgeIntakeRecord",
    "BridgeNormalizedRecord",
    "BridgeRunContext",
    "BridgeSourceRef",
    "BridgeTransformError",
    "BridgeValidationError",
    "BridgeValidationIssue",
    "BridgeValidationResult",
    "assert_valid_normalized_record",
    "create_candidate_artifact_draft",
    "create_intake_record",
    "normalize_bridge_payload",
    "sha256_bytes",
    "sha256_draft_payload",
    "sha256_json_payload",
    "validate_normalized_record",
]
