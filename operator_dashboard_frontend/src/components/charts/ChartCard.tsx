/**
 * Framing for a chart panel: a title, an optional subtitle, the chart itself,
 * and a provenance footnote. Server component — it renders no chart, it only
 * wraps one.
 */
import type { ReactNode } from "react";
import { Card, CardTitle } from "@/components/ui";

export function ChartCard({
  title,
  subtitle,
  badges,
  children,
  footer,
}: {
  title: string;
  subtitle?: string;
  badges?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <Card className="flex flex-col">
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <CardTitle>{title}</CardTitle>
        {badges ? (
          <div className="mb-3 flex flex-wrap gap-2">{badges}</div>
        ) : null}
      </div>
      {subtitle ? (
        <p className="mb-3 text-xs text-cockpit-muted">{subtitle}</p>
      ) : null}
      {children}
      {footer ? <div className="mt-3">{footer}</div> : null}
    </Card>
  );
}
