import type { NextConfig } from "next";
import path from "node:path";
import { BASE_PATH } from "./lib/config";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Serve the app under /ticketagent. The value lives in lib/config.ts so
  // the client fetch() can import the same constant.
  basePath: BASE_PATH,
  // Pin the tracing root so Next.js doesn't walk up to a stray parent lockfile.
  outputFileTracingRoot: path.resolve(__dirname),
};

export default nextConfig;
