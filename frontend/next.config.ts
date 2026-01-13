// frontend/next.config.ts
import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  serverExternalPackages: ["@copilotkit/runtime"],

  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;

