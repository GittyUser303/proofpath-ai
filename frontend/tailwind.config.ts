import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        display: ["Sora", "Inter", "ui-sans-serif"],
      },
      colors: {
        obsidian: "#070A0F",
        panel: "#101722",
        line: "rgba(148, 163, 184, 0.18)",
        cyan: "#49D3FF",
        mint: "#52E09B",
        amber: "#F7C45A",
      },
      boxShadow: {
        glow: "0 0 32px rgba(73, 211, 255, 0.18)",
        panel: "0 22px 60px rgba(0, 0, 0, 0.36)",
      },
    },
  },
  plugins: [],
};

export default config;
