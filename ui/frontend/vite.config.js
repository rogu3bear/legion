import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dotenv from 'dotenv'
import path from 'path'
import { fileURLToPath, URL } from 'node:url'

// Load environment variables from .env.ports located at the project root
const __dirname = path.dirname(fileURLToPath(import.meta.url))
const envConfig = dotenv.config({ path: path.resolve(__dirname, '../../.env.ports') })

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(envConfig.parsed?.PORT_ALLOCATOR_UI_FRONTEND) || 5173,
  },
})
