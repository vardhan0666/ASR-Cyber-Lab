/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        risk: {
          critical: "#7f1d1d",
          high: "#b91c1c",
          medium: "#b45309",
          low: "#1d4ed8",
          info: "#374151",
        },
      },
    },
  },
  plugins: [],
};