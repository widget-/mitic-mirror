import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: process.env.VITE_BASE_URL || '/',
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:3001'
    }
  }
})
