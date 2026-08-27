"""Closed executable-action registry.

BROKER-1 kept this registry deliberately empty and non-dispatching. H3-1 adds the
first — and structurally the only permitted kind of — dispatch-capable entry: a
single real, read-only A1 action. Two invariants are locked here so the registry
*cannot express* anything more dangerous than a read-only action:

* every entry is ``read_only`` (a mutating action can never be registered), and
* an entry is either a non-dispatching ``proof_only`` entry or a dispatch-capable
  real entry, never both and never a dispatch-capable proof entry.

A0 remains registry-absent and every entry must require A1.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tools.hermes.proposals.models import A0_DOMAINS, AffectedDomain, AuthorityClass

from .models import (
    ExactBound,
    ExecutableAction,
    StrictBrokerModel,
    TimeoutBound,
)

REGISTRY_SCHEMA_VERSION = "hermes_broker_action_registry_v1"
PRODUCTION_REGISTRY_VERSION = "broker1-production-empty-v1"


@dataclass(frozen=True)
class RegistryEntry:
    registry_schema_version: str
    registry_version: str
    action_type: str
    action_model: type[ExecutableAction]
    required_authority_class: AuthorityClass
    target_model: type[StrictBrokerModel]
    scope_model: type[StrictBrokerModel]
    parameters_model: type[StrictBrokerModel]
    budget_model: type[ExactBound]
    count_or_quantity_model: type[ExactBound] | None
    timeout_model: type[TimeoutBound]
    adapter_id: str
    adapter_version: str
    affected_domains: frozenset[AffectedDomain]
    dispatch_capable: bool
    proof_only: bool
    # Locked: the registry can only ever express a read-only action. A mutating
    # first action is not authorized and cannot be represented here at all.
    read_only: bool = True

    def __post_init__(self) -> None:
        if self.registry_schema_version != REGISTRY_SCHEMA_VERSION:
            raise ValueError("unsupported action registry schema")
        if re.fullmatch(r"[a-z][a-z0-9._-]{2,127}", self.action_type) is None:
            raise ValueError("invalid closed action_type")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", self.registry_version) is None:
            raise ValueError("invalid registry version")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", self.adapter_id) is None:
            raise ValueError("invalid adapter identity")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", self.adapter_version) is None:
            raise ValueError("invalid adapter version")
        if self.required_authority_class is not AuthorityClass.A1:
            raise ValueError("registry entries must require A1")
        if self.affected_domains & A0_DOMAINS:
            raise ValueError("A0 domains have no executable registry entry")
        if self.read_only is not True:
            raise ValueError("only read-only registry entries are authorized")
        if self.dispatch_capable == self.proof_only:
            raise ValueError(
                "an entry is exactly one of proof_only (non-dispatching) or "
                "dispatch_capable (real, read-only)"
            )
        if self.dispatch_capable and not self.read_only:
            raise ValueError("a dispatch-capable entry must be read-only")
        if not issubclass(self.action_model, ExecutableAction):
            raise TypeError("action_model must be an ExecutableAction model")
        if not all(
            issubclass(model, StrictBrokerModel)
            for model in (self.target_model, self.scope_model, self.parameters_model)
        ):
            raise TypeError("target, scope, and parameters must be strict broker models")


class ActionRegistry:
    """Immutable exact-version registry with no wildcard or callable surface."""

    def __init__(self, *, version: str, entries: tuple[RegistryEntry, ...] = ()) -> None:
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", version) is None:
            raise ValueError("invalid loaded registry version")
        self.version = version
        mapping: dict[str, RegistryEntry] = {}
        for entry in entries:
            if entry.registry_version != version:
                raise ValueError("registry entry version does not match loaded registry")
            if entry.action_type in mapping:
                raise ValueError("duplicate action_type")
            mapping[entry.action_type] = entry
        self._entries = mapping

    @property
    def entries(self) -> tuple[RegistryEntry, ...]:
        return tuple(self._entries.values())

    def get(self, action_type: str) -> RegistryEntry | None:
        return self._entries.get(action_type)


def production_registry() -> ActionRegistry:
    """Return the production registry: exactly one real A1 read-only action (H3-1).

    The single entry is defined in :mod:`tools.hermes.broker.h3_readonly` and is
    imported lazily so that low-level modules importing this registry never take a
    dependency on the action model, the projection, or the read-only adapter.
    """

    from .h3_readonly import h3_1_readonly_registry

    return h3_1_readonly_registry()
