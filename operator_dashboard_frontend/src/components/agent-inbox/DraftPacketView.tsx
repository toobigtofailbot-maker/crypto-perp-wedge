/**
 * Read-only preview of a returned scratch draft packet.
 *
 * Every value here is the packet's own words, echoed. Nothing is summarized
 * into a verdict, scored, ranked, or presented as executable. The formalizer
 * proposes draft language and parameter bounds; those are neither a Strategy
 * Spec nor a sweep grid, and the packet says so itself via
 * `draft_strategy_spec.produced === false`.
 *
 * There is deliberately no control on this panel: no run, approve, promote,
 * execute, create-candidate, or send-to-pipeline affordance exists.
 */
import { Badge, Card, CardTitle, KeyValue } from "@/components/ui";
import {
  Cell,
  DataTable,
  FlagGrid,
  NoteList,
  Row,
} from "@/components/explorer/primitives";
import type { AgentInboxDraftPacket } from "@/lib/agentInboxClient";

function orDash(value: string | number | null | undefined): string {
  return value === null || value === undefined || value === ""
    ? "—"
    : String(value);
}

/** A labelled block of the formalizer's prose. Text, never a directive. */
function ProseField({
  label,
  value,
}: {
  label: string;
  value: string | undefined;
}) {
  if (!value) return null;
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
        {label}
      </span>
      <p className="text-sm text-cockpit-text">{value}</p>
    </div>
  );
}

