/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Environment variables available to the client
  env: {
    // Feature flags
    ENABLE_TESTING_SUITE: process.env.ENABLE_TESTING_SUITE || 'false',
    
    // API Configuration
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    
    // Environment detection
    NEXT_PUBLIC_ENVIRONMENT: process.env.NODE_ENV || 'development',
  },

  // API rewrites for proxying requests to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
  
  // Security headers for production
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'geolocation=(), microphone=(), camera=()',
          },
        ],
      },
    ]
  },

  // Optimize for production
  poweredByHeader: false,
  generateEtags: false,
  
  // Compression and performance
  compress: true,
  
  // Output configuration for deployment
  output: 'standalone',
  
  // Disable source maps in production for security
  productionBrowserSourceMaps: false,
}

module.exports = nextConfig 