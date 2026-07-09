/** Presentational primitives for the operator cockpit shell. Read-only. */
import type { ReactNode } from "react";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-lg border border-cockpit-border bg-cockpit-panel p-4 ${className}`}
    >
      {children}
    </section>
  );
}

export function CardTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-cockpit-muted">
      {children}
    </h2>
  );
}

export function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
}) {
  return (
    <Card className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wider text-cockpit-muted">
        {label}
      </span>
      <span className="font-mono text-2xl text-cockpit-heading">{value}</span>
      {hint ? <span className="text-xs text-cockpit-muted">{hint}</span> : null}
    </Card>
  );
}

type Tone = "neutral" | "good" | "warn" | "bad" | "info";

const TONE_CLASS: Record<Tone, string> = {
  neutral: "border-cockpit-border bg-cockpit-panel-2 text-cockpit-muted",
  good: "border-cockpit-good/40 bg-cockpit-good/10 text-cockpit-good",
  warn: "border-cockpit-warn/40 bg-cockpit-warn/10 text-cockpit-warn",
  bad: "border-cockpit-bad/40 bg-cockpit-bad/10 text-cockpit-bad",
  info: "border-cockpit-info/40 bg-cockpit-info/10 text-cockpit-info",
};

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: Tone;
}) {
  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${TONE_CLASS[tone]}`}
    >
      {children}
    </span>
  );
}

export function KeyValue({
  label,
  value,
}: {
  label: string;
  value: ReactNode;
}) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-cockpit-border/50 py-1.5 last:border-b-0">
      <span className="text-sm text-cockpit-muted">{label}</span>
      <span className="font-mono text-sm text-cockpit-text">{value}</span>
    </div>
  );
}
