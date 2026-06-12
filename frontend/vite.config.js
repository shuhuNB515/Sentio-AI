import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // GitHub Pages 部署路径：仓库名为 Sentio-AI
  base: '/Sentio-AI/',
  build: {
    // 单CSS文件减少请求数
    cssCodeSplit: false,
    // 小资源内联为base64，减少请求
    assetsInlineLimit: 8192,
    // 关闭sourcemap减小体积
    sourcemap: false,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
