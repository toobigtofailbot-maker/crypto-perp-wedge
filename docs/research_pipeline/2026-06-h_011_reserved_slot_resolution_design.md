# H-011 Reserved-Slot Resolution Design

## 1. Scope

WP-S2c-136 / WP-12fo is a Tier 1 documentation-only package. It designs options
for resolving H-011's reserved-slot state.

This package creates this design document and updates `docs/project_status.md`
only. It creates no registry change and no H-011 resolution.

This package does not release, preserve, repurpose, promote, register, or
pre-register H-011. It creates no HYPOTHESIS.md, notebook, EXP, REP, trial-log,
OL, REC, DEC, schema, validator, query-view, tool, code, test, runtime, or
protected-path change.

## 2. Authorization basis

Main 4.0 authorized WP-S2c-136 as AUTHORIZED NOW.

WP-S2c-137 is Karl-gated. It cannot be drafted until Side reports this option
set back to Main/Karl and Karl resolves which option, if any, should be locked.

Current merged repo truth is later than the original WP-S2c-136 dependency
wording: WP-S2c-138 is already merged. That later state reinforces the need for
an explicit H-011 resolution before any future candidate-ID use in the second
Path B tranche.

## 3. Repo-truth basis

Direct inspection of `research/candidate_registry.jsonl` records H-011 as a
reserved draft slot:

- `status=DRAFT`
- `overall_verdict=PENDING`
- `pipeline_stage=reserved`
- `strategy_family=cross_asset_regime`
- `timeframe=weekly`
- `information_inputs=[]`
- `free_parameter_count=null`
- `hypothesis_md_path=null`
- `decision_record_path=null`
- `trial_ids=[]`
- notes: slot reserved by WP-6a and full pre-registration plus data procurement
  deferred to a later package.

`docs/research_pipeline/2026-04-candidate_registry.md` records the same
reserved-slot convention: H-011 has no data procurement, no hypothesis file, and
no testing commitment.

H-012 was used for Path B execution instead of promoting or repurposing H-011.
H-012 is now `CONCLUDED` / `NO-GO` with `pipeline_stage=baseline_tested`.

H-011 has no pre-registration, no evidence, no decision, and no trial.

## 4. Problem statement

H-011's reservation has become operationally stale.

Leaving the slot indefinite creates ambiguity for future candidate-ID selection
and Path B sequencing. The ambiguity is now concrete because current merged
repo truth includes a second Path B execution design opening whose
candidate-ID sequencing depends on whether H-011 remains reserved or becomes
available.

The slot needs an explicit resolution, but that resolution is decision-like and
should be Karl-gated.

## 5. Design objective

This design presents clean, bounded options while separating option design from
the locking decision.

It preserves the registry schema, locked criteria, permanent human gates, and
no-readiness authority.

It makes candidate-ID implications explicit for the future WP-S2c-140
registration package without selecting a second Path B candidate and without
resolving H-011 here.

## 6. Option A - release reservation

Under Option A, the H-011 reservation is released.

H-011 may become available for future candidate assignment only if the registry
convention supports reuse or replacement of the reserved row. WP-S2c-137 would
document Karl's decision and make the minimum H-011 registry update required by
schema and convention.

This is not a promotion and not a candidate recommendation. It does not create
a hypothesis, evidence, trial, EXP, REP, OL, REC, DEC, readiness claim, or
transition claim.

If release requires changing the registry schema, changing locked criteria, or
creating a non-minimal registry convention, this option should stop or escalate
instead of being implemented.

## 7. Option B - preserve reservation as-is with explicit rationale

Under Option B, H-011 remains `DRAFT` / `PENDING` / `reserved`.

WP-S2c-137 would document Karl's explicit rationale and may leave the registry
unchanged. This avoids registry mutation but keeps the slot occupied.

If H-011 remains reserved through the second Path B candidate registration
preflight, the Track 3 second Path B candidate should use the next available
non-H-011 ID, likely H-013 unless refreshed repo truth differs.

Preserving H-011 is not a recommendation, not a readiness claim, and not an
implicit decision to activate the cross-asset/weekly idea.

## 8. Option C - repurpose with bounded reservation conditions

Under Option C, H-011 remains a reserved slot but receives clearer purpose,
conditions, or activation prerequisites.

WP-S2c-137 would document what would be required before H-011 can be activated.
Any registry update must remain limited to H-011 and must not pre-register or
promote it.

Repurposing must stay inside the existing schema and locked criteria. If the
repurpose path requires taxonomy changes, timeframe-status changes,
data-catalog changes, data procurement, a hypothesis file, evidence creation,
or promotion/pre-registration semantics, the option should be rejected or
escalated.

Repurposing H-011 is not pre-registration and does not authorize a backtest or
artifact chain.

## 9. Option D - other Karl-directed resolution

Karl may direct another bounded route.

Any such route must be expressible without schema changes, gate automation,
readiness authority, transition authority, ranking/scoring, recommendation
authority, runtime contact, or protected-path contact.

If the route cannot be expressed within those limits, WP-S2c-137 must stop and
escalate rather than improvise.

## 10. Cross-option preservation rules

All options preserve these rules:

- No registry schema change.
- No candidate promotion.
- No hypothesis pre-registration.
- No backtest or evidence creation.
- No locked decision reinterpretation.
- No permanent human-gate weakening.
- No Path B candidate selection.
- No runtime, protected-path, or Tier 4 work.
- No ranking, scoring, recommendation, readiness, transition, approval, or
  paper/live authority.

## 11. WP-S2c-137 locking package shape

The downstream locking package should create:

- `docs/research_pipeline/2026-06-h_011_reserved_slot_resolution_decision.md`
- one `docs/project_status.md` entry

It may modify only the H-011 registry row, and only if Karl's chosen option
requires it.

If the registry changes, full pytest and the registry validator are required.
No other registry rows may change.

WP-S2c-137 is not auto-drafted by this design. It requires Side report-back and
Karl option resolution first.

## 12. Registry-change implications

Release or bounded repurpose may require modifying only the H-011 row.

Preserve-as-is requires no registry modification.

Any need to modify `research/schemas/candidate_registry.schema.json` is a stop.
Any need to modify validators, query views, tools, tests, other candidate rows,
or canonical research artifacts is a stop unless a later explicit package
authorizes that exact scope.

## 13. Candidate-ID implications for second Path B tranche

If H-011 is released before WP-S2c-140 preflight and registry convention
supports using it, second Path B registration may use H-011.

If H-011 remains reserved or unresolved, second Path B registration should use
the next available slot, likely H-013 unless refreshed repo truth differs.

This is operational sequencing, not a Main escalation, per Main's batch
instruction. It does not select a second Path B candidate and does not resolve
the candidate surface.

## 14. Forbidden interpretations

Releasing H-011 is not candidate approval.

Preserving H-011 is not a recommendation.

Repurposing H-011 is not pre-registration.

H-011 status does not determine Path B continuation or termination.

This design does not select the second Path B candidate.

This design does not create readiness, transition, approval, ranking, scoring,
recommendation, policy, paper/live, runtime, or protected-path authority.

## 15. Stop conditions

Stop if any option requires schema change.

Stop if any option weakens, automates, or bypasses a permanent human gate.

Stop if any option requires candidate registration or pre-registration in
WP-S2c-136.

Stop if any option creates readiness, transition, ranking, scoring,
recommendation, approval, policy, runtime, or protected-path authority.

Stop on Karl override.

## 16. Report-back requirement

After merge, Side must report these options to Main/Karl.

WP-S2c-137 is not auto-drafted.

Karl must resolve the option before WP-S2c-137 is drafted.
