/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/templates/**/*.html',
    './node_modules/flowbite/**/*.js'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          "50":"#F2F0FA",
          "100":"#E4E0F5",
          "200":"#DCD7EA",
          "300":"#CAB3FF",
          "400":"#A796D9",
          "500":"#927ed0",
          "600":"#8169C9",
          "700":"#745AC4",
          "800":"#463187",
          "900":"#2F205A",
          "950":"#20153C"
        },
        gray: {
          "50":"##F5F5F5",
          "100":"#E2E2E2",
          "200":"#D6D6D6",
          "300":"#C8C8C5",
          "400":"#ADADAD",
          "500":"#9C9C96",
          "600":"#888881",
          "700":"#74746D",
          "800":"#696963",
          "900":"#4A4A45",
          "950":"#1b1b1b"
        },
        accent: "#f4e846"
      }
    },
    fontFamily: {
      'body': ['General Sans', 'sans-serif'],
      'sans': ['General Sans', 'sans-serif']
    }
  },
  plugins: [
    require('flowbite/plugin')
  ]
}