export function DraftPacketView({ packet }: { packet: AgentInboxDraftPacket }) {
  const formalizer = packet.formalizer_result ?? {};
  const research = formalizer.research_object ?? null;
  const draftSpec = formalizer.draft_strategy_spec ?? null;
  const capability = packet.availability_primitive_check ?? null;
  const provenance = packet.provenance ?? {};
  const parameterBounds = research?.parameter_bounds ?? [];

  return (
    <div className="flex flex-col gap-4">
      <Card className="border-cockpit-warn/40">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <CardTitle>Draft packet</CardTitle>
          <div className="flex flex-wrap gap-2">
            <Badge tone="warn">scratch only</Badge>
            <Badge tone="warn">not executable</Badge>
            <Badge tone="info">human review required</Badge>
          </div>
        </div>
        <div className="flex flex-col">
          <KeyValue label="draft_id" value={packet.draft_id} />
          <KeyValue label="created_at" value={packet.created_at} />
          <KeyValue label="schema_version" value={packet.schema_version} />
          <KeyValue
            label="formalizer status"
            value={orDash(formalizer.status)}
          />
          <KeyValue
            label="draft_strategy_spec.produced"
            value={String(draftSpec?.produced ?? false)}
          />
          <KeyValue
            label="written to"
            value={orDash(provenance.output_path)}
          />
        </div>
        <p className="mt-3 border-t border-cockpit-border/50 pt-2 text-xs text-cockpit-muted">
          No Strategy Spec was produced. This packet confers no candidate,
          approval, promotion, runner, pipeline, or paper/live authority, and
          nothing downstream reads it automatically.
        </p>
      </Card>

      <Card>
        <CardTitle>Warnings</CardTitle>
        <NoteList
          items={packet.warnings}
          emptyLabel="The packet declares no warnings."
          tone="warn"
        />
      </Card>

      <Card>
        <CardTitle>Open questions</CardTitle>
        <NoteList
          items={packet.open_questions}
          emptyLabel="The packet declares no open questions."
        />
      </Card>

      <Card>
        <CardTitle>Blockers</CardTitle>
        <NoteList
          items={packet.blockers}
          emptyLabel="The packet declares no blockers."
          tone="warn"
        />
        {(formalizer.rejection_reasons ?? []).length > 0 ? (
          <div className="mt-3 flex flex-col gap-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
              Formalizer rejection reasons
            </span>
            <NoteList
              items={formalizer.rejection_reasons}
              emptyLabel="None."
              tone="warn"
            />
          </div>
        ) : null}
      </Card>

      {research ? (
        <Card>
          <CardTitle>Formalizer draft content</CardTitle>
          <p className="mb-3 text-xs text-cockpit-muted">
            Proposed draft language, not a Strategy Spec and not a Variant
            Manifest. Nothing below is compiled, validated, or runnable.
          </p>
          <div className="flex flex-col gap-3">
            <ProseField label="summary" value={research.summary} />
            <ProseField
              label="causal_rationale"
              value={research.causal_rationale}
            />
            <ProseField
              label="falsifiable_prediction"
              value={research.falsifiable_prediction}
            />
            <ProseField label="entry_concept" value={research.entry_concept} />
            <ProseField label="exit_concept" value={research.exit_concept} />

            <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-cockpit-muted">
              <span>
                symbols:{" "}
                <span className="font-mono text-cockpit-text">
                  {orDash((research.symbols ?? []).join(", "))}
                </span>
              </span>
              <span>
                timeframe:{" "}
                <span className="font-mono text-cockpit-text">
                  {orDash(research.timeframe)}
                </span>
              </span>
              <span>
                features:{" "}
                <span className="font-mono text-cockpit-text">
                  {orDash((research.features ?? []).join(", "))}
                </span>
              </span>
            </div>

            {parameterBounds.length > 0 ? (
              <div className="flex flex-col gap-1.5">
                <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
                  Proposed parameter bounds
                </span>
                <DataTable
                  columns={["name", "minimum", "maximum"]}
                  caption="Draft bounds proposed by the formalizer. Not a Variant Manifest, not a Sweep Plan, and not a sweep grid."
                >
                  {parameterBounds.map((bound) => (
                    <Row key={bound.name}>
                      <Cell mono>{bound.name}</Cell>
                      <Cell mono>{bound.minimum}</Cell>
                      <Cell mono>{bound.maximum}</Cell>
                    </Row>
                  ))}
                </DataTable>
              </div>
            ) : null}

            {(research.stop_conditions ?? []).length > 0 ? (
              <div className="flex flex-col gap-1.5">
                <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
                  stop_conditions
                </span>
                <NoteList
                  items={research.stop_conditions}
                  emptyLabel="None declared."
                />
              </div>
            ) : null}
          </div>
        </Card>
      ) : null}

      {capability ? (
        <Card>
          <CardTitle>Availability primitive check</CardTitle>
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={capability.historically_testable_now ? "good" : "warn"}>
                historically_testable_now:{" "}
                {String(capability.historically_testable_now)}
              </Badge>
              {capability.blocking_features.length > 0 ? (
                <Badge tone="bad">
                  blocking: {capability.blocking_features.join(", ")}
                </Badge>
              ) : null}
            </div>
            <p className="text-xs text-cockpit-muted">
              {capability.distinction}
            </p>
            {capability.feature_assessments.length > 0 ? (
              <DataTable
                columns={[
                  "feature",
                  "compiler_field_exists",
                  "coverage_class",
                  "historical_testability",
                  "source_class",
                ]}
              >
                {capability.feature_assessments.map((assessment) => (
                  <Row key={assessment.feature}>
                    <Cell mono>{assessment.feature}</Cell>
                    <Cell mono>{String(assessment.compiler_field_exists)}</Cell>
                    <Cell mono muted>
                      {assessment.coverage_class}
                    </Cell>
                    <Cell mono muted>
                      {assessment.historical_testability}
                    </Cell>
                    <Cell mono muted>
                      {assessment.source_class}
                    </Cell>
                  </Row>
                ))}
              </DataTable>
            ) : null}
          </div>
        </Card>
      ) : null}

      <Card>
        <CardTitle>Non-authority flags</CardTitle>
        <FlagGrid flags={packet.non_authority_flags ?? {}} />
      </Card>

      <Card>
        <CardTitle>Provenance</CardTitle>
        <div className="flex flex-col">
          <KeyValue
            label="service_namespace"
            value={orDash(provenance.service_namespace)}
          />
          <KeyValue label="package_id" value={orDash(provenance.package_id)} />
          <KeyValue
            label="formalizer_module"
            value={orDash(provenance.formalizer_module)}
          />
          <KeyValue
            label="formalizer_mode"
            value={orDash(provenance.formalizer_mode)}
          />
          <KeyValue
            label="provider_mode"
            value={orDash(provenance.provider_mode)}
          />
          <KeyValue label="provider_id" value={orDash(provenance.provider_id)} />
          <KeyValue
            label="api_call_made"
            value={String(formalizer.provider_metadata?.api_call_made ?? false)}
          />
          <KeyValue
            label="tool_context_role"
            value={orDash(provenance.tool_context_role)}
          />
          <KeyValue label="fabricated" value={String(packet.fabricated)} />
          <KeyValue
            label="source_request_sha256"
            value={orDash(packet.source_hashes?.source_request_sha256)}
          />
        </div>
        {(provenance.captured_formalizer_write_paths ?? []).length > 0 ? (
          <div className="mt-3 flex flex-col gap-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
              Formalizer writes captured in memory
            </span>
            <p className="text-xs text-cockpit-muted">
              These paths were intercepted rather than written, so the service
              persisted the draft packet alone.
            </p>
            <NoteList
              items={provenance.captured_formalizer_write_paths}
              emptyLabel="None."
            />
          </div>
        ) : null}
      </Card>

      {packet.tool_context_audit.length > 0 ? (
        <Card>
          <CardTitle>Tool context audit</CardTitle>
          <DataTable
            columns={["action_type", "decision", "target_path"]}
            caption="Audit records only; they confer no canonical, candidate-lifecycle, promotion, paper/live, runtime, or execution authority."
          >
            {packet.tool_context_audit.map((record, index) => (
              <Row key={`${record.target_path}-${index}`}>
                <Cell mono>{record.action_type}</Cell>
                <Cell mono>
                  <Badge tone={record.decision === "allowed" ? "neutral" : "bad"}>
                    {record.decision}
                  </Badge>
                </Cell>
                <Cell mono muted>
                  {record.target_path}
                </Cell>
              </Row>
            ))}
          </DataTable>
        </Card>
      ) : null}
    </div>
  );
}
