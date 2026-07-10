/**
 * The committed free-parameter declaration for a strategy spec.
 *
 * This is the parameter *space* the spec declares — defaults, ranges, and
 * allowed values. It is not a per-variant assignment: no committed artifact
 * projected to this surface records which value a given variant ran with.
 */
import { Badge } from "@/components/ui";
import { Cell, DataTable, FieldNote, Row } from "@/components/explorer/primitives";
import { derivedFreeParameterCount, orDash } from "@/lib/explorer";
import type { SpecFreeParameter, SpecFreeParameters } from "@/lib/types";

const COLUMNS = [
  "name",
  "type",
  "units",
  "default",
  "range",
  "allowed_values",
  "role",
  "in_variant_generation",
];

function rangeLabel(range: SpecFreeParameter["range"]): string {
  if (!range) return "—";
  const min = range.min ?? null;
  const max = range.max ?? null;
  if (min === null && max === null) return "—";
  const open = range.inclusive_min === false ? "(" : "[";
  const close = range.inclusive_max === false ? ")" : "]";
  const step = range.step !== null && range.step !== undefined ? ` step ${range.step}` : "";
  return `${open}${orDash(min)}, ${orDash(max)}${close}${step}`;
}

export function FreeParameterTable({
  freeParameters,
  apiProjectedCount,
}: {
  freeParameters: SpecFreeParameters | undefined;
  /** `free_parameter_count` as the API projects it — `null` on every spec. */
  apiProjectedCount: number | null | undefined;
}) {
  const parameters = freeParameters?.parameters ?? [];
  const derived = derivedFreeParameterCount(freeParameters);
  const max = freeParameters?.max_free_parameters;

  if (freeParameters?.no_free_parameters_declared === true) {
    return (
      <p className="text-sm text-cockpit-muted">
        This spec declares{" "}
        <span className="font-mono text-cockpit-text">
          no_free_parameters_declared = true
        </span>
        . No free parameters exist to show.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="info">
          {derived} declared free parameter{derived === 1 ? "" : "s"}
        </Badge>
        {typeof max === "number" ? (
          <Badge tone="neutral">cap: {max}</Badge>
        ) : null}
        <span className="text-xs text-cockpit-muted">
          count derived by tallying{" "}
          <span className="font-mono text-cockpit-text">
            free_parameters.parameters[]
          </span>
        </span>
      </div>

      {parameters.length === 0 ? (
        <p className="text-xs text-cockpit-muted">
          The spec projects no parameter entries.
        </p>
      ) : (
        <DataTable columns={COLUMNS}>
          {parameters.map((parameter, index) => (
            <Row key={parameter.name ?? index}>
              <Cell mono>{orDash(parameter.name)}</Cell>
              <Cell mono muted>
                {orDash(parameter.type)}
              </Cell>
              <Cell mono muted>
                {orDash(parameter.units)}
              </Cell>
              <Cell mono>{orDash(parameter.default)}</Cell>
              <Cell mono muted>
                {rangeLabel(parameter.range)}
              </Cell>
              <Cell mono muted>
                {parameter.allowed_values?.length
                  ? parameter.allowed_values.join(", ")
                  : "—"}
              </Cell>
              <Cell muted>{orDash(parameter.role)}</Cell>
              <Cell mono muted>
                {orDash(parameter.included_in_variant_generation)}
              </Cell>
            </Row>
          ))}
        </DataTable>
      )}

      {parameters.some((p) => p.rationale || p.constraints?.length) ? (
        <ul className="flex flex-col gap-1.5 text-xs">
          {parameters.map((parameter, index) =>
            parameter.rationale || parameter.constraints?.length ? (
              <li key={parameter.name ?? index} className="text-cockpit-muted">
                <span className="font-mono text-cockpit-text">
                  {orDash(parameter.name)}
                </span>
                {parameter.rationale ? ` — ${parameter.rationale}` : ""}
                {parameter.constraints?.length
                  ? ` Constraints: ${parameter.constraints.join(" ")}`
                  : ""}
              </li>
            ) : null,
          )}
        </ul>
      ) : null}

      {freeParameters?.counting_rule ? (
        <p className="text-xs text-cockpit-muted">
          <span className="uppercase tracking-wider">counting rule</span>{" "}
          {freeParameters.counting_rule}
        </p>
      ) : null}

      <FieldNote
        source="GET /api/strategies/{id}"
        fields={[
          "free_parameters.parameters[]",
          "free_parameters.max_free_parameters",
          "free_parameters.counting_rule",
        ]}
        note={
          apiProjectedCount === null || apiProjectedCount === undefined
            ? "The API's free_parameter_count field reads free_parameters.count, which committed specs do not carry, so it projects null. The count above is derived for display from the committed parameter entries and is not an API-projected value."
            : undefined
        }
      />
    </div>
  );
}
