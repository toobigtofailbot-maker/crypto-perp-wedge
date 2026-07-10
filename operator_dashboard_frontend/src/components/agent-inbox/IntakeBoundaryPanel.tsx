/**
 * The standing boundary declaration for the Agent Inbox route.
 *
 * This is the one place in the dashboard where a form and a submit button
 * exist. That form writes a scratch draft packet and nothing else, so the
 * boundary has to be stated where the operator reads it — above the form,
 * before submitting, not buried in a footer.
 */
import { Card, CardTitle } from "@/components/ui";

/** What submitting this form does, and the far longer list of what it does not do. */
const BOUNDARY_LINES: readonly string[] = [
  "Draft only.",
  "Scratch only.",
  "Does not create Strategy Spec / Variant Manifest / Sweep Plan.",
  "Does not run backtests.",
  "Does not create candidates.",
  "Does not approve, promote, cross, or trade.",
  "Does not touch paper/live/runtime.",
  "Requires human review before any repo action.",
];

export function IntakeBoundaryPanel() {
  return (
    <Card className="border-cockpit-warn/40">
      <CardTitle>Boundary</CardTitle>
      <p className="mb-3 text-sm text-cockpit-muted">
        Submitting an idea writes one noncanonical draft packet to the repo
        scratch tree and returns it for review. That is the entire effect.
      </p>
      <ul className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
        {BOUNDARY_LINES.map((line) => (
          <li
            key={line}
            className="rounded border border-cockpit-warn/30 bg-cockpit-warn/5 px-2 py-1.5 text-xs text-cockpit-text"
          >
            {line}
          </li>
        ))}
      </ul>
      <p className="mt-3 border-t border-cockpit-border/50 pt-2 text-xs text-cockpit-muted">
        The draft packet is review material only. It is not evidence, authority,
        approval, recommendation, ranking, readiness, promotion, or execution
        input.
      </p>
    </Card>
  );
}
