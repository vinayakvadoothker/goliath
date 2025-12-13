/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
    NEXT_PUBLIC_DECISION_URL: process.env.NEXT_PUBLIC_DECISION_URL || 'http://localhost:8002',
    NEXT_PUBLIC_LEARNER_URL: process.env.NEXT_PUBLIC_LEARNER_URL || 'http://localhost:8003',
    NEXT_PUBLIC_GRAPH_URL: process.env.NEXT_PUBLIC_GRAPH_URL || 'http://localhost:8002',
  },
}

module.exports = nextConfig

