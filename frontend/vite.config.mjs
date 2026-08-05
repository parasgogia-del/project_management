import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeuiPlugin from 'frappe-ui/vite'

export default defineConfig(({ mode }) => ({
  plugins: [vue(), frappeuiPlugin({ buildConfig: false })],
  base: mode === 'production' ? '/assets/project_management/frontend/' : '/',
  server: {
    port: 8080,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: `../${path.basename(path.resolve('..'))}/public/frontend`,
    emptyOutDir: true,
    target: 'es2015',
    manifest: true,
  },
  optimizeDeps: {
    exclude: ['frappe-ui'],
    include: [
      'socket.io-client',
      'socket.io-parser',
      'engine.io-client',
      'debug',
      'frappe-ui > feather-icons',
      'highlight.js/lib/core',
      'interactjs',
    ],
  },
}))
