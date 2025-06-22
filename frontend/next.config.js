/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // 静的サイト生成設定（v3.0）
  output: process.env.STATIC_EXPORT === 'true' ? 'export' : undefined,
  
  // ESMモジュールの外部化設定
  experimental: {
    esmExternals: 'loose',
    // 最適化されたランタイム
    optimizeCss: true,
  },
  
  // バンドルサイズ最適化設定
  modularizeImports: {
    // Lodashの最適化
    'lodash': {
      transform: 'lodash/{{member}}',
    },
    // Material UIの最適化（使用している場合）
    '@mui/material': {
      transform: '@mui/material/{{member}}',
    },
    '@mui/icons-material': {
      transform: '@mui/icons-material/{{member}}',
    },
  },
  
  // 画像最適化
  images: {
    domains: ['firebasestorage.googleapis.com', 'lh3.googleusercontent.com'],
    formats: ['image/webp', 'image/avif'],
    // 静的エクスポート時は画像最適化を無効化
    unoptimized: process.env.STATIC_EXPORT === 'true',
  },
  
  // トレイリングスラッシュ（静的ホスティング用）
  trailingSlash: process.env.STATIC_EXPORT === 'true',
  
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
  webpack: (config, { isServer, webpack, dev }) => {
    // バンドルサイズ最適化
    if (!dev && !isServer) {
      // Tree shakingの強化
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: false,
        // モジュール連結の最適化
        concatenateModules: true,
        // ランタイムチャンクの最適化
        runtimeChunk: 'single',
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // React関連
            react: {
              name: 'react',
              chunks: 'all',
              test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              priority: 40,
              enforce: true,
            },
            // MediaPipe（動的インポート用）
            mediapipe: {
              name: 'mediapipe',
              chunks: 'async',
              test: /[\\/]node_modules[\\/]@mediapipe[\\/]/,
              priority: 30,
              enforce: true,
            },
            // グラフライブラリ
            charts: {
              name: 'charts',
              chunks: 'async',
              test: /[\\/]node_modules[\\/](chart\.js|recharts|d3)[\\/]/,
              priority: 20,
              enforce: true,
            },
            // 共通ライブラリ
            commons: {
              name: 'commons',
              chunks: 'initial',
              minChunks: 2,
              priority: 10,
              reuseExistingChunk: true,
            },
            // その他のvendor
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /[\\/]node_modules[\\/]/,
              priority: 0,
            },
          },
          // 最小サイズの設定
          minSize: 20000,
          maxAsyncRequests: 30,
          maxInitialRequests: 25,
        },
      };
      
      // Webpack Bundle Analyzerの設定（開発時のみ）
      if (process.env.ANALYZE === 'true') {
        const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
        config.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'static',
            reportFilename: './analyze/client.html',
            openAnalyzer: false,
          })
        );
      }
    }
    
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
      
      // 不要なモジュールの除外
      config.externals = {
        ...config.externals,
        'canvas': 'canvas',
        'jsdom': 'jsdom',
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
    if (!isServer) {
      // externalsが配列でない場合の処理
      if (Array.isArray(config.externals)) {
        config.externals.push('ajv');
      } else if (typeof config.externals === 'function') {
        const originalExternals = config.externals;
        config.externals = (context, request, callback) => {
          if (request === 'ajv') {
            return callback(null, 'commonjs ' + request);
          }
          return originalExternals(context, request, callback);
        };
      } else {
        config.externals = ['ajv'];
      }
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
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
    // React DevToolsの削除（本番環境）
    reactRemoveProperties: process.env.NODE_ENV === 'production',
    // 未使用のCSSの削除
    styledComponents: true,
  },
  
  // swcMinify設定
  swcMinify: true,
  
  // 圧縮設定
  compress: true,
  
  // Productionソースマップの無効化（バンドルサイズ削減）
  productionBrowserSourceMaps: false,
}

module.exports = nextConfig