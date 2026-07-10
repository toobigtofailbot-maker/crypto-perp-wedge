"use client";

/**
 * Histograms over per-variant metrics committed in result-population artifacts.
 *
 * The bars count real observations. A bin with zero height means no variant
 * landed in that range — it is an observed absence, not a filled-in zero. When
 * a sample has no observations at all, no chart is drawn: callers render an
 * unavailable state instead.
 *
 * These are offline research backtest outputs. A distribution shown here is a
 * description of what a sweep produced, never a performance claim or a ranking.
 */

import { useMemo } from "react";
import { EChart, type CockpitChartOption } from "@/components/charts/EChart";
import {
  axisStyle,
  COCKPIT,
  GRID_TOP_WITH_AXIS_NAME,
  gridStyle,
  tooltipStyle,
} from "@/lib/chartTheme";
import { formatNumber, histogram } from "@/lib/chartData";

function MetricHistogramChart({
  values,
  binCount = 12,
  color,
  /** How a bin boundary is rendered on the axis and in the tooltip. */
  formatBound = formatNumber,
  ariaLabel,
  height = 220,
}: {
  values: number[];
  binCount?: number;
  color: string;
  formatBound?: (value: number) => string;
  ariaLabel: string;
  height?: number;
}) {
  const option = useMemo<CockpitChartOption>(() => {
    const bins = histogram(values, binCount);

    return {
      // The y-axis is named, so reserve room for the name above the grid.
      grid: { ...gridStyle, top: GRID_TOP_WITH_AXIS_NAME },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        ...tooltipStyle,
        formatter: (params: unknown) => {
          const first = Array.isArray(params) ? params[0] : params;
          const index = (first as { dataIndex: number }).dataIndex;
          const bin = bins[index];
          if (!bin) return "";
          const count = bin.count;
          return `${formatBound(bin.start)} … ${formatBound(bin.end)}<br/>${count} variant${count === 1 ? "" : "s"}`;
        },
      },
      xAxis: {
        type: "category",
        data: bins.map((b) => formatBound(b.start)),
        ...axisStyle,
        splitLine: { show: false },
        axisLabel: { ...axisStyle.axisLabel, rotate: 30 },
      },
      yAxis: {
        type: "value",
        name: "variants",
        nameTextStyle: { color: COCKPIT.muted, fontSize: 10 },
        ...axisStyle,
        minInterval: 1,
      },
      series: [
        {
          type: "bar",
          data: bins.map((b) => b.count),
          itemStyle: { color },
          barCategoryGap: "8%",
        },
      ],
    };
  }, [values, binCount, color, formatBound]);

  return <EChart option={option} height={height} ariaLabel={ariaLabel} />;
}

const asPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

/** Distribution of committed per-variant `metrics.return_pct`. */
export function ReturnDistributionChart({
  values,
  binCount,
}: {
  values: number[];
  binCount?: number;
}) {
  return (
    <MetricHistogramChart
      values={values}
      binCount={binCount}
      color={COCKPIT.accent}
      formatBound={asPercent}
      ariaLabel={`Histogram of per-variant return_pct across ${values.length} committed variant rows`}
    />
  );
}

/**
 * Distribution of committed per-variant `metrics.drawdown`.
 *
 * This is the scalar max-drawdown recorded per variant, not a drawdown curve
 * over time — the API projects no time series. See `UnavailableChartState` on
 * the result-populations route for the curve itself.
 */
export function DrawdownDistributionChart({
  values,
  binCount,
}: {
  values: number[];
  binCount?: number;
}) {
  return (
    <MetricHistogramChart
      values={values}
      binCount={binCount}
      color={COCKPIT.warn}
      formatBound={asPercent}
      ariaLabel={`Histogram of per-variant max drawdown across ${values.length} committed variant rows`}
    />
  );
}
