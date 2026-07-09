/**
 * Non-authority banners. These make the shell's read-only, no-control posture
 * explicit on every page.
 */

export function ReadOnlyBanner() {
  return (
    <div className="rounded-md border border-cockpit-accent-dim bg-cockpit-accent/5 px-3 py-2 text-xs text-cockpit-muted">
      <span className="font-semibold text-cockpit-accent">READ-ONLY</span> — This
      operator dashboard shell displays derived projections for inspection only.
      It has no controls and performs no writes, runs, approvals, promotions,
      crossings, trades, notifications, or scheduler actions.
    </div>
  );
}

export function AuthorityBanner() {
  return (
    <div className="rounded-md border border-cockpit-border bg-cockpit-panel-2 px-3 py-2 text-xs text-cockpit-muted">
      <span className="font-semibold text-cockpit-text">Authority state:</span>{" "}
      committed repo artifacts remain truth. This shell is not an execution,
      approval, ranking, readiness, promotion, runtime, or paper/live authority.
      Displayed values are a presentation layer over API-shaped fixtures.
    </div>
  );
}
