import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dotenv from 'dotenv'
import path from 'path'

// Load environment variables from .env.ports located at the project root
dotenv.config({ path: path.resolve(__dirname, '../../.env.ports') })

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.PORT_ALLOCATOR_WEB_UI) || 7602,
  },
})
