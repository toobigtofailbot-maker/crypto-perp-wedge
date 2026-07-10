"use client";

/**
 * Thin client-side ECharts host.
 *
 * Only the chart types and components the cockpit actually draws are
 * registered, so the bundle carries a fraction of the full ECharts build. The
 * only client state here is the chart instance itself and a resize observer —
 * there are no handlers that submit, mutate, or fetch anything. Hover tooltips
 * are visual affordances and reach nothing outside the canvas.
 */

import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { BarChart, ScatterChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { ComposeOption, EChartsType } from "echarts/core";
import type { BarSeriesOption, ScatterSeriesOption } from "echarts/charts";
import type {
  GridComponentOption,
  TooltipComponentOption,
  LegendComponentOption,
} from "echarts/components";

echarts.use([
  BarChart,
  ScatterChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  CanvasRenderer,
]);

export type CockpitChartOption = ComposeOption<
  | BarSeriesOption
  | ScatterSeriesOption
  | GridComponentOption
  | TooltipComponentOption
  | LegendComponentOption
>;

export function EChart({
  option,
  height = 220,
  ariaLabel,
}: {
  option: CockpitChartOption;
  height?: number;
  /** Describes the rendered series for assistive technology. */
  ariaLabel: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<EChartsType | null>(null);

  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;

    const chart = echarts.init(element, undefined, { renderer: "canvas" });
    chartRef.current = chart;

    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(element);

    return () => {
      observer.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    // `notMerge` so a changed series never leaves a stale one underneath it.
    chartRef.current?.setOption(option, true);
  }, [option]);

  return (
    <div
      ref={containerRef}
      role="img"
      aria-label={ariaLabel}
      style={{ height }}
      className="w-full"
    />
  );
}
