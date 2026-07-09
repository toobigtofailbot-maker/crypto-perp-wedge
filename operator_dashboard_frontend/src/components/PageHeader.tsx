/** Route title + breadcrumb + per-page read-only/authority banners. */
import type { ReactNode } from "react";
import { AuthorityBanner, ReadOnlyBanner } from "@/components/Banners";

export function PageHeader({
  title,
  breadcrumb,
  description,
  children,
}: {
  title: string;
  breadcrumb?: string[];
  description?: string;
  children?: ReactNode;
}) {
  return (
    <header className="flex flex-col gap-3">
      {breadcrumb && breadcrumb.length > 0 ? (
        <nav className="text-xs text-cockpit-muted" aria-label="Breadcrumb">
          {breadcrumb.join(" / ")}
        </nav>
      ) : null}
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold text-cockpit-heading">{title}</h1>
        {description ? (
          <p className="text-sm text-cockpit-muted">{description}</p>
        ) : null}
      </div>
      <ReadOnlyBanner />
      <AuthorityBanner />
      {children}
    </header>
  );
}
