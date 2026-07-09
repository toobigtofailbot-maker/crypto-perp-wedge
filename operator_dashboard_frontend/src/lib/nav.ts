/**
 * Sidebar navigation model for the operator dashboard shell.
 * Every entry is a read-only inspection route. No entry triggers an action.
 */

export interface NavItem {
  label: string;
  href: string;
}

export interface NavGroup {
  label: string;
  href: string;
  items?: NavItem[];
}

export const NAV_GROUPS: NavGroup[] = [
  { label: "Command Center", href: "/" },
  {
    label: "Research Lab",
    href: "/research",
    items: [
      { label: "Jobs", href: "/research/jobs" },
      { label: "Result Populations", href: "/research/result-populations" },
      { label: "Families", href: "/research/families" },
      { label: "Blockers", href: "/research/blockers" },
      { label: "Robustness", href: "/research/robustness" },
    ],
  },
  { label: "Strategies", href: "/strategies" },
  { label: "Candidates", href: "/candidates" },
  {
    label: "Reports",
    href: "/reports",
    items: [
      { label: "Daily", href: "/reports/daily" },
      { label: "Weekly", href: "/reports/weekly" },
      { label: "Strategy Review", href: "/reports/strategy-review" },
      { label: "Main", href: "/reports/main" },
    ],
  },
  {
    label: "System / Data",
    href: "/system",
    items: [
      { label: "Data", href: "/system/data" },
      { label: "Validators", href: "/system/validators" },
      { label: "Provenance", href: "/system/provenance" },
      { label: "Blockers", href: "/system/blockers" },
    ],
  },
  { label: "Agent Inbox", href: "/agent-inbox" },
  { label: "Paper Trading", href: "/paper" },
  { label: "Live Trading", href: "/live" },
];
