import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/requirements': 'http://127.0.0.1:8000',
      '/design': 'http://127.0.0.1:8000',
      '/simulation': 'http://127.0.0.1:8000',
      '/export': 'http://127.0.0.1:8000',
      '/codegen': 'http://127.0.0.1:8000'
    }
  }
})