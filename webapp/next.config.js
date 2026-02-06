/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Silence Turbopack warnings about lockfiles
  experimental: {
    turbo: {
      root: process.cwd(),
    },
  },
};

module.exports = nextConfig;
