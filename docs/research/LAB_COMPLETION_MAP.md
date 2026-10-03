# Research-Lab Completion Map

> **Current migration-direction pointer — 2026-09-23:** This map remains the
> authoritative record of the historical no-edge-search lab scope and its proof
> status. It does not override
> `docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`.
> After CPW-MIG-01 establishes target-compatible seams, differentiated research
> may continue, and bounded non-capital infrastructure proof is not blocked by
> the absence of edge. This pointer grants no edge-search, promotion, live, or
> capital authority.

## V2 current direction

The no-edge-search, scheduler/scout default-off, and advisory-only facts below
remain accurate historical evidence and remain operationally effective until
Stage 5B is implemented, validated, explicitly activated, and a valid
Karl-approved bounded research envelope exists. Under `D2-020`, they are not
permanent architecture prohibitions on legal in-envelope research. V2-00
activates nothing; Stage 5B is the future activation boundary. See
`docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`.

## 2026-08-05 controlling readiness decision

`docs/decisions/ENGINEERING_VS_STRATEGY_READINESS.md` now controls the
engineering-vs-strategy boundary. This map remains authoritative for its
historical research evidence, completed proof, and non-authority facts, but its
earlier planning conclusions that made profitable/real-candidate flow a
prerequisite for engineering construction or non-capital validation are
superseded in place below.

H-004-R2 is the designated non-winning engineering dummy. Separately authorized
packages may use it to build and engineering-validate the lab, autonomous
factory, paper/shadow and monitoring layers, and live-capable stack in disabled,
simulation, or other non-capital modes. It remains non-production,
non-promotable, and structurally GO-forbidden; none of its engineering evidence
establishes edge or authorizes real capital.

## Status and authority

This is the authoritative committed completion map for the research lab. It
records, for the current phase, what is **built and complete**, what is
**structurally present but inert / deferred-B**, what is **GO-gated execution-
machine work out of scope**, and the **exact boundaries** at which any of the
deferred work may be reauthorized.

This document is **descriptive only**. It executes nothing, runs or generates no
strategy, resumes no edge-search, writes no canonical or candidate-lifecycle
evidence, ranks or recommends nothing, and touches no runtime, paper/live, OMS,
risk, reconciliation, capital, broker, exchange, provider/API, or funding
accounting path. It introduces no new architecture decision. Its purpose is to
make the current phase state explicit so "finish the lab" cannot silently drift
into edge-search, execution-machine work, or speculative autonomous behavior.

Baseline-proven update: PRs #583 through #586 demonstrated the core research
pipe at fixture/plumbing level using deliberately non-promotable construction
payloads. That proof covers baseline payload definition, non-promoting WFO/OOS
and robustness/MC gate semantics, non-promotable crossing rejection, and bounded
agent/lab-loop behavior for a no-candidate baseline. It does not create
candidate authority, real crossing authority, edge-search authority, always-on
factory completion, paper/live/runtime authority, or execution-machine scope.

Final Side 12 no-edge-phase update: PRs #588 through #590 completed the final
known-payload hardening batch after the baseline-proven sequence. PR #588 proved
scale-correct denominator preservation with a 600-row synthetic population from
the `known_losing_baseline` lineage. PR #589 hardened the read-only registry /
provenance view. PR #590 completed the read-only dashboard gap surface and
fail-closed provenance visibility. Together these packages finish what can be
completed before bounded real-traffic acceptance evidence existed while preserving
the boundary that a known non-promotable payload cannot prove autonomous
always-on factory operation,
first real candidate crossing, or paper/live/runtime authority.

Final operating-readiness audit update: PRs #592 through #595 executed the
deterministic event-tape operating-readiness route after the final Side 12
known-payload map. The route covered a 40-event / 10-job operating-test stream,
queue/scheduler dry-run handling, notification/report dry-run cadence, and
agent-loop/dashboard stream handling. This proves operating-system evidence, not
strategy evidence. The lab is now complete for known-payload strategy-pipe proof
and deterministic operating-readiness acceptance testing. It is still not
production autonomous operation, not generated real-research surface operation,
not real candidate admission, not real crossing, and does not create paper/live
readiness.

