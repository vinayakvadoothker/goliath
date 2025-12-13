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
      colors: {
        border: "#1a1a1a",
        input: "#1a1a1a",
        ring: "#1a1a1a",
        background: "#0a0a0a",
        foreground: "#f5f5f5",
        primary: {
          DEFAULT: "#3b82f6",
          foreground: "#f5f5f5",
        },
        secondary: {
          DEFAULT: "#141414",
          foreground: "#f5f5f5",
        },
        destructive: {
          DEFAULT: "#ef4444",
          foreground: "#f5f5f5",
        },
        muted: {
          DEFAULT: "#141414",
          foreground: "#a0a0a0",
        },
        accent: {
          DEFAULT: "#3b82f6",
          foreground: "#f5f5f5",
        },
        popover: {
          DEFAULT: "#141414",
          foreground: "#f5f5f5",
        },
        card: {
          DEFAULT: "#141414",
          foreground: "#f5f5f5",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

