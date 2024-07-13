/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}"],
  daisyui: {
    themes: ["corporate"],
  },
  plugins: [
    require('daisyui'),
  ],
}

