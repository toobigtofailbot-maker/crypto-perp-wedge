# Gate C contract

The writer requires a JSON object with schema version `gate_c_strategy_spec_approval_v1`, a stable approval ID and timestamp, `approved_by=Karl`, exact scope `one_append_only_canonical_strategy_spec_write`, `content_reviewed=true`, `authorizes_canonical_write=true`, `append_only=true`, and `exact_content_and_target_only=true`.

It binds the exact proposed file bytes through `approved_content_sha256`, the exact non-existing canonical target, the draft ID, independently validated draft/review/eligibility artifacts, and the draft packet's exact idea/formalizer source hashes. Strategy Spec `provenance.source_refs` must exactly encode those three path/hash references plus the Gate C approval ID. The approval ID is permanently single-use. Queue, execution, candidate lifecycle, promotion/readiness, paper/live/runtime, scheduler/autonomy, and notification authority flags must all be false. Any missing field, stale source, mismatch, malformed artifact, collision, or wrong actor/scope stops before writing.

Command:

```powershell
python -m tools.canon_intake.spec_writer --proposed-content <frozen-spec.json> --gate-c <gate-c.json> --repo-root <repo>
```
