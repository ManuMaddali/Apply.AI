/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    // Feature flags
    ENABLE_TESTING_SUITE: process.env.ENABLE_TESTING_SUITE || 'false',
  },
}

module.exports = nextConfig 