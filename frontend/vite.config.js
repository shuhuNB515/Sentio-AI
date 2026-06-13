import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // 相对路径：兼容 shuhu.me（根路径）和 shuhuNB515.github.io/Sentio-AI（子路径）
  base: './',
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
