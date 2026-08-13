# WP-GUIDE-ACCELERATION-OPERATING-MODE-01 — Lock accelerated engineering operating model

## Package record

- Decision source: Main's 2026-08-12 immediate research-lab acceleration directive.
- Directive effective date: 2026-08-12.
- Branch: `codex/wp-guide-acceleration-operating-model-01`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/696.
- Package class: T0 — docs/process guidance only.

## Scope and changed files

The package makes the already-decided operating model durable in the central
policy and every active referenced drafting, reporting, and execution-brief
surface. Exact changed files:

- `docs/ai/codex/VALIDATION_POLICY.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/runbook.md`
- `docs/status_entries/WP-GUIDE-ACCELERATION-OPERATING-MODE-01.md`
- `docs/ai/codex/README.md`
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `prompts/execution_brief.md`
- `.claude/skills/write-execution-brief.md`
- `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md`
- `prompts/report_back.md`
- `.claude/skills/review-report-back.md`

The locked T0-T4 vocabulary selects validation by blast radius: T0
docs/status/comments; T1 test-only, read-only query additions, exact-artifact
persistence, and non-canonical research automation; T2 schema, validator,
contract, query-SQL, and broad production code; T3 canonical crossings and
protected writers; T4 runtime, OMS, reconciliation, risk, capital, and
paper/live paths.

One T0-T4 vocabulary now applies across current shared guidance, compatibility
wrappers, and Claude drafting/review skills. Historical status entries and
architecture/design records retain their contemporaneous labels and were
intentionally not rewritten; they are not authoritative for the current tier
meanings.

## Validation summary

- `git diff --check`: passed.
- `git diff --cached --check`: passed.
- Exact twelve-file allowlist and forbidden-scope checks: passed.
- Internal path references for the active guidance surfaces: passed.
- Markdown fenced-block balance for the active guidance surfaces: passed; no
  repo-owned Markdown lint/render command was discovered.
- Active-guidance tier-nomenclature contradiction scan, including `AGENTS.md`
  and `CLAUDE_START_HERE.md`: passed; no stale live-tier semantics remain.
- Protected-core semantic text audit: passed.
- Final rebase onto current `origin/main`: passed.
- GitHub mergeability: `MERGEABLE` / clean.
- Full pytest: NOT RUN — T0 docs/process policy; not used as merge evidence.
- Registry/query integrity: not run; not used as merge evidence because this
  package changes no generated validation data, artifact index, registry,
  query, schema, or validator behavior.

## Boundary summary

Protected T3/T4 boundaries are unchanged. Exact-content canonical crossings,
irreversible-execution authorization, full-denominator accounting, append-only
integrity, protected writers, human promotion gates, runtime, paper/live, OMS,
reconciliation, hard risk, capital, and required exact-head review retain their
full rigor.

This guidance creates no implementation, runtime, execution, evidence,
canonical-persistence, promotion, approval, scoring, ranking, recommendation,
risk, or capital authority. It does not authorize committing any current H-004
local stream/audit evidence or adding an external dependency or tool.

## Merge status and runway

Ready for Side review; not merged by this package. `docs/project_status.md` is
unchanged. Subsequent packages may use the locked operating model within their
own explicit scope and authority boundary; protected and shared-semantic work
continues to serialize.
