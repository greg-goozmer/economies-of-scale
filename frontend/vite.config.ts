import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, strictPort: true, host: '127.0.0.1',
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/s3': { target: 'http://127.0.0.1:9000', changeOrigin: true, rewrite: path => path.replace(/^\/s3/, '') },
    },
  },
  preview: { port: 3000, strictPort: true },
  test: { environment: 'jsdom', setupFiles: './src/tests/setup.ts', css: false, include: ['src/tests/**/*.test.{ts,tsx}'] },
});
