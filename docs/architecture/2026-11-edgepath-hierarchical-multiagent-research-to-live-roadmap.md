# EdgePath — Hierarchical Multi-Agent Intelligence to USD-M LIVE Trading

**Status:** OWNER-PROPOSED IMPLEMENTATION ROADMAP; planning only. Not an implementation WP, architecture supersession, data-use approval, research-execution approval, capital allocation, or trading activation. Karl approves/merges separately.

**Repository snapshot used for planning:** \`40034f3c7b15fcc26aa410a0bcb560653f67901e\` (PR #773 and PR #774 merged, no open PRs when this plan was drafted). Refresh \`origin/main\` and all active PRs before every subsequent WP. This snapshot is evidence, not a permanent base pin.

**Permanent workflow:** **EdgePath** — the shortest evidence-backed path to a sophisticated, autonomous, multi-symbol Binance USD-M perpetual trading system capable of discovering, validating, executing, and continuously improving *net-of-cost* trading advantage. Profitability is an objective, not an engineering promise.

## 1. Product target and non-negotiable distinctions

The target is **one master intelligence with specialist agents**, not a majority-vote committee and not an LLM directly issuing leveraged exchange orders.

1. **Research master:** Extreme Hermes directs persistent specialists and delegated researchers; selects legal opportunities, research tasks, and next experiments under an approved immutable scientific envelope after Stage 5B activation. Human input is not required per *legal in-envelope research job* once that envelope is activated. Prefect owns durable job execution; CPW owns science and lineage.
2. **Portfolio-intelligence master:** Hermes synthesizes independent, causally timed specialist recommendations and proposes an explicit, explainable portfolio decision across a configurable Binance USD-M universe. Initially **shadow/advisory only**, independently scored versus a deterministic baseline. No new power to promote strategies, size live capital, or send orders is implicit.
3. **Deterministic trading plane:** CPW-approved strategy eligibility, hard risk, account truth, economic controls, safe mode and recovery decisions gate any target; NautilusTrader owns native order, fill, position and account mechanics. Never put an LLM in the tick-by-tick OMS, risk kill-switch or exchange acknowledgment loop.
4. **Continuous feedback:** actual execution quality, funding, fees, drawdown, latency, realized net P&L, and agent/model cost inform Hermes's next **research** decisions. A recommendation never silently updates a live model or risk policy.

**A live-trading authority decision is OPEN, not silently decided here.** D2-024/D2-025 presently permit Hermes as a persistent research director and later paper/LIVE *observer-advisor*, **not** an autonomous economic authority. A separately reviewed owner decision must specify whether and how an approved, bounded advisor output can influence paper/LIVE portfolio targets through a CPW-owned policy and promotion gate. Until then, agent decisions are shadow/advisory artifacts only.

Do not equate: multi-symbol metadata ≠ physical scientific result; test-only scientific fixture ≠ genuine study; multi-symbol CPWSIM ≠ authenticated testnet; agent consensus ≠ predictive edge; upstream installation ≠ working CPW adoption; passing software tests ≠ profitability.

## 2. Verified starting state and current gaps

| Component | Merged evidence at snapshot | Not established |
| --- | --- | --- |
| Lane A / PR #774 | Versioned M1 historical candidate contracts, BTC/ETH 15m/1h source/economic bindings, bounded public USD-M probes, custody and owner-signature *verification*, TEST_ONLY M1 science plumbing | Genuine approved historical M1 study execution is intentionally blocked; 0/4 physical BTC/ETH x 15m/1h accepted Result Populations; historical integrity findings and funding limitations remain |
| Lane B / PR #773 | Native NautilusTrader two-symbol offline CPWSIM portfolio fixture, repeated target adjustments, common account, simulated fees, native observations and restricted read-only recovery | Real private Binance testnet account/order/fill reconciliation, funding/margin economics, generalized multi-cycle recovery, sustained paper, or LIVE |
| Hermes | D2-024/D2-025 locked target, F1/F2 isolated canary proof, specialist profiles and delegation proof, Project-Evidence tools, manual 02A–02K cohort preparation/replay and broker safety foundation | Persistent production research organization, live model-authored continuous cycles, Stage 5B activation, functioning research-to-portfolio decision consumer |
| Existing real upstream use | CPW imports/calls real Optuna, Prefect, CCXT, DuckDB, Nautilus; VectorBT isolated/triage pilot | Full autonomous end-to-end use of those components as one factory |
| Unconsumed priority upstream | Research and selected future integration of TradingAgents, RD-Agent, Qlib, skfolio, AlphaGen, QuantaAlpha, Cryptofeed | Pinned, runnable upstream implementation producing output that a CPW consumer verifiably uses |

The 57-repository adoption register is a full accountability universe, **not** a mandate to run 57 production services. Every candidate needs a documented operational disposition: WORKING_CONSUMED, ISOLATED_BENCHMARK, DEFERRED_WITH_TRIGGER, or REJECTED_WITH_EVIDENCE. Do not relabel source research or a bespoke reimplementation as adoption.

## 3. Target intelligence flow and explicit owners

\`\`\`text
Time- and source-qualified USD-M universe / live observations
  -> Hermes persistent director (research sandbox; no exchange secrets)
       -> independent market/regime specialist
       -> technical and quantitative signal specialist
       -> order-flow / funding / liquidity specialist
       -> macro/news/sentiment specialist
       -> TradingAgents upstream analyst / bull-bear / portfolio-debate graph
       -> RD-Agent upstream factor/model iteration + Qlib datasets/models/predictions
       -> skeptical statistics / leakage / robustness critic
       -> portfolio/correlation/capacity specialist (skfolio only when useful)
       -> operational and execution-quality specialist (read-only)
  -> Hermes structured master synthesis: sources + as-of + dissent +
     conflicts + uncertainty + budget + expiry + recommended research/portfolio idea
  -> [RESEARCH] CPW scientific authority / durable lineage / Search Governor / Optuna
                -> Prefect scientific worker -> RP, OOS, WFO, MC, costs -> memory/feedback
  -> [TRADING ADVICE] versioned non-authoritative portfolio recommendation
                -> CPW candidate-eligibility, economic and policy boundary
                -> (paper/LIVE only after separate owner-approved crossing)
                -> Lane B native Nautilus -> orders/fills/account/reconcile
                -> actual net results -> immutable feedback -> Hermes research
\`\`\`

**Two clocks, not one monolithic agent loop.** Fast data, qualified model signals, order handling, risk enforcement and venue recovery use deterministic code. Slower evidence-rich Hermes research and portfolio deliberation run asynchronously at budgeted, causal decision points. Do not invent a fixed cadence or latency target without measurements.

**Specialists are roles, not compulsory always-on processes.** Start with real persistent Hermes profiles (director, scout, critic) and genuine TradingAgents upstream debate, then expand to quantitative, microstructure, portfolio and performance roles based on measured incremental benefit. Roles must have distinct data/evidence responsibilities, no inherited capital credentials, bounded parallelism, and no unsourced voting. A master output must show how dissent was resolved and permit HOLD / FLAT / NO_OPPORTUNITY.

**Typed evidence contract, not generic free text.** Initial non-authoritative schema must record: exact repo/source/model versions, as-of time, data availability and causal freshness, USD-M symbol/instrument identities, optional strategy/candidate IDs, independent specialist inputs and receipts, conflicting hypotheses, recommendation, confidence/calibration if measurable, valid-until, prior trial ancestry, research/compute cost, and **not_authority=true**. This is a provisional interface shape; file and schema ownership are decided by the first actual producer/consumer WP, not by this roadmap.

**Specialist and upstream ownership:**
- Hermes: intelligence, research delegation, synthesis, operational working memory; upstream Bot/profile/delegation/skills first, no second custom generic agent runtime.
- TradingAgents: call real upstream \`TradingAgentsGraph\` and \`propagate\` or pinned verified successor API; preserve useful upstream role/debate/checkpoint behavior; replace stock-centric data assumptions with source-qualified crypto tools. Its own simulated transaction or risk approval never grants CPW economic authority.
- RD-Agent: execute actual pinned upstream quantitative RD loop/factor or model generation, not a CPW-written imitation.
- Qlib: use actual upstream data loader, dataset/model training/prediction APIs; ensure predictions are timestamped and generated out-of-sample relative to training.
- Optuna: proposals only under CPW Search Governor, not independent scientific budget authority.
- Prefect: durable experiments, claims, idempotency, retry/recovery; Hermes routines wake intelligence and must not become a competing scheduler.
- skfolio: actual upstream portfolio experiments and optimization only when qualified independent return streams exist; compare with a simple baseline.
- AlphaGen / QuantaAlpha: isolated, pinned factor-generation benchmarks after an RD-Agent/Qlib working path; promote only if independent diversity or net scientific value.
- Cryptofeed: optional isolated streaming microstructure worker **only** where actual consumer requires it; Python >=3.13 and AGPL-3.0-or-later demand environment and licensing review before distribution/commercial architecture choice. Never place its dependencies into the pinned Nautilus environment by default.
- NautilusTrader (Lane B): execution, orders, fills, native account, native venue APIs and supported persistence; CPW owns whether recovered state is safe to trade.
- CPW: scientific admission, canonical records, lineage/holdout, eligibility, hard risk, overlays, reconciliation acceptability, all promotion and economic/capital gates.

## 4. Bundled implementation runway — 8 conditional capability packages, not 8 mandatory PRs

**B0 baseline is already merged (#773/#774).** Prepare WPs from the latest merged state; exact scope, branch, changed-file owners and acceptance fixtures come from predraft inspection.

| Priority / bundle | Owner; may run alongside | Delivered working outcome, minimum proof | Not permitted / stop rule |
| --- | --- | --- | --- |
| **A1 — Hermes Master-Intelligence SHADOW vertical** | Lane A; parallel to A2 in a *separate non-overlapping worktree* | Bring F1/F2 persistent noncapital specialist organization into controlled actual operation; invoke **real** pinned TradingAgents research graph with source-qualified USD-M BTC/ETH/third-symbol historical/as-of inputs; director synthesizes at least multiple independent specialist reports into typed, timestamped shadow decisions; run replay, disagreement, provenance, tool containment, agent/model cost and latency; evidence proves CPW ingests the output as non-authoritative advisory data. Prefer one substantial WP encompassing deployment + real upstream call + CPW consumer, not an installation-only PR. | No private/live credentials, autonomous scientific trials, candidate promotion, OMS/risk edits or shadow-to-order route. If protected crossing needed, isolate the decision. |
| **A2 — Genuine M1 historical science** | Lane A; parallel to A1 with different file ownership | Connect merged M1 source/custody/governed science to a lawful real study path. Minimum **one physical non-BTC ETH** study, then BTC/ETH x 15m/1h four complete Result Populations with all trials/failures, funding/fee/slippage sources and OOS/holdout discipline. One coherent engineering WP; actual byte reads, Gate C, owner-signed study and physical runs require exact separate authorizations. | Do not count TEST_ONLY or public-data discovery as real science. If the original approved acceptance definition does not allow engineering-only merge, obtain a narrow owner amendment; never self-waive. |
| **B1 — Native authenticated multi-symbol testnet readiness** | Lane B; parallel to A1/A2 | Reuse Nautilus's **real** Binance private APIs for account/order/fill discovery, partial fills, instrument filters, reconnect, funding/margin, native events, source-bound reconciliation and CPW fail-closed recovery; default OFF and testnet-only. One substantial engineering/physical-acceptance WP; offline adversarial tests first and exact owner approval for credentialed testnet actions. | No custom duplicate OMS, broad automatic recovery based on P1 three-fill proof, real capital or live fallback. |
| **A3 — Upstream quantitative alpha worker** | Lane A; after A2 first legitimate science consumer, or do isolated non-authoritative integration earlier | **Actual RD-Agent + Qlib** worker outputs real features, factors, models, timestamped predictions and failure evidence which CPW can ingest/evaluate; causal train/validation/test windows, baseline comparison, version/pin, cost/time budgets and complete rejected trials. One capability WP for first end-to-end CPW-consumed result, not independent 'install RD-Agent' and 'install Qlib' WPs. | No factor numerics misrepresented as executable strategy, no model-free synthetic profitability, no fork rewriting their internals. |
| **A4 — Hermes-led closed-loop autonomous research** | Lane A; after A1+A2+A3 evidence and approved envelope; may bundle with A3 only if gates already ready | Real repeated director -> specialists -> legal contract -> Governor/Optuna -> Prefect -> CPW science -> critique/memory -> next legal research action. Explicit Stage 5B acceptance and owner's activation are **separate** from merging engineering. Must prove restart/recovery, cumulative denominator, negative results, budgets, agent-cost controls, invalid/expired envelopes, and no unauthorized successor. | No cron as scientific job owner; no self-enlarged envelopes, holdout reset, unauthorized scientific opens, candidate promotion or economic authority. |
| **J1 — Qualified portfolio advice and paper integration** | Joint: Lane A decides upstream eligibility/advice, Lane B implements target adapter and execution | Use independent net-of-cost scientific returns (skfolio if comparative proof warrants), candidate qualification, frozen target contract, causal risk/capacity and portfolio selection; match actual Lane A producer to Lane B Nautilus consumer. First run SHADOW on multi-symbol market timeline, then separately authorized repeated native paper/testnet; compare with same-market deterministic baseline. Strong candidate for one joint interface-driven release, using disjoint file ownership and one accountable integrator. | TradingAgents vote or Hermes free text never bypasses promotion or hard risk. A new economic decision crossing requires a distinct architecture/owner approval *before* coding into protected paths. |
| **J2 — Forward economic feedback + continuous strategy health** | Joint; after J1 real paper evidence | Evidence ledger of native fills, funding, commissions, slip, mark/realized P&L, drawdown, exposure, latency and reconciled trades; strategy/agent/version attribution; Hermes read-only performance specialist proposes research follow-ups; reporting daily/weekly; A/B comparison of baseline vs agent-enhanced decisions. Prefer one operational workstream instead of separate dashboard/report/monitoring micro-WPs. | No performance fabrication, automated live strategy changes, independent execution authority, or duplicate canonical P&L store. |
| **L1 — LIVE pilot readiness and conditional small-capital activation** | Owner-led joint; only after independent paper economics and robust B1/J1/J2 | Exact operating runbook, complete venue reconciliation, margin/liquidation stress, safe recovery/flatten, runtime monitoring, kill/HOLD, rollback and capital exposure limits. If and only if source-backed strategy edge and operational safety merit it, Karl may authorize an explicitly capped LIVE pilot and observe net performance. | Never bundle unrestricted capital authority into an ordinary coding WP. A failed readiness gate blocks LIVE; it does not erase failed evidence. |

**Expected shape:** about 5–7 meaningful engineering PRs before a separate LIVE decision, *not* eight serial PRs. A1, A2, B1 are parallelizable with disjoint worktrees; A3 can prepare worker installation/adapter independently but its scientific claim waits for A2; A4 Stage 5B and J1 economic crossing are distinct gates. Merge outcome-based code WPs where source/file ownership and evidence make that safe; never combine independent protected authorizations merely to reduce PR count.

**Avoid serial drift:** after the first noncapital A1 integration, do not pause agent progress while every M1 historical data gap is solved. Conversely, do not run more agent debates endlessly while native science and real trade economics remain absent. Advance both, using independent workers and explicit freeze points.

## 5. Entry/exit contracts: what must be proved, not merely described

**All upstream-adoption claims require a five-link proof:** (1) exact license/version/commit and import or process invocation; (2) named upstream function/class *actually executed*; (3) raw immutable output and test fixture (no credentials); (4) named CPW consumer reading/using it correctly; (5) baseline or comparative evidence of real purpose, cost/latency and failure handling. A copied workflow or substitute Python function is not upstream adoption.

**Master-agent decision value:** conduct a prospective-as-of, same-universe and same-cost comparison:
- C0: deterministic qualified strategies/portfolio without agent overlay;
- C1: same portfolio with individual specialists as read-only signals;
- C2: full Hermes master synthesis;
- negative control: stale/irrelevant/contradictory agent reports.

Account for all ideas investigated, unexecuted and rejected; prevent lookahead and multiple-testing leakage; track calibrated value when defined; compare net returns after fees, funding, slippage, margin, API/model compute cost, drawdown and capacity. If C2 fails to improve measured incremental value, do **not** grant the master greater economic influence. Retain only beneficial advisory/research use.

**Data and universe:** general USD-M symbol/config admission, not a permanent BTC/ETH cap. BTC/ETH x 15m/1h is the M1 minimum *acceptance evidence*, third symbol must be configurable without coding. Public market availability is not historical/custody proof. Microstructure, streaming and lower clock speeds are only added where an alpha consumer and realistic latency economics justify them.

**Agent economics:** record specialist accuracy/calibration when measurable, novelty and incremental predictive content, dissent, latency, provider tokens and dollar cost, research budget, duplication ratio, completed trials and failure rate. More agents are not automatically better.

**Runtime economics:** net of funding/fees/slippage, correlated exposure, effective market depth, basis/liquidation stress, downtime, reconciliation errors, restart state, and capital utilization. Profit is not implied by a positive backtest. No numeric performance targets or go-live date are invented by this planning record.

**Economic crossing decision (required before J1 capital-bearing implementation):** owner must explicitly decide if Hermes may influence **already qualified** strategy selection/allocation; maximum influence, allowed instruments, decision TTL, human review cadence, rollback, escalation and independent deterministic approval path; never direct order submission. This is a design/authority gate, not something Codex may decide through implementation.

## 6. EdgePath coding workflow — mandatory on EVERY WP and coding follow-up

1. **Owner/Side prep:** refresh merged repo, relevant PRs, actual changed-file owners, primary dependency and the first measurable working user capability. Avoid drafting a WP if the next prerequisite is a specific owner permission or already-merged feature.
2. **Ponytail FIRST:** locate and genuinely invoke \`$ponytail\` at the beginning of **each** Codex coding WP **and every coding follow-up**; do not confuse writing the instruction with using the skill. Verify installed skill names and current versions; never claim missing skill usage.
3. **All other four mandatory skills every time:** \`$wp-predraft-inspector\` (real source/file/authority recon), \`$wp-minimum-test-plan\` (focused/adjacent/full validation and meaningful exit), \`$wp-one-shot-review\` (semantic scope, changed files, forbidden touches), \`$verification-before-completion\` (exact source and raw test evidence). Use them at their proper task stages, including follow-ups. Invoke relevant *available* specialist skills for upstream-source reuse, scientific correctness, prompt/model provenance, finance invariants, Docker isolation, security, systematic debugging, release and PR evidence; inspect the actual local skill inventory.
4. **Use a single designated write-authorized agent per worktree.** Parallel **read-only** agents may research, critique and design tests. Lane A / Lane B use separate worktrees; share interface agreement rather than mutate one another's live branch. Record writer ownership; if collision, preserve everything and stop competing writes before recovery.
5. **One Codex owner outcome, not a micro-WP chain.** Supply the objective, actual source entrypoints, dependencies, allowed/forbidden files, exact protected gates and measurable acceptance. Codex autonomously edits, tests, diagnoses and fixes routine in-scope failures until final validation. Do not stop for each import error, ordinary fixture issue or intermediate test. The same blocker twice triggers a root-cause investigation, not a third identical continuation.
6. **One complete evidence ZIP** from the executor on DONE, BLOCKED, FAILED or PARTIAL, including actual changed-file inventory, base/head, upstream call proof, skills receipts, raw test commands/outcomes, missing inputs, impact on science/economics, PR ref, checksums and forbidden-scope check. Side independently inspects exact diff/blobs, not just a summary.
7. **Minimal owner reporting:** if merge-ready, respond \`MERGE PR #XXX\` and at most 2–3 factual sentences; no additional owner merge-note/assessment files. If blocked, one precise authority decision. If coding fix needed, smallest *same writer/same PR* follow-up, with all five mandatory skills again.
8. **Validation:** label ENGINEERING_READY, SCIENTIFIC_PENDING, SHADOW_ONLY, PAPER_TESTNET_READY, or LIVE_AUTHORIZED accurately. Hosted smoke is not full T3; fixture outputs are not scientific truth. Do not modify validators or narrow test profiles to manufacture PASS. Full validation class follows repo rules.

**Skills are mandatory, not the deliverable.** Never extend a WP just to create procedural reports or load the complete 57-repo research register into each coding context. Use concise source pointers and stage-specific skills.

## 7. Cross-lane ownership and PR discipline

- **Lane A owns:** Hermes/Bot organization; TradingAgents and RD-Agent/Qlib research workers; data/science preparation; source custody; Governor; Prefect research orchestration; Research Memory and non-authoritative master decision advice; strategy/portfolio *qualification*; noncapital performance interpretation.
- **Lane B owns:** Nautilus native venue clients, multi-symbol order/position/account mechanics, authenticated testnet, execution-quality observations and full-lifecycle reconciliation proof; protected runtime change requests only under explicitly authorized scope.
- **Joint interface:** propose once, before separate consumers diverge. Each file has exactly one designated writer. Cross-lane changes require named owner, agreed schema version and test compatibility on both sides, not a shared mutable worktree.
- **Karl alone owns:** merging; protected data/custody/signing access; Stage 5B activation; strategy promotion; economic-policy or risk change; testnet credentials/action permission; and LIVE capital.
- **No separate custom agent runtime, scheduler, OMS, reconciliation ledger, research-science authority or result-truth store.** Reuse the existing upstream owners, and retire old duplicate machinery only after tested parity.

## 8. Immediate sequencing and decision checkpoint

**Before coding:**
1. Merge/accept this docs-only roadmap if it matches owner intent; do not interpret the merge as signing the open economic decision.
2. Side 25 Lane A prepares **A1 and A2** with exact non-overlapping file lists and preverified permissions, rather than another whole-architecture writeup. If they conflict on actual scientific files, serialize only that overlap. A1 should directly call real upstream TradingAgents and existing Hermes, not invent a new multi-agent coordinator.
3. Side 25 B prepares **B1** on separate worktree, based on merged #773; native Binance private testnet integration default OFF. Request a precise physical-testnet permission only when a controlled test profile and expected action list are ready.
4. Lane A establishes the narrow non-authoritative master-to-portfolio interface shape with Lane B and documents its **owner-economic-authority decision** separately before any agent advice can affect actual positions.
5. Once A2 yields legitimate non-BTC scientific results, Lane A delivers **A3 actual RD-Agent/Qlib outputs**; A1 shadow comparisons can start before that, but cannot claim real strategy performance from agent prose. Then activate A4 only after Stage 5B gates.

**Shortest correct completion evidence:** (a) real Hermes and TradingAgents specialists producing a time-bound master advisory decision on public noncapital USD-M data; (b) genuine non-BTC research population; (c) native multi-symbol testnet fill/reconciliation under owner permission; (d) measured incremental research/decision value and qualified paper net economics; (e) independently justified controlled LIVE authorization. No UI-only, audit-only or BTC-only end states.

## 9. Source-of-truth index / external source review

Repo controls (all at planning snapshot unless otherwise noted):
- \`AGENTS.md\`
- \`docs/architecture/2026-10-extreme_hermes_autonomous_research_director.md\` (D2-024)
- \`docs/architecture/2026-10-extreme_hermes_capability_coverage_and_orchestration_ownership.md\` (D2-025)
- \`docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md\`
- \`docs/architecture/LONG_TERM_SCOPE.md\`
- \`tools/hermes/config/config.f1f2.yaml\`; \`tools/hermes/research_cycle_coordinator.py\`
- \`tools/research_autonomy/m1_source.py\`; \`tools/research_autonomy/historical_source_gate.py\`; \`tools/research_autonomy/m1_study_authorization.py\`
- \`tools/data_ingestion/m1_public_source_probe.py\`
- \`src/execution/nautilus_portfolio_contract.py\`; \`src/execution/nautilus_native_backend.py\`
- PRs [#773](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/773) and [#774](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/774).

Upstream verification pointers (examples; *recheck immutable pins/licenses inside each WP*):
- [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents): Apache-2.0, \`TradingAgentsGraph\`/\`propagate\`; stock-centric adapters need crypto-appropriate data; upstream output is not CPW approval.
- [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent): genuine quant RD loops/factor/model work, pin and test runnable dependencies before promising integration.
- [microsoft/qlib](https://github.com/microsoft/qlib): MIT, use actual dataset/model/prediction APIs and causal splits.
- [bmoscon/cryptofeed](https://github.com/bmoscon/cryptofeed): Python >=3.13 and AGPL-3.0-or-later in current available metadata; assess license/deployment obligations and isolate interpreter.
- [skfolio](https://github.com/skfolio/skfolio), [AlphaGen](https://github.com/RL-MLDM/alphagen), [QuantaAlpha](https://github.com/QuantaAlpha/QuantaAlpha): source/pin/licensing/API availability must be checked again before adoption.
- All 57 historically reviewed candidates remain in the existing adoption register; this file is not permission to add every dependency.

**Decision hygiene:** Fact = merged source/test evidence. Target = this roadmap. Open decision = economic authority and any protected new source/Stage 5B/testnet/LIVE permission. A proposed WP is not an executed capability. Losses and failures remain recorded; no optimistic label substitution.
