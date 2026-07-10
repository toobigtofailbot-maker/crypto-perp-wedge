# WP-INBOX-DRAFT-REVIEW-STATE-03B — no-canonical-control evidence

## Every control added by this package

| Control | Location | What it does | Why it cannot canonicalize / queue / run / approve / promote / execute |
| --- | --- | --- | --- |
| "Refresh (read-only)" button | `ReviewTrail.tsx` | Re-GETs the review trail for the open draft via the same-origin passthrough. | GET only; reads existing scratch annotations. Submits and mutates nothing. |
| Review-state `<select>` | `ReviewTrail.tsx` (append form) | Chooses one of four review states for the annotation being drafted. | Local form state only. Choosing `flagged_for_canonicalization` sets a string field; it triggers no request until submit, and the submit only appends a scratch annotation. |
| "Reviewer label" input | append form | Local text state. | No network effect on its own. |
| "Rationale" textarea | append form | Local text state. | No network effect on its own. |
| "Clarification request" textarea (optional) | append form | Local text state. | No network effect on its own. |
| "Append scratch review event" submit button | append form | POSTs one bounded annotation to the isolated service via the same-origin passthrough. | The upstream is exactly `POST /api/agent/drafts/{draft_id}/review-events` on the isolated intake service. That service appends one JSONL row under `scratch/…/reviews/` and stamps `annotation_only`, `not_canonicalization_approval`, `not_queue_admission`, `not_research_execution`, `not_candidate_creation`, `not_runtime_action`. There is no other upstream and no other verb. |
| "Non-authority flags" `<details>` disclosure | event row | Expands/collapses the event's own non-authority flags. | Presentational; no state or network effect. |

No control is labelled or behaves like: approve, promote, execute, run, queue,
canonicalize, create Strategy Spec, send to research, or candidate.

## Route surface

`src/app/agent-inbox/drafts/[draft_id]/review-events/route.ts` exports only `GET`
and `POST`. No `PUT`/`PATCH`/`DELETE` exist, so Next.js returns 405 for them
(verified at runtime). Each verb forwards to exactly one hardcoded upstream path;
neither is a generic proxy, and neither contacts `tools.operator_dashboard_api`.

## What was NOT built

No Strategy Spec, Variant Manifest, Sweep Plan, queue entry, Result Population,
candidate or candidate-lifecycle record, runner/bridge/gate/pipeline/scheduler/
notification/paper/live/runtime/provider/broker/exchange/OMS/risk/reconciliation/
safe-mode/credential call, and no scratch-to-canonical bridge or canonicalization
validation. No client-side persistence (no localStorage/sessionStorage/cookie/
IndexedDB). No dependency was added. `tools/**` was not modified.

## Runtime confirmation (see validation_summary.txt)

- Network during a full review-flow session was limited to: `GET /agent-inbox/drafts`,
  `GET /agent-inbox/drafts/{id}`, `GET …/review-events`, `POST …/review-events`.
- `localStorage`, `sessionStorage`, and `document.cookie` were all empty after
  appending events.
- Invalid draft id (`bad-id`) returned 400 from the passthrough with no upstream
  call; `PUT` and `DELETE` returned 405.
