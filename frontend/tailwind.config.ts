import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4ff',
          100: '#d9e2ff',
          200: '#b0c4ff',
          300: '#809eff',
          400: '#5c7dff',
          500: '#3b5bff',
          600: '#2c45cc',
          700: '#213299',
          800: '#162066',
          900: '#0b0f33',
        },
      },
    },
  },
  plugins: [],
}
export default config
