# Repo-truth discovery

- Base: `origin/main` at `03dac33`; PR #649 merged the advisory eligibility validator prerequisite.
- Control-plane design: `docs/architecture/scratch_to_canonical_intake_control_plane.md` defines Karl-only exact-content Gate C, the target convention, and a physically separate writer.
- Canonical target convention: `research/strategy_specs/STRAT-SPEC-NNNN.strategy_spec.json`; existing IDs end at `STRAT-SPEC-0006` on the package base. The writer accepts only the exact new ID/path approved by Gate C and never allocates an ID itself.
- Structural authority: `research/schemas/strategy_spec.schema.json` plus `tools/registry/validate_strategy_specs.py`.
- Review/eligibility inputs remain scratch evidence. `eligible_for_gate_c_review`, `reviewed`, and `flagged_for_canonicalization` grant no write authority.
- No real Gate C artifact was supplied. This package therefore writes no production Strategy Spec; tests exercise only isolated temporary repositories.
