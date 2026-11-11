import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Dev: proxy /api to Flask so the session cookie stays same-origin.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': 'http://localhost:5001' } },
})
