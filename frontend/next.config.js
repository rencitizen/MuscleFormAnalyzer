/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // ESMモジュールの外部化設定
  experimental: {
    esmExternals: 'loose',
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
          ? 'https://tenaxfit-production.up.railway.app/:path*'
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
  
  // Firebaseとundiciのトランスパイル設定
  transpilePackages: [
    '@firebase/auth',
    'firebase',
    'undici'
  ],
  
  // webpack設定
  webpack: (config, { isServer, webpack }) => {
    // クライアントサイドでのポリフィル設定
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        crypto: false,
        stream: false,
        buffer: false,
      };
    }
    
    // パスエイリアスの設定
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname,
    };
    
    // undiciのprivateフィールド構文を処理するための設定
    config.module.rules.push({
      test: /\.js$/,
      include: /node_modules\/(undici|@firebase)/,
      use: {
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env'],
          plugins: [
            '@babel/plugin-proposal-private-methods',
            '@babel/plugin-proposal-class-properties',
            '@babel/plugin-proposal-private-property-in-object'
          ]
        }
      }
    });
    
    // Node.js組み込みモジュールのポリフィル
    config.plugins.push(
      new webpack.NormalModuleReplacementPlugin(
        /^node:/,
        (resource) => {
          resource.request = resource.request.replace(/^node:/, '');
        }
      )
    );
    
    // ajvモジュールの外部化
    config.externals = config.externals || [];
    if (!isServer) {
      config.externals.push('ajv');
    }
    
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
  
  // swcMinify設定
  swcMinify: true,
}

module.exports = nextConfig