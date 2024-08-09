/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      maxWidth: {
        'custom': '88rem', // Define custom max-width
      },
    },
  },
  plugins: [],
}