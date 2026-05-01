/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'rev-dark': '#191c1f',
        'rev-white': '#ffffff',
        'rev-surface': '#f4f4f4',
        'rev-blue': '#494fdf',
        'rev-teal': '#00a87e',
        'rev-danger': '#e23b4a',
        'rev-warning': '#ec7e00',
        'rev-yellow': '#b09000',
        'rev-slate': '#505a63',
        'rev-muted': '#8d969e',
        'rev-border': '#c9c9cd',
      },
      backgroundColor: {
        'card': '#1e2225',
      },
      borderRadius: {
        'pill': '9999px',
        'card': '20px',
        'sm': '12px',
      },
      fontSize: {
        'display': ['136px', { lineHeight: '1.00', letterSpacing: '-2.72px' }],
        'hero': ['80px', { lineHeight: '1.00', letterSpacing: '-0.8px' }],
        'heading': ['48px', { lineHeight: '1.21', letterSpacing: '-0.48px' }],
        'subhead': ['40px', { lineHeight: '1.20', letterSpacing: '-0.4px' }],
        'body-lg': ['18px', { lineHeight: '1.56', letterSpacing: '-0.09px' }],
        'body': ['16px', { lineHeight: '1.50', letterSpacing: '0.24px' }],
        'body-semi': ['16px', { lineHeight: '1.50', letterSpacing: '0.16px' }],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}
