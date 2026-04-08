import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#2563eb',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        surface: {
          DEFAULT: '#F9F8F5',
          50: '#F9F8F5',
          100: '#f3f2ef',
        },
        border: {
          DEFAULT: '#EAEAE5',
          strong: '#c4c0b8',
        },
        ink: {
          DEFAULT: '#1e293b',
          muted: '#6b7280',
          faint: '#9ca3af',
          dark: '#111827',
          darkest: '#0f172a',
        },
      },
      fontFamily: {
        display: ['Instrument Serif', 'Georgia', 'serif'],
        sans: ['DM Sans', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        bubble: '1rem',
        'bubble-tail-user': '1rem 1rem 0.2rem 1rem',
        'bubble-tail-assistant': '0.2rem 1rem 1rem 1rem',
      },
      boxShadow: {
        topbar: '0 1px 4px rgba(0,0,0,0.04)',
        card: '0 1px 4px rgba(0,0,0,0.04)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.07)',
        bubble: '0 2px 10px rgba(37,99,235,0.22)',
        modal: '0 8px 24px rgba(0,0,0,0.08)',
        icon: '0 8px 28px rgba(0,0,0,0.18)',
      },
      animation: {
        'slide-in-right': 'slideInRight 0.28s cubic-bezier(0.22,1,0.36,1)',
        'fade-in': 'fadeIn 0.2s ease',
        'thinking': 'thinking 1.2s ease-in-out infinite',
      },
      keyframes: {
        slideInRight: {
          from: { opacity: '0', transform: 'translateX(18px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        thinking: {
          '0%, 80%, 100%': { transform: 'scale(0)', opacity: '0.3' },
          '40%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

export default config
