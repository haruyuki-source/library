import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// Vite 配置:Vue 插件、路径别名、后端代理
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // 前端以 /api 开头的请求转发到 Flask 后端(端口 5000)
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
