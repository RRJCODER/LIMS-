import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2d6a2d',
          50: '#f0fff0',
          100: '#dcfce7',
          200: '#bbf7d0',
          500: '#2d6a2d',
          600: '#256025',
          700: '#1d4f1d',
          800: '#163c16',
          900: '#0e280e',
        },
        olive: {
          DEFAULT: '#6b7c3e',
          light: '#8fa04f',
          dark: '#4a5928',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config
