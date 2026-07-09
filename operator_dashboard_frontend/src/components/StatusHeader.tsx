/**
 * Global status header. Static, derived from the committed dashboard-summary
 * fixture. Displays posture and authority state only — no controls.
 */
import { Badge } from "@/components/ui";
import { fixtures } from "@/lib/fixtures";

export function StatusHeader() {
  const summary = fixtures.dashboardSummary();
  const posture = summary.data.system_posture ?? "unknown";
  const paper = summary.data.paper_trading?.status ?? "unavailable";
  const live = summary.data.live_trading?.status ?? "unavailable";

  return (
    <header className="flex flex-wrap items-center gap-3 border-b border-cockpit-border bg-cockpit-bg px-6 py-3">
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-cockpit-muted">
          Posture
        </span>
        <Badge tone="info">{posture}</Badge>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-cockpit-muted">
          Mode
        </span>
        <Badge tone="good">read-only</Badge>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-cockpit-muted">
          Paper
        </span>
        <Badge tone="warn">{paper}</Badge>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-cockpit-muted">
          Live
        </span>
        <Badge tone="warn">{live}</Badge>
      </div>
      <div className="ml-auto text-[11px] text-cockpit-muted">
        Local-first · no runtime / paper / live contact
      </div>
    </header>
  );
}
