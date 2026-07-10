/**
 * Renders a committed strategy spec's entry, exit, and filter logic.
 *
 * Conditions are transcribed from the artifact's own operand tree. The panel
 * does not evaluate, simulate, or reorder them, and it does not claim the logic
 * is executable — it is not. Strategy specs are planning artifacts.
 */
import { Badge } from "@/components/ui";
import { conditionCount, flattenGroups, formatCondition } from "@/lib/explorer";
import type { SpecLogicGroup } from "@/lib/types";

function GroupBlock({
  group,
  depth,
}: {
  group: SpecLogicGroup;
  depth: number;
}) {
  const conditions = group.conditions ?? [];
  return (
    <div
      className="rounded border border-cockpit-border/60 bg-cockpit-panel-2 p-3"
      style={depth > 0 ? { marginLeft: `${depth}rem` } : undefined}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs text-cockpit-heading">
          {group.group_id ?? "—"}
        </span>
        {group.group_role ? <Badge>{group.group_role}</Badge> : null}
        {group.logic ? <Badge tone="info">{group.logic}</Badge> : null}
        {group.side ? <Badge tone="neutral">side: {group.side}</Badge> : null}
      </div>

      {conditions.length > 0 ? (
        <ul className="mt-2 flex flex-col gap-2">
          {conditions.map((condition, index) => (
            <li
              key={condition.condition_id ?? index}
              className="flex flex-col gap-0.5 border-l-2 border-cockpit-border pl-2.5"
            >
              <code className="text-xs text-cockpit-text">
                {formatCondition(condition)}
              </code>
              <span className="font-mono text-[0.7rem] text-cockpit-muted">
                {condition.condition_id ?? "—"}
                {condition.condition_role ? ` · ${condition.condition_role}` : ""}
                {condition.units ? ` · units: ${condition.units}` : ""}
              </span>
              {condition.notes ? (
                <span className="text-xs text-cockpit-muted">
                  {condition.notes}
                </span>
              ) : null}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-xs text-cockpit-muted">
          This group declares no conditions.
        </p>
      )}

      {group.notes ? (
        <p className="mt-2 text-xs text-cockpit-muted">{group.notes}</p>
      ) : null}
    </div>
  );
}

export function SpecLogicPanel({
  label,
  groups,
  notes,
  emptyLabel,
}: {
  label: string;
  groups: SpecLogicGroup[] | undefined;
  notes?: string | null;
  /** Shown when the spec declares no groups at all. */
  emptyLabel: string;
}) {
  const flattened = flattenGroups(groups);
  const total = conditionCount(groups);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-cockpit-heading">{label}</span>
        <Badge tone="neutral">
          {flattened.length} group{flattened.length === 1 ? "" : "s"}
        </Badge>
        <Badge tone="neutral">
          {total} condition{total === 1 ? "" : "s"}
        </Badge>
      </div>

      {flattened.length === 0 ? (
        <p className="text-xs text-cockpit-muted">{emptyLabel}</p>
      ) : (
        <div className="flex flex-col gap-2">
          {flattened.map(({ group, depth }, index) => (
            <GroupBlock
              key={group.group_id ?? index}
              group={group}
              depth={depth}
            />
          ))}
        </div>
      )}

      {notes ? <p className="text-xs text-cockpit-muted">{notes}</p> : null}
    </div>
  );
}
