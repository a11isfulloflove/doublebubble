import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/whisper/transcribe': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/whisper\/transcribe/, '/transcribe'),
      },
      '/whisper/getallvideos': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/whisper\/getallvideos/, '/getallvideos'),
      },
      '/whisper/getbyslugtitle': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/whisper\/getbyslugtitle/, '/getbyslugtitle'),
      },
      '/whisper/deletevideo': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/whisper\/deletevideo/, '/deletevideo'),
      },
    },
  },
})