Real-traffic acceptance update: PR #606 and PR #608 added bounded real research
traffic acceptance evidence for the real-input operating layer. The revised
four-hypothesis batch preserved the full frozen denominator: 32/32 rows
preserved, 0 dropped, 0 blocked after completion, and 32 executed successful
rows. The stream covered formalize, route, sweep, preserve, gate, and review
without writing a canonical Result Population and without surfacing GO-like or
candidate-worthy evidence. This is real-input operating-layer acceptance
evidence, not candidate authority, crossing authority, paper/live/runtime
authority, production autonomous operation, or always-on factory completion.

## 1. Current phase definition

The current phase is a **human-driven, no-edge-search research lab**. Its job is
to make completed research **legible, auditable, and operator-reviewable** while
preserving locked evidence discipline and permanent human gates.

In this phase the lab:

- consumes already-produced research evidence and exposes it through read-only
  operator surfaces;
- enforces evaluation rigor (replay normalization, walk-forward / OOS gating,
  robustness review reach) on that evidence;
- records conclusions (including NO-GO) with full provenance;
- holds all autonomous behavior, strategy generation, candidate promotion, and
  runtime contact behind explicit separate authorization.

The phase does **not** include: generating new strategy hypotheses, resuming
edge-search, executing canonical crossing, promoting candidates, or any
paper/live/runtime execution. Those are out of phase by design, not by omission.

The conceptual target operating model (the "Side 12" target-state in
`docs/research_pipeline/2026-06-strategy_research_lab_target_operating_model.md`)
remains the long-horizon reference. Current project posture remains at autonomy
levels **L0 / L1** (manual design; assisted drafting) — L2 and above are not
authorized.

## 2. Built and complete (no-edge-search research-lab scope)

The following are built, merged, and complete for this phase.

### 2.1 Research engine and evidence primitives

- **Compiler / primitives and deterministic research runner** — the offline
  research runner and funding-percentile compiler semantics that produced the
  committed Result Populations (`tools/research_runner/`, compiler funding
  percentile semantics). Deterministic, offline, no runtime contact.
- **Result Populations and validators** — committed Result Population artifacts
  (`RP-2009`, `RP-7592`, `RP-2592`, …) with preserved denominators and integrity
  validators surfaced through the query layer.
- **Query layer** — `tools/research_query/` (`run.py`, `query_layer.py`,
  `views.sql`) exposing read-only views over candidates, experiments, gate
  results, outcome ledger, reconciliation, and integrity checks
  (`python -m tools.research_query.run --list-views`).
- **Replay-normalization contract** — family-agnostic Result Population replay
  comparison (`docs/research/RP_REPLAY_NORMALIZATION_CONTRACT.md`,
  `tools/research_replay`).

### 2.2 Evaluation-rigor gates

- **Walk-forward / OOS gate** — non-canonical walk-forward / out-of-sample gate
  contract with decisions `pass` / `fail` / `blocked` / `advisory_only`
  (`docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md`, `tools/oos_gate/`,
  `tools/walkforward/`). Holds no approval/promotion authority.
- **Robustness / candidate-review reach** — generic robustness review reach
  contract with `NO_GO_*` / `BLOCKED_*` reason codes and explicit withheld-
  statistic handling (`docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md`,
  `tools/robustness`). Withholds PSR / DSR / MinTRL rather than fabricating them.

### 2.3 Research artifact / status model

