import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/Real-World-Simulator-OS/",
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        ws: true
      }
    }
  }
});
