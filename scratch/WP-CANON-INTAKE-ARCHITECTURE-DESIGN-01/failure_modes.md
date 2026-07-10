# Failure Modes

| Failure mode | Detection | Required response |
|---|---|---|
| Vague idea becomes canonical | Missing falsifiable mechanism, observable conditions, or disconfirmation | Block; request human clarification or reject. |
| Duplicate family consumes compute | Exact/near match across specs, candidates, concluded families, or Result Populations | Reject exact duplicate; require incremental justification and Karl acknowledgement for near-duplicate. |
| Parameter explosion | More than five free parameters, open ranges, hidden choices, excessive denominator | Block; bound/simplify before Gate C and re-check budget at Gate Q. |
| Untestable feature | No deterministic repo capability or historical reconstruction | Data/feature-block; do not default or approximate silently. |
| Hidden data dependency | Unpinned external/online/paid/runtime/account/order-book input | Block and escalate any requested scope expansion. |
| UI approval weakens freeze | Button/flag/label is treated as approval or content is not hash-bound | Reject approval; require Karl structured exact-content Gate C/Q record. |
| Accidental queue admission | Canonical write implicitly creates queue item or Gate C is reused | Fail closed; require distinct Gate Q with exact hashes and budget. |
| Accidental dispatch/autonomy | Admission invokes runner, scheduler, retry, or successor | Abort; queue writer must prove zero dispatch and no scheduler authority. |
| False edge confidence | Source performance claim or small/incomplete result is presented as evidence | Preserve as unsupported claim; require authorized full-denominator evidence and separate review. |
| Canonical provenance ambiguity | Missing source path/hash, unclear transformation, orphan spec | Block; require bidirectional lineage and source-to-output diff. |
| Hallucinated model logic | Generated entry/exit/feature/claim lacks source or human clarification | Mark generated and block; human must explicitly supply/approve material logic before re-freeze. |
| Approval replay or drift | Actor/scope/hash/target differs, content changes, approval is stale | Reject and require a new exact-content approval. |
| Partial canonical write | Crash leaves ambiguous artifact/receipt state | Future writer must use fail-closed atomic/recovery design and post-write validation; do not treat partial output as canonical. |
| Identifier/path collision | Proposed ID/target already exists or path escapes canonical root | Reject; append-only means no overwrite or alternate-path improvisation. |
| Ambiguity silently defaulted | Multiple plausible interpretations or implicit timeframe/data/risk choice | Block and enter human clarification loop; regenerate and revalidate. |
| Unsupported runtime assumption | Spec relies on paper/live, OMS, broker/exchange, risk, safe mode, or hidden execution behavior | Reject/defer and escalate; protected scope is not available here. |
| Budget bypass | Queue item omits limits or runner expands/retries beyond approved envelope | Reject Gate Q/item; execution must revalidate and hard-stop at bounds. |
| Incomplete denominator/file drawer | Variants are removed after results or failed rows omitted | Invalidate plan/result; preserve all planned and terminal dispositions. |
| Candidate auto-promotion | Result Population or review packet creates/crosses/promotes candidate | Block; candidate decisions remain separate human-gated lifecycle work. |

Any failure that cannot be resolved without schema, validator, query, runtime,
protected-path, or authority expansion stops and escalates to Karl/Main.
