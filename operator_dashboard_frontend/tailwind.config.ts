import type { Config } from "tailwindcss";

/**
 * Dark operator-cockpit visual posture. Colors are defined here (not via a
 * runtime theme service) so the shell stays static and self-contained.
 */
const config: Config = {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cockpit: {
          bg: "#0a0e14",
          panel: "#111721",
          "panel-2": "#161d29",
          border: "#232c3b",
          muted: "#8a97ab",
          text: "#d7dee8",
          heading: "#f2f5fa",
          accent: "#38bdf8",
          "accent-dim": "#0e7490",
          good: "#34d399",
          warn: "#fbbf24",
          bad: "#f87171",
          info: "#818cf8",
        },
      },
      fontFamily: {
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
