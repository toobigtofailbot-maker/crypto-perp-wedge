"use client";

/**
 * Outcome distribution across result populations, as stacked horizontal bars —
 * one bar per population, one segment per committed outcome category.
 *
 * This is the charted form of the committed `outcome_counts` block. Every
 * population's full committed denominator is shown; no winner-only slice is
 * taken and no bucket is dropped for looking bad.
 */

import { useMemo } from "react";
import { EChart, type CockpitChartOption } from "@/components/charts/EChart";
import { axisStyle, gridStyle, tooltipStyle, TONE_COLOR } from "@/lib/chartTheme";
import { humanize, type Tone } from "@/lib/status";

export interface OutcomePopulation {
  id: string;
  counts: Record<string, number>;
}

export function OutcomeDistributionChart({
  populations,
  categoryTones,
  ariaLabel,
}: {
  populations: OutcomePopulation[];
  /** Tone per outcome category, so `failed` is never rendered as healthy. */
  categoryTones: Record<string, Tone>;
  ariaLabel: string;
}) {
  const option = useMemo<CockpitChartOption>(() => {
    // Union of every category present, so a population missing a bucket
    // contributes 0 to that stack rather than shifting the colours.
    const categories = [
      ...new Set(populations.flatMap((p) => Object.keys(p.counts))),
    ];

    return {
      // Extra bottom margin clears the legend, which sits at the card's floor.
      grid: { ...gridStyle, left: 8, top: 8, bottom: 40 },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        ...tooltipStyle,
      },
      legend: {
        type: "scroll",
        bottom: 0,
        textStyle: { color: "#8a97ab", fontSize: 10 },
        itemWidth: 10,
        itemHeight: 10,
      },
      xAxis: { type: "value", ...axisStyle, minInterval: 1 },
      yAxis: {
        type: "category",
        inverse: true,
        data: populations.map((p) => p.id),
        ...axisStyle,
        splitLine: { show: false },
        axisLabel: {
          ...axisStyle.axisLabel,
          fontFamily: "ui-monospace, monospace",
        },
      },
      series: categories.map((category) => ({
        type: "bar" as const,
        stack: "outcome",
        name: humanize(category),
        data: populations.map((p) => p.counts[category] ?? 0),
        itemStyle: { color: TONE_COLOR[categoryTones[category] ?? "neutral"] },
        barMaxWidth: 22,
      })),
    };
  }, [populations, categoryTones]);

  return (
    <EChart
      option={option}
      height={Math.max(190, populations.length * 30 + 90)}
      ariaLabel={ariaLabel}
    />
  );
}
