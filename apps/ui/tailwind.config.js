/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      borderColor: {
        DEFAULT: "#262626",
      },
      colors: {
        border: "#262626", // Dark grey border for high contrast against #020202
        input: "#262626",
        ring: "#ffffff", // White ring
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "#ffffff", // White Primary
          foreground: "#000000", // Black Text
        },
        secondary: {
          DEFAULT: "#262626", // Dark Grey
          foreground: "#ffffff",
        },
        destructive: {
          DEFAULT: "#ef4444",
          foreground: "#ffffff",
        },
        muted: {
          DEFAULT: "#262626",
          foreground: "#a3a3a3",
        },
        accent: {
          DEFAULT: "#262626",
          foreground: "#ffffff",
        },
        popover: {
          DEFAULT: "#020202", // Same as bg
          foreground: "#d9d9d9",
        },
        card: {
          DEFAULT: "#020202", // Same as bg
          foreground: "#d9d9d9",
        },
        // Goliath Custom Colors
        success: {
          DEFAULT: "#ffffff",
          foreground: "#000000",
        },
        decision: {
          DEFAULT: "#ffffff",
          foreground: "#000000",
        },
        outcome: {
          DEFAULT: "#737373", // Neutral grey
          foreground: "#ffffff",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
      animation: {
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

