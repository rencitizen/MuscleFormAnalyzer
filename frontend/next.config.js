/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // 実験的機能
  experimental: {
    // appDir is now stable in Next.js 14
  },
  
  // 画像最適化
  images: {
    domains: ['firebasestorage.googleapis.com', 'lh3.googleusercontent.com'],
    formats: ['image/webp', 'image/avif']
  },
  
  // 環境変数
  env: {
    NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  
  // API リライト（本番環境ではRailwayのURLに変更）
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://muscleformanalyzer-production.up.railway.app/:path*'
          : 'http://localhost:5000/:path*'
      }
    ]
  },
  
  // ヘッダー設定
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
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
  
  // MediaPipeの静的ファイルを適切に扱うための設定
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false
      };
    }
    
    // パスエイリアスの設定
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname,
    };
    
    return config;
  },
  
  // TypeScript設定
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // ESLint設定
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // コンパイラ最適化
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // PWA設定（将来的に追加予定）
  // pwa: {
  //   dest: 'public',
  //   register: true,
  //   skipWaiting: true,
  // }
}

module.exports = nextConfig