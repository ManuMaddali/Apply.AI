/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      },
      colors: {
        // Tokyo Night theme colors
        tokyo: {
          bg: '#1a1b26',
          'bg-light': '#24283b',
          'bg-dark': '#16161e',
          text: '#c0caf5',
          'text-dim': '#9aa5ce',
          accent: '#7aa2f7',
          'accent-bright': '#bb9af7',
          success: '#9ece6a',
          warning: '#e0af68',
          error: '#f7768e',
          purple: '#bb9af7',
          cyan: '#7dcfff',
          green: '#9ece6a',
          orange: '#ff9e64',
          red: '#f7768e',
          yellow: '#e0af68',
          blue: '#7aa2f7'
        }
      }
    },
  },
  plugins: [],
}
