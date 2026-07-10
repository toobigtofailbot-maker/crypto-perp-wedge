/**
 * Static presentational primitives shared by the Strategy Explorer.
 *
 * Every element here is text, a table, or an in-page anchor. None of them
 * accepts a handler, submits anything, or implies an action.
 */
import type { ReactNode } from "react";
import { Badge, Card, CardTitle } from "@/components/ui";
import type { Tone } from "@/lib/status";

/**
 * A titled Explorer section with a stable anchor id, so `SectionNav` can link
 * to it. `<section id>` + `<a href="#id">` is navigation, not state.
 */
export function ExplorerSection({
  id,
  title,
  subtitle,
  aside,
  children,
}: {
  id: string;
  title: string;
  subtitle?: string;
  aside?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section
      id={id}
      className="scroll-mt-4 rounded-lg border border-cockpit-border bg-cockpit-panel p-4"
    >
      <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
            {title}
          </h2>
          {subtitle ? (
            <p className="text-sm text-cockpit-muted">{subtitle}</p>
          ) : null}
        </div>
        {aside ? <div className="flex flex-wrap gap-2">{aside}</div> : null}
      </div>
      {children}
    </section>
  );
}

/** In-page anchor list. Link-only navigation; nothing here holds state. */
export function SectionNav({
  sections,
}: {
  sections: Array<{ id: string; label: string }>;
}) {
  return (
    <nav
      aria-label="Strategy sections"
      className="flex flex-wrap gap-x-3 gap-y-1.5 rounded-lg border border-cockpit-border bg-cockpit-panel-2 px-3 py-2.5 text-xs"
    >
      {sections.map((section) => (
        <a
          key={section.id}
          href={`#${section.id}`}
          className="text-cockpit-accent hover:underline"
        >
          {section.label}
        </a>
      ))}
    </nav>
  );
}

/**
 * A static table. Horizontally scrollable so a wide metric grid never forces the
 * page body to scroll sideways.
 */
export function DataTable({
  columns,
  children,
  caption,
}: {
  columns: string[];
  children: ReactNode;
  caption?: string;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-max border-collapse text-left text-xs">
        {caption ? (
          <caption className="pb-2 text-left text-xs text-cockpit-muted">
            {caption}
          </caption>
        ) : null}
        <thead>
          <tr className="border-b border-cockpit-border">
            {columns.map((column) => (
              <th
                key={column}
                scope="col"
                className="whitespace-nowrap px-2 py-1.5 font-mono font-medium text-cockpit-muted"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

export function Row({ children }: { children: ReactNode }) {
  return (
    <tr className="border-b border-cockpit-border/40 last:border-b-0">
      {children}
    </tr>
  );
}

export function Cell({
  children,
  mono = false,
  muted = false,
}: {
  children: ReactNode;
  mono?: boolean;
  muted?: boolean;
}) {
  return (
    <td
      className={`whitespace-nowrap px-2 py-1.5 ${mono ? "font-mono" : ""} ${
        muted ? "text-cockpit-muted" : "text-cockpit-text"
      }`}
    >
      {children}
    </td>
  );
}

/**
 * Render a committed record of boolean declaration flags.
 *
 * `true` is shown as asserted, `false` as not asserted. Nothing is inverted or
 * summarised into a verdict — these are the artifact's own words.
 */
export function FlagGrid({ flags }: { flags: Record<string, boolean> }) {
  const entries = Object.entries(flags);
  if (entries.length === 0) {
    return (
      <p className="text-xs text-cockpit-muted">
        No declaration flags are projected for this artifact.
      </p>
    );
  }
  return (
    <ul className="grid grid-cols-1 gap-1.5 sm:grid-cols-2 lg:grid-cols-3">
      {entries.map(([key, value]) => (
        <li
          key={key}
          className="flex items-center justify-between gap-2 rounded border border-cockpit-border/60 bg-cockpit-panel-2 px-2 py-1.5 text-xs"
        >
          <span className="font-mono text-cockpit-muted">{key}</span>
          <Badge tone={value ? "good" : "neutral"}>{String(value)}</Badge>
        </li>
      ))}
    </ul>
  );
}

/** A bulleted list of committed strings, or an explicit "none declared" note. */
export function NoteList({
  items,
  emptyLabel,
  tone = "muted",
}: {
  items: readonly string[] | null | undefined;
  emptyLabel: string;
  tone?: "muted" | "warn";
}) {
  const list = items ?? [];
  if (list.length === 0) {
    return <p className="text-xs text-cockpit-muted">{emptyLabel}</p>;
  }
  return (
    <ul className="flex list-disc flex-col gap-1 pl-4 text-xs">
      {list.map((item, index) => (
        <li
          key={index}
          className={tone === "warn" ? "text-cockpit-warn" : "text-cockpit-text"}
        >
          {item}
        </li>
      ))}
    </ul>
  );
}

/** A short caption stating which committed fields a panel read. */
export function FieldNote({
  source,
  fields,
  note,
}: {
  source: string;
  fields: string[];
  note?: string;
}) {
  return (
    <div className="mt-3 flex flex-col gap-1 border-t border-cockpit-border/50 pt-2 text-xs text-cockpit-muted">
      <p>
        <span className="uppercase tracking-wider">source</span>{" "}
        <span className="font-mono text-cockpit-text">{source}</span>
      </p>
      <p>
        <span className="uppercase tracking-wider">fields</span>{" "}
        <span className="font-mono text-cockpit-text">{fields.join(", ")}</span>
      </p>
      {note ? <p>{note}</p> : null}
    </div>
  );
}

/**
 * A non-chart absence. Mirrors `UnavailableChartState` for panels that are not
 * charts, so a missing table reads as honestly as a missing series.
 */
export function UnavailablePanel({
  title,
  absence,
  reason,
  source,
}: {
  title: string;
  absence: "withheld" | "unavailable" | "deferred";
  reason: string;
  source?: string;
}) {
  const tone: Record<string, Tone> = {
    withheld: "neutral",
    unavailable: "warn",
    deferred: "info",
  };
  return (
    <Card className="border-dashed">
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <CardTitle>{title}</CardTitle>
        <div className="mb-3">
          <Badge tone={tone[absence]}>{absence}</Badge>
        </div>
      </div>
      <p className="text-sm text-cockpit-text">{reason}</p>
      <p className="mt-2 text-xs text-cockpit-muted">
        Nothing is inferred, zero-filled, or simulated.
        {source ? (
          <>
            {" "}
            Declared by{" "}
            <span className="font-mono text-cockpit-text">{source}</span>.
          </>
        ) : null}
      </p>
    </Card>
  );
}