- **Coordinator state model** — the canonical read-only state model that all
  operator surfaces consume so they read one status vocabulary
  (`docs/research/LAB_COORDINATOR_STATE_MODEL.md`, `tools/lab_state/`, PR #568).
  Introduces no new state names; resolver reads committed artifacts only.
- **Funding NO-GO conclusion** — `H-FUNDING-RATE-POSITIONING-FADE-01 = NO-GO`
  under the tested price-P&L funding-rate signal interpretation
  (`docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`). All 36/36
  completed rows failed the 20% primary drawdown screen; scratch-only,
  non-canonical, no candidate registered, no crossing executed.

### 2.4 Operator-facing surfaces (all read-only)

- **Results dashboard** — read-only projection of the state model; shows the
  full denominator (not winners-only), evidence class, withheld statistics,
  NO-GO caveats, artifact drill-down (`docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`,
  `tools/lab_dashboard/`, PR #569).
- **Daily brief / weekly report** — read-only shaping of the dashboard
  projection into operator-readable artifacts; descriptive-only; charting
  deferred (`docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`,
  `tools/lab_reporting/`, PR #570).
- **Approval / gate queue** — read-only view of pending human gates, blocked
  validation states, and candidate-review readiness *only when evidence exists*;
  displays gates, does not execute them
  (`docs/research/LAB_APPROVAL_QUEUE_SURFACE.md`, `tools/lab_approval_queue/`,
  PR #572).
- **Scheduler shell (default-off / inert)** — control-plane structure (run
  queue, run-status / retry / block model, artifact-link model, dry-run planner)
  with **no executor**; the only output it can produce is a planned no-op
  (`docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md`,
  `tools/lab_scheduler_shell/`, PR #571).

`WP-LAB-OPERATOR-SURFACE-INTEGRATION-01` (#573) and
`WP-LAB-STATE-MODEL-COVERAGE-AUDIT-01` (#574) are merged. The follow-up
`WP-LAB-COVERAGE-GAP-CLOSE-01` binds the audit-discovered historical evidence
gaps into read-only coordinator/operator visibility: eight coordinator subjects,
107 covered coordinator artifacts, 103 surface-visible artifact references, and
zero unmapped gap artifacts. Candidate-ready remains zero and operator-gate
pending remains zero.

### 2.5 Baseline-proven core pipe fixture/plumbing proof

PRs #583 through #586 prove the baseline construction sequence at
fixture/plumbing level:

- baseline construction payloads are defined as construction-only and
  non-promotable;
- WFO/OOS and robustness/MC gate semantics are hardened as non-promoting gates;
- baseline payloads cannot create candidate eligibility, promotion readiness,
  paper/live eligibility, edge claims, or canonical crossing authority;
- the non-promotable crossing guard rejects construction payloads with
  `reason_code=reject_by_construction`;
- the bounded baseline agent/lab loop observed a no-candidate result and did
  not recommend rescue, retuning, ranking as edge, readiness, promotion, real
  crossing, or paper/live action.

This is a core pipe fixture/plumbing proof only. It is not full always-on
factory completion, not real candidate flow, and not a promotion or execution
authorization.

## 3. Inert / default-off surfaces (structurally present, not live)

These are committed and structurally complete but produce **no effect**:

- **Scheduler shell** — every autonomy flag (`autonomous_enabled`,
  `edge_search_enabled`, `run_triggering_enabled`, `notification_firing_enabled`,
  `candidate_lifecycle_writes_enabled`, `runtime_contact_enabled`,
  `paper_live_contact_enabled`) defaults `False`; there is no executor; the
  dry-run planner emits only `no_op` actions with `executed: false`.
- **Approval / gate queue** — displays gates and shows `nothing_candidate_ready`
  honestly; it cannot write an approval or execute a gate.

## 4. Deferred-B behaviors (deferred, with exact reason)

Historical pre-decision posture (superseded on 2026-08-05 for engineering
construction and non-capital validation): "Deferred-B" meant that the
*structure* was present or anticipated but intentionally not live, with separate
operator authorization and real candidate flow required before activation.

Under `docs/decisions/ENGINEERING_VS_STRATEGY_READINESS.md`, separately
authorized engineering construction and validation may proceed with H-004-R2 in
disabled, simulation, or other non-capital modes. Genuine candidate evidence is
still required for performance-dependent promotion and real-capital activation;
the dummy cannot satisfy that boundary.

| Deferred-B behavior | Why it is deferred |
| --- | --- |
| Autonomous scheduling / run triggering | Scheduler shell is default-off with no executor; turning runs on is an autonomy step that needs explicit operator authorization. |
| Research scout (idea sourcing automation) | Would generate/seek new hypotheses — that is edge-search, which is held. |
| Notification firing | Surfaces are descriptive; `notification_firing_enabled = false`. Firing requires authorization and a real event to fire on. |
| Approval-queue writes | Queue displays gates only; writing an approval is a human-gated lifecycle action it cannot grant. |
| Candidate lifecycle writes | The lifecycle engine exists but is human-gated; no candidate is registered, so there is nothing to write. |
| Coordinator transition execution | The state model is descriptive; executing a transition is owned by the human-gated candidate lifecycle engine, not the model. |
| First real canonical crossing | No candidate has passed human review; crossing is a separately authorized package and has not occurred. |
| Live candidate-flow-dependent behavior | Genuine lifecycle/performance transitions still require a qualified candidate. Candidate-agnostic engineering plumbing may be built and validated with the designated dummy without creating candidate authority. |
| At-scale continuous sweeps | Historical proof covered baseline plumbing only. Separately authorized scale engineering may now use the dummy; results remain engineering evidence, not edge evidence. |
| At-scale WFO/OOS and robustness/MC execution volume | Gate semantics are hardened. Separately authorized volume/capacity validation may use the dummy, while performance-dependent promotion still requires genuine candidate evidence. |
| Agent scheduling / prioritization / autonomy | Baseline proof remains bounded historical evidence. Separately authorized factory engineering may operate over dummy/non-capital traffic; live-impacting or real-capital activation remains separately gated. |
| Notification firing over real jobs | Notification firing requires real jobs/events plus separate authorization; baseline fixtures do not create either. |

Historical pre-decision conclusion (superseded on 2026-08-05): activation of
every Deferred-B behavior required separate operator authorization and real
candidate flow. The controlling rule now permits separately authorized
engineering construction/non-capital validation with the designated dummy;
genuine candidate evidence remains mandatory wherever performance, promotion,
or real-capital semantics require it. This document itself grants no activation.

## 5. GO-gated execution-machine activation and engineering buildability

Historical pre-decision conclusion (superseded on 2026-08-05 for construction
and non-capital validation): the following were out of scope for the entire lab
phase and required an explicit GO decision plus the locked execution-machine
gates (D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, permanent human gates):

- paper / shadow / live execution;
- runtime monitoring;
- the execution machine itself;
- broker / exchange / order paths;
- OMS / risk / reconciliation / capital management;
- safe-mode / kill-switch operational authority (governance boundary preserved;
  no operational authority is added by the lab).

The historical claim that none of these layers is buildable in the current phase
is superseded by `docs/decisions/ENGINEERING_VS_STRATEGY_READINESS.md`. They may
be built, integrated, and engineering-validated with H-004-R2 in simulation,
disabled, or other non-capital modes under separately authorized packages.
Paper/live activation, runtime contact with live impact, promotion, risk/capital
changes, and real-capital deployment remain behind their explicit protected
gates and genuine-performance requirements.

## 6. Edge-search hold

**No further edge-search is authorized.** Strategy generation / hypothesis
search remains held until separate operator authorization. The funding NO-GO is
a *conclusion about one tested interpretation*; it does **not** authorize another
edge-search cycle, and this map does not recommend resuming edge-search. New
data-derived families or funding variants require separate Main/operator
authorization.

## 7. What remains buildable now (within phase)

Historical pre-decision conclusion (superseded on 2026-08-05): after the
deterministic event-tape route and bounded real-traffic revised batch, no further
no-edge operating-readiness package was identified as both buildable and
value-adding. Current repo truth permits separately authorized engineering work
with H-004-R2 where it adds new infrastructure/capacity/safety proof in
non-capital modes. Such work must remain deterministic, non-authoritative, and
must not imply edge, promotion, or real-capital authority.

## 8. Historical real-candidate-flow build hold (superseded in part)

The following list records the historical pre-decision conclusion. It is
preserved as historical truth but superseded on 2026-08-05 wherever it treated
real-candidate flow as a prerequisite for engineering construction or
non-capital validation:

- Any new strategy hypothesis, family, variant, sweep, or backtest.
- Any candidate-flow-dependent surface behavior (real approval queue entries,
  candidate lifecycle writes, canonical crossing, transition execution).
- Autonomous scheduling/scout/notification behavior.
- At-scale continuous sweeps, at-scale WFO/OOS volume, and at-scale
  robustness/MC volume.
- Autonomous agent scheduling, prioritization, or factory operation over a real
  research queue.

The historical conclusion was that these could not be built or demonstrated
meaningfully without GO-like, authorized, live candidate flow. Under the
controlling decision, H-004-R2 may now serve as the engineering fixture for
separately authorized idea-intake, scheduling, sweep, WFO/OOS, robustness,
factory, paper/shadow, monitoring, and disabled execution-stack proof. It does
not authorize genuine candidate lifecycle transitions, edge claims, promotion,
live impact, or real-capital deployment.

## 9. What is not authorized

- Resuming edge-search or generating strategies.
- Mutating Strategy Specs, Variant Manifests, Sweep Plans, canonical Result
  Populations, trial logs, candidate registry, or candidate lifecycle records.
- Executing canonical crossing; writing approvals, promotions, or readiness
  declarations.
- Enabling autonomous scheduler / scout / coordinator behavior; firing
  notifications.
- Any paper / live / runtime / OMS / risk / reconciliation / capital / broker /
  exchange / order-path contact, or funding P&L / accounting change.

## 10. Definition of done — no-edge-search lab scope

The lab is "finished as intended" for this no-edge-search, human-driven phase
when:

1. Completed research evidence is legible through a coherent read-only state
   model and operator surfaces (dashboard, brief/report, approval queue). ✅
2. Evaluation rigor is enforced and honest: replay normalization, walk-forward /
   OOS gating, robustness review reach, with withheld statistics shown rather
   than fabricated. ✅
3. Conclusions (including the funding NO-GO) are recorded with full provenance
   and no candidate is fabricated. ✅
4. All autonomous / write / execution capability is structurally inert and
   default-off behind explicit authorization. ✅
5. This completion map exists and pins the phase boundaries. ✅

"Done" for this phase explicitly **excludes** generating new edges, promoting a
candidate, running anything live, or declaring an always-on autonomous research
factory complete. Those are future, separately authorized phases or held-B
layers, not unfinished business of this one.

Current final decision state after the known-payload proof sequence, final
non-edge-search hardening batch, and deterministic event-tape
operating-readiness route:

- core pipe fixture/plumbing proof: true;
- known-payload proof complete: true;
- non-promotable promotion/crossing rejection proven: true;
- scale-correctness on known payloads proven: true;
- read-only dashboard/reporting/registry visibility hardened: true;
- deterministic event-tape operating-readiness route complete: true;
- operating-readiness acceptance-tested: true;
- bounded real research traffic acceptance evidence exists: true;
- real-input operating layer acceptance-tested: true;
- queue/scheduler dry-run handling acceptance-tested: true;
- notification/report dry-run cadence acceptance-tested: true;
- agent-loop/dashboard stream handling acceptance-tested: true;
- lab complete for known-payload proof, event-tape readiness, and bounded
  real-traffic acceptance evidence: true;
- lab declared finished without qualification: false;
- production autonomous operation declared: false;
- bounded real research traffic started: true;
- GO-like / candidate-worthy evidence surfaced: false;
- edge-search authorized here: false;
- candidate authority created: false;
- crossing authority created: false;
- paper/live authority created: false;
- always-on factory completed: false;
- at-scale/autonomous layers: historical real-candidate-flow hold superseded for
  separately authorized dummy-based engineering/non-capital validation; real
  promotion and capital activation remain genuinely candidate-gated;
- first performance/promotion/real-capital crossing: held until a genuinely
  qualified candidate and explicit gate exist;
- paper/live/runtime: GO-gated and protected;
- further engineering-readiness packages may be authorized when they add new
  dummy-based infrastructure, capacity, observability, or safety proof without
  claiming edge or capital authority.

The remaining operator choices are:

1. Hold the completed no-edge operating-readiness lab.
2. Authorize a separate future research or operator-surface package under
   explicit scope and stop conditions.

This map does not recommend which choice to make.

## 11. Final Side 12 capability map

This section is the authoritative final Side 12 capability map for the
no-edge-search phase. `canonical_authority_created` records whether repo truth
already contains canonical authority for the relevant surface; this package
creates none.

The proof statuses and historical evidence gaps in this table remain unchanged.
Any "real traffic" or "real candidate" remaining condition is an evidence or
performance boundary, not a blanket prohibition on separately authorized
dummy-based engineering construction/non-capital validation under the
2026-08-05 controlling decision.

| ID | Capability | Final status | Proof basis | Remaining condition |
| --- | --- | --- | --- | --- |
| 1 | Idea intake | `complete_for_no_edge_phase` | Human-driven intake and evidence organization are sufficient for the no-edge phase. | Real idea intake resumes only with explicit real research traffic. |
| 2 | Automatic strategy formalization from arbitrary ideas | `not_applicable_to_no_edge_phase` | Arbitrary strategy formalization is edge-search / generation work. | Explicit edge-search authorization. |
| 3 | Strategy-family classification and routing | `proven_on_known_payload` | PR #583 and PR #588 route the `known_losing_baseline` construction lineage through known-payload proof. | Real multi-family traffic for autonomous routing claims. |
| 4 | Data / primitive / feature availability classifier | `held_B_needs_real_research_traffic` | Existing blockers and withheld states are visible, but known payloads do not exercise real feature-discovery demand. | Stream of real research jobs with varied data/primitive needs. |
| 5 | Strategy Spec draft generation | `not_applicable_to_no_edge_phase` | PR #583 intentionally did not create schema-valid draft specs because exact construction provenance would need schema changes. | Explicit strategy-generation / schema path authorization. |
| 6 | Variant Manifest / parameter generation | `proven_on_known_payload` | PR #588 proves deterministic scale rows for one non-promotable lineage without candidate authority. | Real variant traffic for edge-search work. |
| 7 | Sweep Plan generation | `proven_on_known_payload` | PR #588 proves full-denominator synthetic population shape for known-payload sweep accounting. | Real sweep plans under explicit research authorization. |
| 8 | Large-scale batch sweeps | `proven_on_known_payload` | PR #588 materializes 600 scratch-only rows across completed, failed, invalid, blocked, insufficient, and withheld states. | Real at-scale batch execution over real research jobs. |
| 9 | Full result-population preservation including failures / blocked / invalid / data-unavailable rows | `proven_on_known_payload` | PR #588 preserves all 600 known-payload rows and status denominators. | Real traffic to prove continuous denominator preservation under live research variety. |
| 10 | Run registry / result store with provenance, lineage, validation status, blockers, and run history | `complete` | PR #589 inventories canonical, scratch, fixture, docs-only, and blocked/deferred entries with provenance and validation state. | Real research traffic can expand entries but is not needed to complete no-edge visibility. |
| 11 | WFO/OOS execution | `proven_on_known_payload` | PR #584 hardens non-promoting WFO/OOS gate semantics and PR #588 carries known-payload status accounting. | Real candidate WFO/OOS volume. |
| 12 | Monte Carlo / robustness computation | `proven_on_known_payload` | PR #584 hardens robustness/MC withheld/advisory behavior and PR #588 preserves those statuses in known-payload population proof. | Real robustness volume over real candidates. |
| 13 | Anti-overfit review across full result populations | `proven_on_known_payload` | Full-denominator known-payload preservation prevents winner-only interpretation for fixture proof. | Real populations and real selection pressure. |
| 14 | Dashboard coverage | `acceptance_tested_by_event_tape` | PR #590 adds baseline proof and held-boundary panels; PR #595 acceptance-tests dashboard state transitions over operating-test traffic with operating-test labels present and real-research labels absent. | Real research dashboard operation requires real research traffic. |
| 15 | Daily operator brief | `acceptance_tested_by_event_tape` | PR #594 acceptance-tests deterministic daily-window reporting over the event tape with two daily windows. | Real recurring production cadence requires real research traffic. |
| 16 | Weekly performance / research report | `acceptance_tested_by_event_tape` | PR #594 acceptance-tests deterministic weekly-window reporting over the event tape with one weekly window. | Real recurring production cadence requires real research traffic. |
| 17 | Notification system | `acceptance_tested_by_event_tape` | PR #594 acceptance-tests dry-run notification rendering and matched notification actions while real sending remains false. | Real notification sending requires real jobs/events plus explicit firing authorization. |
| 18 | Bounded research-agent loop | `acceptance_tested_by_event_tape` | PR #586 proves no-candidate behavior on `known_losing_baseline`; PR #595 acceptance-tests bounded agent action handling over the 10-job / 40-event operating-test stream with no rescue, retuning, ranking, readiness, or promotion recommendation. | Real autonomous research loop operation requires real research traffic and explicit authorization. |
| 19 | Agent scheduling and prioritization over a research queue | `acceptance_tested_by_event_tape` | PR #593 acceptance-tests queue/scheduler dry-run handling and deterministic priority ordering while autonomous scheduler activation remains false. | Production prioritization requires real research queue traffic. |
| 20 | Research queue / job orchestration / resource limits | `acceptance_tested_by_event_tape` | PR #593 acceptance-tests queue/scheduler dry-run handling, including resource-limit, blocked, delayed, and terminal behavior. | Production operation requires real research queue traffic. |
| 21 | Candidate lifecycle gate maturity for real candidates | `needs_real_GO_candidate` | Non-promotable rejection / no-admission behavior is acceptance-tested, and PR #595 records `candidate_admitted=false`; no real GO candidate exists. | A real candidate reaching human review under explicit authority. |
| 22 | First real candidate crossing | `needs_real_GO_candidate` | PR #585/#586 prove `reject_by_construction`, not real crossing. | A real GO candidate and explicit crossing package. |
| 23 | Paper/live path | `GO_gated_protected` | Paper/live/runtime paths remain protected and untouched. | Explicit GO decision under protected runtime gates. |

## 12. Supersession of the prior non-winning-strategy conclusion

Historical pre-decision conclusion (preserved): known, non-winning,
non-promotable payloads
are appropriate for proving lab machinery before edge hunting. The boundary is
that PR #586 and PR #588 already consumed that class of input at single-pipe and
scale levels.

A non-winning / non-promotable strategy and a non-promotable baseline
construction payload are the same class of lab input for current proof purposes:
both are known-outcome, non-promotable inputs, and both must terminate as
no-candidate / `reject_by_construction`. PR #586 proved that path end-to-end for
`known_losing_baseline`. PR #588 proved scale-correctness for the same class with
600 denominator-preserved rows. Running another non-promotable strategy through
the same path would be re-proof, not new capability completion. The remaining
held-B capabilities require streams of real research jobs, not one known-outcome
payload.

That conclusion is superseded on 2026-08-05 as a limit on *new engineering
proof*. H-004-R2 is now the designated engineering fixture and may establish new
infrastructure, integration, capacity, observability, safety, paper/shadow,
monitoring, factory, and disabled-stack proof under separately authorized
packages. Repeating proof already established remains unnecessary, but the
dummy's non-winning status is not itself a blocker to new engineering scope.

The historical and current conclusions make no real-edge claim, recommend no
strategy family, and authorize no edge-search, GO, promotion, live impact, or
real-capital operation. H-004-R2 remains structurally GO-forbidden and its
engineering evidence is not strategy-performance evidence.

## 13. External adoption runway final state

External runway surfaces remain non-authoritative and do not become execution or
evidence authority through this map.

| Surface | Final state |
| --- | --- |
| workflow-gen | No new adoption WP is identified; any further use belongs to real research traffic / idea-generation phase. |
| analytics metrics | Dashboard/reporting surfaces are hardened; no new adoption WP is identified unless real research reporting expands. |
| robustness MC | Gate posture, withheld/advisory behavior, and known-payload denominator proof are complete for no-edge; real volume belongs to real research traffic. |
| vectorbt | Non-canonical sidecar only; no new adoption WP without explicit edge-search / triage authorization. |
| CCXT | Public data / funding adapter runway only; no new adoption WP without real data or research need. |
| Nautilus | Historical Side 12 posture retained; CPW-MIG-00 prospectively permits separately authorized non-capital N1/N2/N3 proof before GO, without granting trading or economic authority. |

## 14. Drift guardrails

- **No edge-search drift.** "Finish the lab" never means resume strategy
  generation or hypothesis search. A NO-GO conclusion does not authorize a new
  cycle.
- **No execution-machine drift.** Read-only surfaces never gain run / approve /
  promote / retry / scheduler-toggle controls through this map. Deferred-B
  engineering work requires a separate package; dummy-based non-capital
  validation may be authorized, while live-impacting/performance/real-capital
  activation still requires its genuine candidate evidence and protected gates.
- **No authority-by-existence.** No surface, fixture, manifest, scheduler entry,
  dashboard, or stored artifact infers authority from its own existence.
- **No authority by engineering work.** Historical no-edge map work was
  read-only by default. Separately authorized engineering packages may build
  within their exact scope, but must remain deterministic/non-authoritative in
  non-capital modes and preserve protected boundaries (OMS, risk,
  reconciliation, kill-switch / safe-mode, Tier 4, `lib/`, `src/`, `configs/`,
  `.claude/`, `data/`, permanent human gates) unless a later protected package
  explicitly authorizes a narrower change.
- **Human gates are permanent.** Any movement toward candidate promotion, R2S /
  S2P, paper/live, or runtime remains human-gated under existing locked gates.
