/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          DEFAULT: "#134e40",
          50: "#f0f7f4",
          100: "#dbeef5",
          200: "#b8ded6",
          300: "#80c2b2",
          400: "#4da38e",
          500: "#2a8570",
          600: "#1e6b5a",
          700: "#185648",
          800: "#134e40",
          900: "#0d3b30",
          950: "#06221c",
        },
        saffron: {
          DEFAULT: "#e69943",
          50: "#fef8ee",
          100: "#fdedd6",
          200: "#fad7ab",
          300: "#f5bd76",
          400: "#efa044",
          500: "#e68424",
          600: "#c76617",
          700: "#9e4c16",
        },
        cream: {
          DEFAULT: "#FAF7F0",
          50: "#FFFFFF",
          100: "#FAF7F0",
          200: "#F4EFE6",
          300: "#EAE2D5",
        },
        sage: {
          light: "#DCECDF",
          DEFAULT: "#C5DFCA",
          dark: "#9EBAA4",
        },
        charcoal: "#263238",
        mutedGreen: "#718078",
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', '"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Noto Sans"', '"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        indic: ['"Noto Sans"', '"Noto Sans Devanagari"', '"Noto Sans Bengali"', '"Noto Sans Tamil"', '"Noto Sans Telugu"', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(19, 78, 64, 0.08)',
        'elevated': '0 10px 30px -4px rgba(19, 78, 64, 0.12)',
        'mic': '0 0 0 10px rgba(19, 78, 64, 0.08), 0 0 0 24px rgba(19, 78, 64, 0.04), 0 0 0 42px rgba(19, 78, 64, 0.02)',
        'mic-active': '0 0 0 14px rgba(19, 78, 64, 0.14), 0 0 0 32px rgba(19, 78, 64, 0.08), 0 0 0 54px rgba(19, 78, 64, 0.04)',
      },
      animation: {
        'pulse-subtle': 'pulseSubtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ripple': 'ripple 2.5s cubic-bezier(0, 0.2, 0.8, 1) infinite',
        'float-slow': 'floatSlow 6s ease-in-out infinite',
      },
      keyframes: {
        pulseSubtle: {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.025)', opacity: '0.96' },
        },
        ripple: {
          '0%': { transform: 'scale(0.95)', opacity: '0.8' },
          '50%': { transform: 'scale(1.12)', opacity: '0.4' },
          '100%': { transform: 'scale(1.25)', opacity: '0' },
        },
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
      }
    },
  },
  plugins: [],
};
