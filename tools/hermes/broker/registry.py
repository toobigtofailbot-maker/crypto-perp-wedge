"""Closed, non-dispatching BROKER-1 executable-action registry."""

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
            raise ValueError("BROKER-1 registry entries must require A1")
        if self.affected_domains & A0_DOMAINS:
            raise ValueError("A0 domains have no executable registry entry")
        if self.dispatch_capable:
            raise ValueError("BROKER-1 registry entries cannot dispatch")
        if not self.proof_only:
            raise ValueError("BROKER-1 permits proof-only entries only")
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
    """BROKER-1 production default: deliberately zero executable actions."""

    return ActionRegistry(version=PRODUCTION_REGISTRY_VERSION)
