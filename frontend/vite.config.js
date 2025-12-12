import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  server: {
    host: true,    
    port: 5173,       
    watch: {
      usePolling: true 
    },
    // Настройка прокси чтобы запросы летели на бэк
    proxy: {
      '/places': {
        target: 'http://backend:8000', 
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
