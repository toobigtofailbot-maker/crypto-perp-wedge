/** Honest empty / loading / unavailable / placeholder states. */
import type { ReactNode } from "react";
import { Card, CardTitle } from "@/components/ui";

export function UnavailableState({
  title = "Unavailable",
  reason,
}: {
  title?: string;
  reason: string;
}) {
  return (
    <Card className="border-dashed">
      <CardTitle>{title}</CardTitle>
      <p className="text-sm text-cockpit-muted">{reason}</p>
    </Card>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-md border border-dashed border-cockpit-border px-4 py-8 text-center text-sm text-cockpit-muted">
      {message}
    </div>
  );
}

export function LoadingState({ message = "Loading…" }: { message?: string }) {
  return (
    <div className="rounded-md border border-dashed border-cockpit-border px-4 py-8 text-center text-sm text-cockpit-muted">
      {message}
    </div>
  );
}

/**
 * A card that documents a panel deferred to a later package. Used by shell
 * pages that intentionally have no analytical content yet.
 */
export function PlaceholderCard({
  title,
  children,
}: {
  title: string;
  children?: ReactNode;
}) {
  return (
    <Card className="border-dashed">
      <CardTitle>{title}</CardTitle>
      <p className="text-sm text-cockpit-muted">
        {children ??
          "Scaffold only. This panel is built by a later dashboard package."}
      </p>
    </Card>
  );
}
