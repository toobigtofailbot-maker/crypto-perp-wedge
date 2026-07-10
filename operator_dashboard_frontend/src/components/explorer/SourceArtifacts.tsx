/**
 * Where this strategy spec came from: the committed artifact, its digest, the
 * documents it cites, and the constraints and unresolved claims its authors
 * recorded.
 *
 * Paths are printed as text. Nothing here opens a file, resolves a link, or
 * touches the filesystem — the operator reads a path and goes and looks.
 */
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import { FieldNote, NoteList } from "@/components/explorer/primitives";
import { orDash, shortHash } from "@/lib/explorer";
import type { ProvenanceRef, SpecProvenance } from "@/lib/types";

export function SourceArtifacts({
  specPath,
  envelopeProvenance,
  provenance,
}: {
  specPath: string | null | undefined;
  /** Envelope-level artifact refs, carrying role and sha256. */
  envelopeProvenance: ProvenanceRef[];
  /** The spec's own committed provenance block. */
  provenance: SpecProvenance | undefined;
}) {
  const unresolved = provenance?.unresolved_claims ?? [];

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col">
        <KeyValue label="Spec artifact" value={orDash(specPath)} />
        <KeyValue label="Source type" value={orDash(provenance?.source_type)} />
        <KeyValue label="Prepared by" value={orDash(provenance?.prepared_by)} />
        <KeyValue label="Created at" value={orDash(provenance?.created_at)} />
        <KeyValue label="Updated at" value={orDash(provenance?.updated_at)} />
      </div>

      {provenance?.rationale ? (
        <p className="text-sm text-cockpit-text">{provenance.rationale}</p>
      ) : null}

      <Card className="bg-cockpit-panel-2">
        <CardTitle>Envelope artifacts</CardTitle>
        {envelopeProvenance.length === 0 ? (
          <p className="text-xs text-cockpit-muted">
            The envelope carries no artifact references.
          </p>
        ) : (
          <ul className="flex flex-col gap-1.5 text-xs">
            {envelopeProvenance.map((ref, index) => (
              <li key={`${ref.path}-${index}`} className="flex flex-col">
                <span className="font-mono text-cockpit-text">{ref.path}</span>
                <span className="text-cockpit-muted">
                  {ref.role}
                  {ref.sha256 ? (
                    <>
                      {" · "}
                      <span className="font-mono">{shortHash(ref.sha256)}</span>
                    </>
                  ) : null}
                  {ref.note ? ` · ${ref.note}` : ""}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <div className="flex flex-col gap-1.5">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Source references
        </span>
        <NoteList
          items={provenance?.source_refs}
          emptyLabel="The spec cites no source documents."
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
          Source constraints
        </span>
        <NoteList
          items={provenance?.source_constraints}
          emptyLabel="The spec declares no source constraints."
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
            Unresolved claims
          </span>
          {unresolved.length > 0 ? (
            <Badge tone="warn">{unresolved.length} open</Badge>
          ) : null}
        </div>
        <NoteList
          items={unresolved}
          emptyLabel="The spec records no unresolved claims."
          tone="warn"
        />
      </div>

      <FieldNote
        source="GET /api/strategies/{id}"
        fields={[
          "path",
          "provenance.source_type",
          "provenance.source_refs[]",
          "provenance.prepared_by",
          "provenance.rationale",
          "provenance.source_constraints[]",
          "provenance.unresolved_claims[]",
          "envelope.provenance[]",
        ]}
        note="Paths and digests are shown as text. This surface performs no filesystem navigation."
      />
    </div>
  );
}
