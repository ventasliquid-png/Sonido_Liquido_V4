// frontend/vite.config.ts (DESACTIVAR HMR)
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [ vue() ],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
  },
  // --- AÑADIDO: Desactivar HMR ---
  server: {
    hmr: false // Desactiva Hot Module Replacement
  }
  // ---
})