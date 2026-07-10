/**
 * Chart palette and shared axis/grid/tooltip fragments for the cockpit.
 *
 * Colours mirror the `cockpit.*` Tailwind tokens in `tailwind.config.ts`.
 * ECharts needs literal colours rather than Tailwind classes, so they are
 * duplicated here deliberately; keep the two in step.
 */

import type { Tone } from "@/lib/status";

export const COCKPIT = {
  panel: "#111721",
  panel2: "#161d29",
  border: "#232c3b",
  muted: "#8a97ab",
  text: "#d7dee8",
  heading: "#f2f5fa",
  accent: "#38bdf8",
  good: "#34d399",
  warn: "#fbbf24",
  bad: "#f87171",
  info: "#818cf8",
} as const;

export const TONE_COLOR: Record<Tone, string> = {
  neutral: COCKPIT.muted,
  good: COCKPIT.good,
  warn: COCKPIT.warn,
  bad: COCKPIT.bad,
  info: COCKPIT.info,
};

/** Axis styling shared by every cockpit chart. */
export const axisStyle = {
  axisLine: { lineStyle: { color: COCKPIT.border } },
  axisTick: { show: false },
  axisLabel: { color: COCKPIT.muted, fontSize: 10 },
  splitLine: { lineStyle: { color: COCKPIT.border, opacity: 0.4 } },
};

/** Tooltip styling. Tooltips are hover-only visual affordances. */
export const tooltipStyle = {
  backgroundColor: COCKPIT.panel2,
  borderColor: COCKPIT.border,
  textStyle: { color: COCKPIT.text, fontSize: 11 },
  padding: [6, 8],
};

/** Compact grid: charts sit inside cards that already supply padding. */
export const gridStyle = {
  top: 16,
  right: 16,
  bottom: 24,
  left: 48,
  containLabel: true,
};
