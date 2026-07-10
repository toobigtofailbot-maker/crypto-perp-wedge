"use client";

/**
 * A bar chart over committed categorical tallies — queue states, registry
 * verdicts, funnel stages, report state distributions.
 *
 * Bar order is the order the caller supplies, which is the committed display
 * order. Length encodes a count and nothing else: it is not a rank, a score,
 * or a preference.
 */

import { useMemo } from "react";
import { EChart, type CockpitChartOption } from "@/components/charts/EChart";
import { axisStyle, gridStyle, tooltipStyle, TONE_COLOR } from "@/lib/chartTheme";
import { humanize, type Tone } from "@/lib/status";

export interface CategoryBar {
  label: string;
  count: number;
  tone?: Tone;
}

export function CategoricalCountChart({
  bars,
  horizontal = false,
  height,
  ariaLabel,
}: {
  bars: CategoryBar[];
  /** Horizontal bars read better for long labels and funnel stages. */
  horizontal?: boolean;
  height?: number;
  ariaLabel: string;
}) {
  const option = useMemo<CockpitChartOption>(() => {
    const labels = bars.map((b) => humanize(b.label));
    const values = bars.map((b) => ({
      value: b.count,
      itemStyle: { color: TONE_COLOR[b.tone ?? "info"] },
    }));

    const categoryAxis = {
      type: "category" as const,
      data: labels,
      ...axisStyle,
      splitLine: { show: false },
      axisLabel: {
        ...axisStyle.axisLabel,
        // Long queue-state names need room; horizontal bars get full labels.
        rotate: horizontal ? 0 : 30,
        width: horizontal ? 130 : undefined,
        overflow: "truncate" as const,
      },
    };
    const valueAxis = {
      type: "value" as const,
      ...axisStyle,
      minInterval: 1,
    };

    return {
      grid: { ...gridStyle, left: horizontal ? 8 : gridStyle.left },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        ...tooltipStyle,
      },
      xAxis: horizontal ? valueAxis : categoryAxis,
      yAxis: horizontal ? { ...categoryAxis, inverse: true } : valueAxis,
      series: [
        {
          type: "bar",
          data: values,
          barMaxWidth: 28,
          label: {
            show: true,
            position: horizontal ? "right" : "top",
            color: "#d7dee8",
            fontSize: 10,
            fontFamily: "ui-monospace, monospace",
          },
        },
      ],
    };
  }, [bars, horizontal]);

  const fallbackHeight = horizontal ? Math.max(140, bars.length * 34 + 40) : 220;

  return (
    <EChart
      option={option}
      height={height ?? fallbackHeight}
      ariaLabel={ariaLabel}
    />
  );
}
