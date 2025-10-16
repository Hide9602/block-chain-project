# ベースイメージ
FROM node:18-alpine

# 作業ディレクトリ設定
WORKDIR /app

# パッケージファイルのコピー
COPY package*.json ./

# 依存パッケージのインストール
RUN npm ci --only=production=false

# アプリケーションコードのコピー
COPY . .

# Next.js ビルド（本番環境用）
# 開発環境ではコメントアウト
# RUN npm run build

# 実行ユーザーの作成（セキュリティのため）
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# ユーザー切替
USER nextjs

# ポート公開
EXPOSE 3000

# デフォルトコマンド（開発環境）
CMD ["npm", "run", "dev"]

# 本番環境用コマンド
# CMD ["npm", "start"]
