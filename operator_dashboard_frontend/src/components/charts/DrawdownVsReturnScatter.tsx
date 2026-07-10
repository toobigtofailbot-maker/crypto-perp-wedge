"use client";

/**
 * Committed per-variant max drawdown against committed per-variant return.
 *
 * One dot per variant result row. Position restates two committed numbers side
 * by side; it implies no preference between quadrants, selects no winner, and
 * marks nothing as admissible. Rows missing either value are omitted rather
 * than placed at the origin — the caller reports how many.
 */

import { useMemo } from "react";
import { EChart, type CockpitChartOption } from "@/components/charts/EChart";
import { axisStyle, COCKPIT, gridStyle, tooltipStyle } from "@/lib/chartTheme";

export interface ScatterPoint {
  /** Committed `metrics.drawdown`. */
  x: number;
  /** Committed `metrics.return_pct`. */
  y: number;
  /** `RP-id · VAR-id`, for the tooltip. */
  label: string;
}

const asPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

export function DrawdownVsReturnScatter({
  points,
  height = 260,
}: {
  points: ScatterPoint[];
  height?: number;
}) {
  const option = useMemo<CockpitChartOption>(() => {
    return {
      grid: gridStyle,
      tooltip: {
        trigger: "item",
        ...tooltipStyle,
        formatter: (params: unknown) => {
          const { data } = params as { data: [number, number, string] };
          const [x, y, label] = data;
          return `${label}<br/>drawdown ${asPercent(x)}<br/>return ${asPercent(y)}`;
        },
      },
      xAxis: {
        type: "value",
        name: "max drawdown",
        nameLocation: "middle",
        nameGap: 26,
        nameTextStyle: { color: COCKPIT.muted, fontSize: 10 },
        ...axisStyle,
        axisLabel: { ...axisStyle.axisLabel, formatter: asPercent },
      },
      yAxis: {
        type: "value",
        name: "return",
        nameTextStyle: { color: COCKPIT.muted, fontSize: 10 },
        ...axisStyle,
        axisLabel: { ...axisStyle.axisLabel, formatter: asPercent },
      },
      series: [
        {
          type: "scatter",
          symbolSize: 7,
          data: points.map((p) => [p.x, p.y, p.label]),
          itemStyle: { color: COCKPIT.info, opacity: 0.75 },
        },
      ],
    };
  }, [points]);

  return (
    <EChart
      option={option}
      height={height}
      ariaLabel={`Scatter of per-variant max drawdown against return across ${points.length} committed variant rows`}
    />
  );
}
