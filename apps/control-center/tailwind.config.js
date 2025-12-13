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
        primary: {
          DEFAULT: '#9BB4C0',
          light: '#B8D0DC',
          dark: '#7A9BA8',
        },
        secondary: {
          DEFAULT: '#A18D6D',
          light: '#B8A88A',
          dark: '#8A7555',
        },
        error: {
          DEFAULT: '#703B3B',
          light: '#8A4F4F',
          dark: '#5A2F2F',
        },
        background: {
          DEFAULT: '#E1D0B3',
          light: '#F0E5D0',
          dark: '#D2C19A',
        },
        border: "#A18D6D",
        input: "#A18D6D",
        ring: "#9BB4C0",
        foreground: "#2A1F1F",
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

