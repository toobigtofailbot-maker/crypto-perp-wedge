"""Local-only AUTO bridge primitives."""

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

__all__ = [
    "BridgeIntakeError",
    "BridgeIntakeRecord",
    "BridgeNormalizedRecord",
    "BridgeRunContext",
    "BridgeSourceRef",
    "BridgeTransformError",
    "create_intake_record",
    "normalize_bridge_payload",
    "sha256_bytes",
    "sha256_json_payload",
]
