import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import type { PluginOption } from "vite";

export default defineConfig({
  plugins: [react()] as PluginOption[],
  build: {
    outDir: "dist",
    sourcemap: false,
    minify: "esbuild",
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_URL || "http://localhost:5001",
        changeOrigin: true,
      },
    },
  },
});