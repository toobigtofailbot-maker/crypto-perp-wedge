# CPW Domain Extraction and Active Storage Contract

## 1. Status, package, and effective boundary

This contract is the normative output of `CPW-MIG-01`. It becomes effective
when that package merges. It defines framework-neutral CPW research-domain
functions and non-authoritative local workspace paths only.

## 2. Purpose

The contract separates CPW-owned scientific meaning from legacy agent and lab
wrappers, and gives future migration consumers stable repo-local locations for
active/provisional and ephemeral work. It is a foundation extraction, not a
framework, authority, or runtime cutover.

## 3. Domain package public responsibilities

`tools.research_domain` owns the minimum public surface locked by CPW-MIG-01:

- research timeframes, trial statuses, and current lab preregistration constants;
- deterministic feature detection, capability assessment, and Strategy-Spec
  draft construction from already-loaded inputs;
- exact noncanonical preregistration packet, requirement, approval, and marker
  meaning, including content-hash binding and fail-closed validation;
- declared-trial and variant-denominator validation, deterministic bridge ledger
  construction, and the existing bridge/direct Result Population comparison.

Public validation failures are `ValueError`-compatible. Functions perform no
file, network, provider, scheduler, runner, canonical, or runtime operation.

## 4. Explicit non-responsibilities

The domain package does not own provider invocation, orchestration, run state,
search legality or budgets, compiler or backtest mechanics, candidate lifecycle,
promotion, ranking, readiness, canonical writers, runtime, OMS, reconciliation,
risk, overlay, safe mode, exchange/order handling, live behavior, or capital.
It is not a generic approval framework or service layer.

## 5. Framework-neutral import and dependency rule

`tools.research_domain` and `tools.research_storage` may use the Python standard
library and pure typed/data primitives only. They must not depend on Pydantic AI,
Hermes, Prefect, NautilusTrader, ToolContext, lab orchestration/state/scheduler,
canonical intake, `lib.backtest`, protected runtime modules, or network clients.

## 6. Legacy compatibility rule

Existing research-agent and lab-pipeline import paths, CLIs, exception surfaces,
default outputs, and package-named `scratch/` paths remain operational. Scoped
wrappers retain file/provider/ToolContext behavior and delegate extracted meaning
to `tools.research_domain`. Existing oracle tests remain unchanged.

## 7. Active, provisional, and ephemeral storage layout

The entire repo-local `.cpw/` tree is gitignored:

- active/provisional: `.cpw/active/`
- ephemeral: `.cpw/ephemeral/`

`tools.research_storage.resolve_workspace_path` accepts only safe relative
namespaces and artifact paths, resolves them beneath one of those roots, rejects
absolute, drive-qualified, traversal, and escaping symlink/junction ancestry,
and may create parents only below the selected root.

## 8. Authority meaning of each storage class

Active/provisional content is noncanonical work in progress. It may be
regenerated from frozen inputs where another contract requires that, but its
presence is not repo truth and creates no Result Population, candidate,
promotion, execution, or canonical authority.

Ephemeral content is disposable task-local cache or intermediate state. It may
be deleted or recomputed and has no authority by presence.

Operational history remains a future Prefect concern and is not implemented
here.

## 9. Historical scratch posture

Existing tracked and local package-named `scratch/` content remains readable
under its recorded historical contracts. CPW-MIG-01 does not move, delete,
rewrite, reclassify, or migrate it, and does not change ToolContext
`WRITE_SCRATCH` behavior.

## 10. Canonical boundary

Canonical research authority remains CPW-controlled and outside
`tools.research_storage`. The storage API cannot target canonical research,
source, runtime, or protected paths. No final canonical `RunRequest`,
`ResultEnvelope`, writer, crossing, schema, validator, or query contract is
created here.

## 11. Consumer guidance for later packages

Separately authorized `CPW-HERMES-01`, `CPW-PREFECT-01`,
`CPW-NAUTILUS-N1-01`, `CPW-CANON-01`, and `CPW-RESEARCH-02` packages may consume
these seams. They must preserve CPW-owned meaning and may not infer authority
from a function result or `.cpw/` file. These names describe runway eligibility
only; this contract authorizes none of those packages.

## 12. Deletion and retirement posture

No legacy wrapper, scheduler, state store, runner, scratch path, or historical
artifact is retired by CPW-MIG-01. Consumer cutover, ownership transfer, data
migration, and retirement each require a later explicit package and proof.

## 13. Validation and oracle posture

The unchanged legacy agent/lab tests are the semantic oracle. Direct domain and
storage tests additionally prove determinism, hash/approval binding,
full-denominator validation, exact result comparison, import purity, path
containment, gitignore coverage, and absence of authority-bearing side effects.
The T2 full-release profile is required for the package's final implementation
head.

## 14. Next-package eligibility after merge

Merge completes only the CPW-owned foundation identified by CPW-MIG-00. Any
next migration lane requires a separately approved package and retains all
scientific, canonical, human, protected-runtime, live, and capital gates.
