"""Default-off configuration for the research-lab scheduler shell.

Every capability that could lead to autonomous behavior defaults to ``False``.
The configuration is the single guardrail the rest of the shell consults before
*planning* anything; because all of these are off, the planner can only ever
emit no-op actions.

There is intentionally **no** code path that flips these to ``True`` from inside
the shell. ``SchedulerShellConfig`` is frozen, and even a hand-constructed
"enabled" config does not give the shell an executor — it has none. The flags
exist so the inert posture is *legible and asserted*, not because toggling them
would do anything in this package.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Final


# The exact default-off guarantees required by the package (§5). Each maps to a
# class of autonomous behavior that stays disabled.
DEFAULT_OFF_FLAGS: Final[tuple[str, ...]] = (
    "autonomous_enabled",
    "edge_search_enabled",
    "run_triggering_enabled",
    "notification_firing_enabled",
    "candidate_lifecycle_writes_enabled",
    "runtime_contact_enabled",
    "paper_live_contact_enabled",
)


@dataclass(frozen=True)
class SchedulerShellConfig:
    """Inert scheduler configuration. All autonomy disabled by default.

    Frozen so a config value cannot be mutated in place after construction. The
    defaults are the contract: a config built with no arguments is fully off.
    """

    autonomous_enabled: bool = False
    edge_search_enabled: bool = False
    run_triggering_enabled: bool = False
    notification_firing_enabled: bool = False
    candidate_lifecycle_writes_enabled: bool = False
    runtime_contact_enabled: bool = False
    paper_live_contact_enabled: bool = False

    def as_dict(self) -> dict[str, bool]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def any_enabled(self) -> bool:
        """True if *any* autonomous capability is enabled (should be False)."""
        return any(self.as_dict().values())

    def enabled_flags(self) -> tuple[str, ...]:
        """Names of any enabled flags (empty in the default-off posture)."""
        return tuple(name for name, value in self.as_dict().items() if value)


def default_config() -> SchedulerShellConfig:
    """Return the canonical default-off configuration."""
    return SchedulerShellConfig()


class SchedulerConfigError(ValueError):
    """Raised when a config is asserted default-off but is not."""


def validate_default_off(config: SchedulerShellConfig) -> dict[str, object]:
    """Validate that every required default-off flag is ``False``.

    Returns a structured validation result. Raises ``SchedulerConfigError`` only
    if asked to *assert* (see ``assert_default_off``). The shell calls this
    before planning and refuses to plan anything but no-ops regardless.
    """
    flag_values = config.as_dict()
    missing = [name for name in DEFAULT_OFF_FLAGS if name not in flag_values]
    enabled = [name for name in DEFAULT_OFF_FLAGS if flag_values.get(name)]
    return {
        "all_default_off": not enabled and not missing,
        "missing_flags": missing,
        "enabled_flags": enabled,
        "checked_flags": list(DEFAULT_OFF_FLAGS),
    }


def assert_default_off(config: SchedulerShellConfig) -> None:
    """Raise if any required default-off flag is enabled or missing."""
    result = validate_default_off(config)
    if not result["all_default_off"]:
        raise SchedulerConfigError(
            "scheduler shell config is not default-off: "
            f"enabled={result['enabled_flags']} missing={result['missing_flags']}"
        )
