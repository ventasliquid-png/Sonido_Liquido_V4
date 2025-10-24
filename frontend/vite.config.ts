import { fileURLToPath, URL } from 'node:url' // Mantenemos por si acaso, aunque path lo reemplaza
import path from 'node:path' // La forma robusta de manejar rutas
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue(), // Inicialización simple y estándar del plugin de Vue
  ],
  resolve: {
    alias: {
      // La definición robusta del alias '@' que sabemos que funciona
      '@': path.resolve(__dirname, './src'),
    }
  },
  // SIN sección 'esbuild'
  // SIN sección 'optimizeDeps' por ahora
})