/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#fff0ed",
          100: "#ffddd5",
          200: "#ffb8a5",
          300: "#ff8a6b",
          400: "#ff5530",
          500: "#e8360f",
          600: "#cc3318",  // primary — matches logo red
          700: "#a82b14",
          800: "#8a2410",
          900: "#6b1a08",
        },
      },
      fontFamily: {
        sans: ["Cairo", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
