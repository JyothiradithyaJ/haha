/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F6F4EE",
        card: "#FFFEFB",
        ink: "#1C1B18",
        "ink-soft": "#5B564C",
        "ink-faint": "#8C8676",
        line: "#DBD5C4",
        "line-strong": "#C7BFA8",
        oxblood: {
          DEFAULT: "#7A2E2A",
          dark: "#5E211E",
          light: "#9C4A44",
          tint: "#F3E6E2",
        },
        brass: {
          DEFAULT: "#B8892F",
          tint: "#F6ECD6",
        },
        moss: {
          DEFAULT: "#4B5E45",
          tint: "#E9EDE3",
        },
        /* category identity colors */
        notes: { DEFAULT: "#1E7A4C", dark: "#155C39", light: "#3FA873", tint: "#E4F3EA" },
        papers: { DEFAULT: "#C1660B", dark: "#9A4F08", light: "#E88A34", tint: "#FBEBDA" },
        extras: { DEFAULT: "#C23B3B", dark: "#992D2D", light: "#E1655F", tint: "#FBE4E2" },
        refs: { DEFAULT: "#6B3FA0", dark: "#502E79", light: "#9067C4", tint: "#EEE6F7" },
      },
      fontFamily: {
        serif: ["'Source Serif 4'", "'Iowan Old Style'", "Georgia", "serif"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tightish: "-0.015em",
      },
      boxShadow: {
        card: "0 1px 2px rgba(28,27,24,0.04), 0 8px 24px -12px rgba(28,27,24,0.10)",
        lift: "0 4px 10px rgba(28,27,24,0.06), 0 20px 40px -18px rgba(28,27,24,0.18)",
        glow: "0 2px 8px -2px var(--tw-shadow-color), 0 16px 32px -18px var(--tw-shadow-color)",
      },
      backgroundImage: {
        grid: "linear-gradient(to right, rgba(28,27,24,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(28,27,24,0.05) 1px, transparent 1px)",
      },
      maxWidth: {
        content: "1180px",
      },
    },
  },
  plugins: [],
};
