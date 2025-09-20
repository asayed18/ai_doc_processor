/** @type {import('next').NextConfig} */
const nextConfig = {
  // Reduce development warnings
  reactStrictMode: false, // Temporarily disable for debugging
  swcMinify: true,
  
  // Better error handling
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
  
  // Disable telemetry
  telemetry: false,
  
  // Development proxy for API calls (bypasses CORS)
  async rewrites() {
    return process.env.NODE_ENV === 'development' ? [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ] : []
  },
  
  // Development headers for CORS
  async headers() {
    return process.env.NODE_ENV === 'development' ? [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ] : []
  },
}

module.exports = nextConfig