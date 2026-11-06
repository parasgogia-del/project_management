import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";
import frappeuiPlugin from "frappe-ui/vite";

export default defineConfig({
  plugins: [vue(), frappeuiPlugin({ buildConfig: false })],
  base: "/assets/project_management/frontend/",
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  build: {
    outDir: "../project_management/public/frontend",
    emptyOutDir: true,
    target: "es2015",
    manifest: true,
  },
  optimizeDeps: {
    exclude: ["frappe-ui"],
    include: [
      "socket.io-client",
      "socket.io-parser",
      "engine.io-client",
      "debug",
      "frappe-ui > feather-icons",
      "highlight.js/lib/core",
      "interactjs",
    ],
  },
});
