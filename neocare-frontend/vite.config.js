import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  cacheDir: "node_modules/.vite",
  server: {
    host: true, // Expone el servidor para que Windows lo vea sin problemas
    port: 5173
  }
})
