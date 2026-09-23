/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Brand palette taken directly from the organization's logo (logo.svg):
        // deep green #00401A and gold #CAA202.
        fire: {
          50: '#eaf3ee', 100: '#cfe4d8', 200: '#a3cab3', 300: '#6fac86',
          400: '#3f8c60', 500: '#237347', 600: '#0f5c34', 700: '#0a4c29',
          800: '#00401a', 900: '#002911',
        },
        gold: {
          50: '#fbf6e6', 100: '#f5e9c2', 200: '#ecd88a', 300: '#e2c757',
          400: '#d9b52e', 500: '#caa202', 600: '#a17f02', 700: '#7a6101',
          800: '#574501', 900: '#362b01',
        },
      },
    },
  },
  plugins: [],
}
