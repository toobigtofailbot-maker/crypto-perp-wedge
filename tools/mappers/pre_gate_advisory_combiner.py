"""Deterministic pre-gate advisory bucket combiner."""

from __future__ import annotations


BUCKETS = {"ALLOW", "ALLOW_REDUCED", "BLOCK"}
MACRO_AWARE_FLOOR = "MACRO_AWARE_FLOOR"


def combine_pre_gate_advisory_bucket(mapped_bucket: str, macro_window_flag: bool) -> str:
    """Combine committed BMAP bucket state with committed MOUT macro-window state."""

    if mapped_bucket not in BUCKETS:
        raise ValueError(f"mapped_bucket must be one of {sorted(BUCKETS)}, got {mapped_bucket!r}")
    if not isinstance(macro_window_flag, bool):
        raise ValueError(f"macro_window_flag must be bool, got {macro_window_flag!r}")

    if not macro_window_flag:
        return mapped_bucket
    if mapped_bucket == "ALLOW":
        return "ALLOW_REDUCED"
    return mapped_bucket
