import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

/**
 * Polyfill legacy Three.js color encodings removed in Three.js r152+
 * (LinearEncoding = 3000, sRGBEncoding = 3001) in @designcodeio/threeui bundle.
 * Eliminates [IMPORT_IS_UNDEFINED] build warnings and runtime shader undefined encoding.
 */
function threeEncodingPolyfillPlugin(): Plugin {
  return {
    name: 'three-encoding-polyfill',
    transform(code, id) {
      if (id.includes('@designcodeio/threeui') || id.includes('threeui')) {
        let transformed = code
          .replace(/\b([a-zA-Z0-9_$]+)\.sRGBEncoding\b/g, '3001')
          .replace(/\b([a-zA-Z0-9_$]+)\.LinearEncoding\b/g, '3000')
        if (transformed !== code) {
          return {
            code: transformed,
            map: null,
          }
        }
      }
      return null
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), threeEncodingPolyfillPlugin()],
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('scheduler')) {
              return 'vendor-react';
            }
            if (id.includes('recharts')) {
              return 'vendor-charts';
            }
            if (id.includes('lucide-react')) {
              return 'vendor-icons';
            }
            if (id.includes('three') || id.includes('threeui')) {
              return 'vendor-three';
            }
          }
        },
      },
    },
  },
  server: {
    port: 5173,
    host: '127.0.0.1',
    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
