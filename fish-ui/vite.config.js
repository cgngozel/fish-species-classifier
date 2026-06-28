import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react' // Eklenti adı bu şekilde olmalı
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})