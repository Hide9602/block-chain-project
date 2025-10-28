/** @type {import('next').NextConfig} */
const { i18n } = require('./next-i18next.config');

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  i18n,
  
  // 環境変数
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_APP_NAME: 'MetaSleuth NextGen',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },

  // 画像最適化
  images: {
    domains: ['localhost', 'metasleuth-nextgen.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // ヘッダー設定
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // リダイレクト設定
  async redirects() {
    return [];
  },

  // Webpack設定
  webpack: (config, { isServer }) => {
    // グラフライブラリの最適化
    config.externals = config.externals || [];
    if (!isServer) {
      config.externals.push({
        bufferutil: 'bufferutil',
        'utf-8-validate': 'utf-8-validate',
      });
    }

    return config;
  },

  // バンドル分析（ANALYZE=true next build）
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config) => {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: './analyze.html',
        })
      );
      return config;
    },
  }),
};

module.exports = nextConfig;
