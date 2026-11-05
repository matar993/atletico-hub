import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import react from '@vitejs/plugin-react'
import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'

// The image's security headers, read from its nginx snippet: the preview build that browser tests run on gets the
// same Content-Security-Policy as the image.
const imageHeaders = Object.fromEntries(
  [
    ...readFileSync(new URL('./nginx/security-headers.conf', import.meta.url), 'utf8').matchAll(
      /^add_header (\S+) "([^"]*)" always;$/gm,
    ),
  ].map(([, name, value]) => [name, value]),
)

export default defineConfig({
  plugins: [tanstackRouter({ target: 'react', autoCodeSplitting: true }), react(), tailwindcss()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: {
    host: true,
    port: 3200,
    // Some Docker hosts do not pass file events into bind mounts: VITE_POLLING=1 makes the server poll instead.
    watch: process.env.VITE_POLLING === '1' ? { usePolling: true, interval: 300 } : undefined,
    proxy: {
      '/api': {
        target: process.env.API_PROXY_TARGET ?? 'http://localhost:8200',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  preview: { headers: imageHeaders },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
    setupFiles: ['./src/test/setup.ts'],
    restoreMocks: true,
  },
})
