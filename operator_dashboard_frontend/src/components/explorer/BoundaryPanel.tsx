/**
 * The strategy's own non-authority declaration, plus this surface's posture.
 *
 * The flags below are read from the committed artifacts — they are not prose
 * this dashboard wrote. A strategy spec is a planning artifact: it is not
 * executable, not a candidate, not approved beyond variant planning, and it
 * confers no readiness, promotion, ranking, or runtime authority. Nothing on
 * this page can change that, because nothing on this page writes anything.
 */
import { Badge } from "@/components/ui";
import { FieldNote, FlagGrid, NoteList } from "@/components/explorer/primitives";
import { orDash } from "@/lib/explorer";
import type { SpecReview } from "@/lib/types";

/** What this surface is not. Fixed, and true of every route in this dashboard. */
const SURFACE_POSTURE: readonly string[] = [
  "Read-only presentation. No control, form, or submit surface exists.",
  "Not executable. Strategy specs are planning artifacts.",
  "Not candidate approval, promotion, readiness, or crossing.",
  "Not paper or live trading, and no runtime, broker, or exchange contact.",
  "Not a ranking or a recommendation. No variant, spec, or population is preferred.",
  "No Agent Inbox write. No scheduler or notification firing.",
];

export function BoundaryPanel({
  nonExecutionDeclaration,
  review,
  populationDeclarations,
}: {
  nonExecutionDeclaration: Record<string, boolean> | undefined;
  review: SpecReview | undefined;
  /** `non_authority_declaration` from each linked result population. */
  populationDeclarations: Array<{
    id: string;
    declaration: Record<string, unknown>;
  }>;
}) {
  const acknowledgement = review?.non_authority_acknowledgement ?? {};

  // Only project committed booleans; anything else is left out rather than cast.
  const populationFlags: Record<string, boolean> = {};
  for (const { declaration } of populationDeclarations) {
    for (const [key, value] of Object.entries(declaration)) {
      if (typeof value === "boolean" && value) populationFlags[key] = value;
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          This surface
        </span>
        <ul className="flex flex-col gap-1 text-xs">
          {SURFACE_POSTURE.map((line) => (
            <li
              key={line}
              className="rounded border border-cockpit-border/60 bg-cockpit-panel-2 px-2 py-1.5 text-cockpit-text"
            >
              {line}
            </li>
          ))}
        </ul>
      </div>

      <div className="flex flex-col gap-1.5">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Spec: non_execution_declaration
        </span>
        <FlagGrid flags={nonExecutionDeclaration ?? {}} />
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
            Spec: review
          </span>
          {review?.approval_scope ? (
            <Badge tone="warn">scope: {review.approval_scope}</Badge>
          ) : null}
          {review?.human_review_required ? (
            <Badge tone="info">human review required</Badge>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-cockpit-muted">
          <span>
            reviewer:{" "}
            <span className="font-mono text-cockpit-text">
              {orDash(review?.reviewer)}
            </span>
          </span>
          <span>
            reviewed_at:{" "}
            <span className="font-mono text-cockpit-text">
              {orDash(review?.reviewed_at)}
            </span>
          </span>
        </div>
        <NoteList
          items={review?.review_notes}
          emptyLabel="The spec records no review notes."
        />
        <div className="mt-1">
          <FlagGrid flags={acknowledgement} />
        </div>
      </div>

      {Object.keys(populationFlags).length > 0 ? (
        <div className="flex flex-col gap-1.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
            Linked result populations: non_authority_declaration
          </span>
          <FlagGrid flags={populationFlags} />
          <p className="text-xs text-cockpit-muted">
            Asserted across{" "}
            <span className="font-mono text-cockpit-text">
              {populationDeclarations.map((p) => p.id).join(", ")}
            </span>
            .
          </p>
        </div>
      ) : null}

      <FieldNote
        source="GET /api/strategies/{id} · GET /api/research/result-populations/{id}"
        fields={[
          "non_execution_declaration",
          "review.approval_scope",
          "review.human_review_required",
          "review.reviewer",
          "review.reviewed_at",
          "review.review_notes[]",
          "review.non_authority_acknowledgement",
          "non_authority_declaration",
        ]}
        note="approval_scope is read from review.approval_scope. The API's top-level approval_scope field reads review.review_scope, which committed specs do not carry, so it projects null."
      />
    </div>
  );
}
