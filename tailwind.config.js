/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html","./static/script/*.js"],
  theme: {
    extend: {
      gridTemplateColumns:{
        '2a':"70% 30%"
      }
    },
  },
  plugins: [],
}

