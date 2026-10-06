/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        nexus: {
          bg: '#0d0e12',
          card: '#15171e',
          cardHover: '#1a1c25',
          border: '#222533',
          borderLight: '#2c2f42',
          textMuted: '#8b8fa3',
          purple: '#9333ea',
          pink: '#ec4899',
          green: '#22c55e',
          cyan: '#06b6d4',
          amber: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
