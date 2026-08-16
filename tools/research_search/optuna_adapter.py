"""Capability-gated Optuna proposal adapter with no scientific authority."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

import optuna

from tools.research_search.contract import (
    ConditionalParameterRule,
    ParameterSpec,
    ProposerSpec,
    canonical_json,
    sha256_payload,
)

SNAPSHOT_VERSION = "optuna-proposal-replay-v1"


class OptunaAdapterError(RuntimeError):
    """Raised when the proposal-only adapter cannot safely continue."""


class AdapterBypassDenied(OptunaAdapterError):
    """Raised when code attempts to use Optuna without a Governor capability."""


class SnapshotReplayError(OptunaAdapterError):
    """Raised when recorded proposal state cannot reproduce exact continuation."""


_CAPABILITY_BRAND = object()


@dataclass(frozen=True)
class _GovernorCapability:
    search_id: str
    contract_hash: str
    brand: object


def _new_governor_capability(search_id: str, contract_hash: str) -> _GovernorCapability:
    return _GovernorCapability(search_id, contract_hash, _CAPABILITY_BRAND)


@dataclass(frozen=True)
class ProposalSurface:
    search_id: str
    contract_hash: str
    parameter_space: tuple[ParameterSpec, ...]
    conditional_rules: tuple[ConditionalParameterRule, ...]
    proposer: ProposerSpec
    seed: int
    objective_direction: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdapterProposal:
    handle: str
    backend_trial_number: int
    params: dict[str, Any]


def supported_backends() -> dict[str, bool]:
    return {
        "tpe": hasattr(optuna.samplers, "TPESampler"),
        "random": hasattr(optuna.samplers, "RandomSampler"),
        "qmc": hasattr(optuna.samplers, "QMCSampler"),
        "gp": hasattr(optuna.samplers, "GPSampler"),
    }


def _sampler(spec: ProposerSpec, seed: int) -> Any:
    config = dict(spec.config)
    if spec.backend == "tpe":
        allowed = {"multivariate", "group", "n_startup_trials"}
        unknown = set(config) - allowed
        if unknown:
            raise OptunaAdapterError(f"unsupported TPE config: {sorted(unknown)}")
        return optuna.samplers.TPESampler(seed=seed, **config)
    if spec.backend == "random":
        if config:
            raise OptunaAdapterError("Random proposer accepts no extra config")
        return optuna.samplers.RandomSampler(seed=seed)
    if spec.backend == "qmc":
        allowed = {"qmc_type", "scramble"}
        unknown = set(config) - allowed
        if unknown:
            raise OptunaAdapterError(f"unsupported QMC config: {sorted(unknown)}")
        return optuna.samplers.QMCSampler(seed=seed, **config)
    if spec.backend == "gp":
        if not hasattr(optuna.samplers, "GPSampler"):
            raise OptunaAdapterError("GPSampler is unavailable in the pinned Optuna")
        allowed = {"deterministic_objective", "n_startup_trials"}
        unknown = set(config) - allowed
        if unknown:
            raise OptunaAdapterError(f"unsupported GP config: {sorted(unknown)}")
        return optuna.samplers.GPSampler(seed=seed, **config)
    raise OptunaAdapterError(f"unknown proposer backend: {spec.backend}")


class OptunaProposalAdapter:
    """Optuna ask/tell wrapper callable only with a bound Governor capability."""

    def __init__(
        self,
        surface: ProposalSurface,
        *,
        capability: _GovernorCapability | None = None,
    ) -> None:
        self._verify_capability(capability, surface)
        if surface.proposer.version != optuna.__version__:
            raise OptunaAdapterError(
                "pinned proposer version mismatch: "
                f"contract={surface.proposer.version}, installed={optuna.__version__}"
            )
        self.surface = surface
        self._study = optuna.create_study(
            direction=surface.objective_direction,
            sampler=_sampler(surface.proposer, surface.seed),
            study_name=surface.search_id,
        )
        self._live_trials: dict[str, Any] = {}
        self._operations: list[dict[str, Any]] = []

    @staticmethod
    def _verify_capability(
        capability: _GovernorCapability | None,
        surface: ProposalSurface,
    ) -> None:
        if (
            capability is None
            or capability.brand is not _CAPABILITY_BRAND
            or capability.search_id != surface.search_id
            or capability.contract_hash != surface.contract_hash
        ):
            raise AdapterBypassDenied("Optuna proposals require a bound Search Governor")

    def _verify_bound(self, capability: _GovernorCapability | None) -> None:
        self._verify_capability(capability, self.surface)

    def _suggest(self, trial: Any, spec: ParameterSpec) -> Any:
        if spec.kind == "int":
            return trial.suggest_int(
                spec.name,
                int(spec.low),
                int(spec.high),
                step=int(spec.step or 1),
            )
        if spec.kind == "float":
            kwargs = {"step": float(spec.step)} if spec.step is not None else {}
            return trial.suggest_float(spec.name, float(spec.low), float(spec.high), **kwargs)
        return trial.suggest_categorical(spec.name, list(spec.choices))

    def ask(self, capability: _GovernorCapability | None = None) -> AdapterProposal:
        self._verify_bound(capability)
        trial = self._study.ask()
        params: dict[str, Any] = {}
        rules = {rule.parameter: rule for rule in self.surface.conditional_rules}
        for spec in self.surface.parameter_space:
            rule = rules.get(spec.name)
            if rule is not None:
                if rule.when_parameter not in params:
                    raise OptunaAdapterError(
                        f"conditional gate must precede parameter {spec.name}: "
                        f"{rule.when_parameter}"
                    )
                if params[rule.when_parameter] not in rule.when_values:
                    continue
            params[spec.name] = self._suggest(trial, spec)
        handle = f"optuna-trial:{trial.number}"
        self._live_trials[handle] = trial
        operation = {
            "op": "ask",
            "handle": handle,
            "backend_trial_number": trial.number,
            "params": params,
        }
        self._operations.append(operation)
        return AdapterProposal(handle, trial.number, params)

    def tell(
        self,
        capability: _GovernorCapability | None,
        handle: str,
        *,
        state: str,
        value: float | None = None,
    ) -> None:
        self._verify_bound(capability)
        trial = self._live_trials.pop(handle, None)
        if trial is None:
            raise OptunaAdapterError(f"unknown or already-told proposal handle: {handle}")
        if state == "complete":
            if value is None:
                raise OptunaAdapterError("complete proposal requires an objective value")
            self._study.tell(trial, float(value))
        elif state in {"invalid", "duplicate", "software_failed"}:
            self._study.tell(trial, state=optuna.trial.TrialState.FAIL)
        else:
            raise OptunaAdapterError(f"unsupported terminal adapter state: {state}")
        self._operations.append({"op": "tell", "handle": handle, "state": state, "value": value})

    def snapshot(self, capability: _GovernorCapability | None) -> dict[str, Any]:
        self._verify_bound(capability)
        if self._live_trials:
            raise OptunaAdapterError("snapshot requires every proposed trial to be told")
        payload = {
            "snapshot_version": SNAPSHOT_VERSION,
            "optuna_version": optuna.__version__,
            "surface": self.surface.to_dict(),
            "operations": list(self._operations),
            "restore_method": "seeded_exact_operation_replay_with_proposal_verification",
            "contains_final_holdout": False,
        }
        payload["snapshot_hash"] = sha256_payload(payload)
        return payload

    @classmethod
    def restore(
        cls,
        surface: ProposalSurface,
        snapshot: Mapping[str, Any],
        *,
        capability: _GovernorCapability | None,
    ) -> OptunaProposalAdapter:
        cls._verify_capability(capability, surface)
        payload = dict(snapshot)
        snapshot_hash = payload.pop("snapshot_hash", None)
        if snapshot_hash != sha256_payload(payload):
            raise SnapshotReplayError("adapter snapshot hash mismatch")
        if payload.get("snapshot_version") != SNAPSHOT_VERSION:
            raise SnapshotReplayError("unsupported adapter snapshot version")
        if payload.get("optuna_version") != optuna.__version__:
            raise SnapshotReplayError("adapter snapshot Optuna version mismatch")
        if canonical_json(payload.get("surface")) != canonical_json(surface.to_dict()):
            raise SnapshotReplayError("adapter snapshot proposal surface mismatch")
        adapter = cls(surface, capability=capability)
        for operation in payload.get("operations", []):
            if operation.get("op") == "ask":
                replayed = adapter.ask(capability)
                expected = {
                    "handle": operation.get("handle"),
                    "backend_trial_number": operation.get("backend_trial_number"),
                    "params": operation.get("params"),
                }
                actual = {
                    "handle": replayed.handle,
                    "backend_trial_number": replayed.backend_trial_number,
                    "params": replayed.params,
                }
                if canonical_json(actual) != canonical_json(expected):
                    raise SnapshotReplayError("Optuna proposal replay diverged")
            elif operation.get("op") == "tell":
                adapter.tell(
                    capability,
                    str(operation.get("handle")),
                    state=str(operation.get("state")),
                    value=operation.get("value"),
                )
            else:
                raise SnapshotReplayError("adapter snapshot contains an unknown operation")
        return adapter
