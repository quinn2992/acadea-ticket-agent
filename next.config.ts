import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Pin the tracing root so Next.js doesn't walk up to a stray parent lockfile.
  outputFileTracingRoot: path.resolve(__dirname),
};

export default nextConfig;
