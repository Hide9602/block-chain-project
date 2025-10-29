/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  
  // 環境変数
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_APP_NAME: 'MetaSleuth NextGen',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },



  // ヘッダーとリダイレクトは静的エクスポートでは使用不可
  // Netlifyの _headers ファイルで設定可能

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
