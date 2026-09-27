# Nautilus N1 Common Research Engine Adapter

## Status and purpose

`CPW-NAUTILUS-N1-01` promotes the historical bounded mapping spike into one
reusable, non-authoritative CPW research adapter. It consumes the merged
CANON-01 `RunRequest`, separately resolved CPW artifacts and data, executes the
frozen RP-2592 profile through NautilusTrader `1.231.0`, and normalizes the
result with CANON-01 `build_result_envelope`.

This is an adapter-seam and determinism proof. It is not cross-engine semantic
parity, research-engine promotion, canonical persistence, or paper/live
authority.

## Ownership boundary

| Surface | Owner | N1-01 posture |
| --- | --- | --- |
| Strategy Spec, Variant Manifest, Sweep Plan, signal/domain meaning | CPW | Unchanged; signals come from `compile_signal` |
| RunRequest, denominator, scientific normalization and identity | CPW / CANON-01 | Consumed unchanged |
| Offline generic matching, fills, positions and account mechanics | NautilusTrader | Bounded to the supported fixture |
| Adapter mapping and semantic-gap disclosure | CPW adapter | Common implementation in `tools/nautilus_adapter/research.py` |
| Canonical write/crossing, candidate lifecycle, runtime and capital | CPW / humans | Not authorized or exposed |

The historical `tools/simulators/nautilus_mapping_spike.py` retains its report
and comparison facade but delegates instrument construction, bar/open-event
conversion, target-signal execution, dynamic sizing, and result extraction to
the common adapter.

## Version and environment decision

The proof uses the exact NautilusTrader `1.231.0` 1.x API on CPython 3.12 for
Windows x86-64. It is installed only in fresh environments outside the repo.
`tools/nautilus_adapter/requirements-win-py312.lock.txt` owns the exact N1 proof
dependency set and is consumed only by N1 build/reproduction validation. It has
no root dependency, runtime, engine-selection, or update authority. It may be
updated only by a later package that explicitly changes this proof dependency
surface. Root `requirements.txt`, `requirements.lock.txt`, and `pyproject.toml`
remain unchanged.

## Input and output seams

`ResolvedResearchInputs` binds a validated CANON-01 `RunRequest` to resolved
Strategy Spec, Variant Manifest, Sweep Plan, RP-2592 compatibility source,
OHLCV path, and exact repository revision. The adapter recomputes the existing
artifact hash forms, reprojects RP-2592 through
`project_result_population_v1`, and fails closed on any parent, ordered variant,
denominator, data identity, seed, assumption, sizing, availability, row-count,
or normalized-data-hash mismatch. Machine-local paths never enter CANON
identity.

`execute_nautilus_research` compiles each declared variant through CPW's
existing `compile_signal`, executes all denominator rows, preserves execution
errors as errored rows, and calls CANON-01 `build_result_envelope`. Nautilus,
Python, adapter, source, dependency-lock, environment, and repo-revision facts
are execution provenance and remain outside scientific evidence identity. The
adapter exposes no writer or persistence API.

## Supported N1-01 profile

The only accepted profile is `cpw_nautilus_n1_01_rp2592_profile_v1`: offline
BTCUSDT perpetual research, 15-minute OHLCV, completed-bar target decisions,
next-bar-open fills, complete fills, dynamic realized-available-equity sizing at
1x leverage using the same next-open reference, combined 5 bps taker
fee/slippage representation, zero funding, and the exact eight RP-2592
variants. Other scientific profiles fail closed.

The next-open proof uses a separate open quote event and deterministic bounded
order-insert latency after each completed decision bar. The decision uses only
information through bar `t`; the actual Nautilus fill is recorded at the open
event for bar `t+1`, and its quantity uses realized available equity divided by
that same open. The micro-fixture is a hard gate before the frozen corpus run.

## Semantic-gap matrix

| Category | N1-01 state |
| --- | --- |
| next-bar-open execution | `PROVEN_FOR_N1_01` |
| fee/slippage split | `NOT_PROVEN_IN_N1_01` |
| nonzero funding | `NOT_PROVEN_IN_N1_01` |
| dynamic 1x fixture sizing | `PROVEN_FOR_N1_01_FIXTURE` |
| generalized quantity precision parity | `NOT_PROVEN_IN_N1_01` |
| direct flip | `NOT_PROVEN_IN_N1_01` |
| zero-equity liquidation | `NOT_PROVEN_IN_N1_01` |
| maintenance margin | `NOT_PROVEN_IN_N1_01` |

The semantic-gap report is deterministic, non-authoritative migration evidence;
it is not a promotion or candidate decision. Instrument quantity is quantized
explicitly to eight decimal places in this fixture. N1-02 owns separate fee and
slippage accounting, nonzero funding, generalized sizing precision, direct
flip, liquidation, and margin stress closure. N1-03 alone may later authorize
runner routing, research-engine promotion, or legacy retirement.
