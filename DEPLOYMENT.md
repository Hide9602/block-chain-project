# MetaSleuth NextGen - デプロイメントガイド 🚀

このガイドでは、MetaSleuth NextGenを本番環境にデプロイする方法を説明します。

---

## 📋 目次

1. [デプロイオプション](#デプロイオプション)
2. [Vercel + Railway デプロイ（推奨）](#vercel--railway-デプロイ推奨)
3. [Docker デプロイ](#docker-デプロイ)
4. [AWS デプロイ](#aws-デプロイ)
5. [環境変数設定](#環境変数設定)
6. [デプロイ後の確認](#デプロイ後の確認)

---

## デプロイオプション

### オプション1: Vercel + Railway（推奨）⭐
- **フロントエンド**: Vercel（無料枠あり）
- **バックエンド**: Railway（無料枠あり）
- **難易度**: ⭐☆☆☆☆（最も簡単）
- **コスト**: 無料〜$20/月

### オプション2: Docker Compose
- **すべてのサービス**: 1台のサーバーで動作
- **難易度**: ⭐⭐⭐☆☆
- **コスト**: VPS代のみ（$5〜20/月）

### オプション3: Kubernetes
- **本格的な本番環境**: スケーラブル
- **難易度**: ⭐⭐⭐⭐⭐
- **コスト**: $50〜/月

---

## Vercel + Railway デプロイ（推奨）

### 前提条件
- GitHubアカウント
- Vercelアカウント（無料）
- Railwayアカウント（無料）

### ステップ1: バックエンドをRailwayにデプロイ

1. **Railway にログイン**
   - https://railway.app にアクセス
   - GitHubでサインアップ/ログイン

2. **新しいプロジェクトを作成**
   ```
   1. "New Project" をクリック
   2. "Deploy from GitHub repo" を選択
   3. "Hide9602/block-chain-project" を選択
   4. "backend" ディレクトリを選択
   ```

3. **環境変数を設定**
   ```
   SECRET_KEY=<ランダムな文字列>
   DATABASE_URL=<自動生成>
   REDIS_URL=<自動生成>
   ENVIRONMENT=production
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

4. **PostgreSQLとRedisを追加**
   ```
   1. "New" > "Database" > "Add PostgreSQL"
   2. "New" > "Database" > "Add Redis"
   3. 自動的に DATABASE_URL と REDIS_URL が設定される
   ```

5. **デプロイ**
   - 自動的にビルド・デプロイが開始
   - デプロイ完了後、URLをコピー（例: `https://metasleuth-api.up.railway.app`）

### ステップ2: フロントエンドをVercelにデプロイ

1. **Vercel にログイン**
   - https://vercel.com にアクセス
   - GitHubでサインアップ/ログイン

2. **新しいプロジェクトをインポート**
   ```
   1. "Add New..." > "Project" をクリック
   2. "Hide9602/block-chain-project" を選択
   3. "Import" をクリック
   ```

3. **プロジェクト設定**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **環境変数を設定**
   ```
   NEXT_PUBLIC_API_URL=https://metasleuth-api.up.railway.app
   ```

5. **デプロイ**
   - "Deploy" をクリック
   - 約2-3分でデプロイ完了
   - URLが発行される（例: `https://metasleuth-nextgen.vercel.app`）

### ステップ3: CORS設定を更新

1. Railwayのバックエンドに戻る
2. 環境変数 `CORS_ORIGINS` を更新:
   ```
   CORS_ORIGINS=https://metasleuth-nextgen.vercel.app
   ```
3. 再デプロイ

### ✅ 完了！

アクセス: https://metasleuth-nextgen.vercel.app

---

## Docker デプロイ

### 前提条件
- Docker 20.x以上
- Docker Compose 2.x以上
- サーバー（VPS、AWS EC2等）

### ステップ1: サーバーにログイン

```bash
ssh user@your-server-ip
```

### ステップ2: リポジトリをクローン

```bash
git clone https://github.com/Hide9602/block-chain-project.git
cd block-chain-project
```

### ステップ3: 環境変数ファイルを作成

```bash
# フロントエンド
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://your-server-ip:8000
EOF

# バックエンド
cat > backend/.env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://postgres:postgres@db:5432/metasleuth
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=production
CORS_ORIGINS=http://your-server-ip:3000
EOF
```

### ステップ4: Docker Composeで起動

```bash
# ビルドと起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# 状態確認
docker-compose ps
```

### ステップ5: データベース初期化

```bash
# バックエンドコンテナに入る
docker-compose exec backend bash

# マイグレーション実行
alembic upgrade head

# 初期データ投入（オプション）
python -m app.scripts.seed_data

# コンテナから出る
exit
```

### ✅ 完了！

- フロントエンド: http://your-server-ip:3000
- バックエンドAPI: http://your-server-ip:8000
- API Docs: http://your-server-ip:8000/docs

---

## AWS デプロイ

### オプション1: AWS Amplify（フロントエンド）

1. **AWS Amplify Console にアクセス**
   - https://console.aws.amazon.com/amplify

2. **アプリを接続**
   - "New app" > "Host web app"
   - GitHubリポジトリを選択
   - ブランチ: `main`

3. **ビルド設定**
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - npm install
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: frontend/.next
       files:
         - '**/*'
     cache:
       paths:
         - frontend/node_modules/**/*
   ```

4. **環境変数**
   ```
   NEXT_PUBLIC_API_URL=https://your-api-gateway-url
   ```

### オプション2: AWS ECS（バックエンド）

1. **ECRにイメージをプッシュ**
   ```bash
   # ECRログイン
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   
   # イメージビルド
   docker build -t metasleuth-backend ./backend
   
   # タグ付け
   docker tag metasleuth-backend:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/metasleuth-backend:latest
   
   # プッシュ
   docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/metasleuth-backend:latest
   ```

2. **ECS タスク定義を作成**
   - サービス: Fargate
   - CPU: 0.5 vCPU
   - メモリ: 1GB

3. **RDS（PostgreSQL）とElastiCache（Redis）を設定**

4. **Application Load Balancerを設定**

---

## 環境変数設定

### フロントエンド環境変数

```bash
# frontend/.env.local

# API URL（本番環境のバックエンドURL）
NEXT_PUBLIC_API_URL=https://api.metasleuth-nextgen.com

# アナリティクス（オプション）
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

### バックエンド環境変数

```bash
# backend/.env

# セキュリティ
SECRET_KEY=<64文字以上のランダム文字列>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# データベース
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0

# CORS
CORS_ORIGINS=https://metasleuth-nextgen.com,https://www.metasleuth-nextgen.com

# 環境
ENVIRONMENT=production
DEBUG=false

# ブロックチェーンAPI（オプション）
ETHERSCAN_API_KEY=<your-key>
INFURA_PROJECT_ID=<your-id>
```

---

## デプロイ後の確認

### ヘルスチェック

```bash
# バックエンド
curl https://your-backend-url/health

# フロントエンド
curl -I https://your-frontend-url
```

### 動作確認チェックリスト

- [ ] フロントエンドが正常に表示される
- [ ] 言語切り替えが動作する（日本語⇔英語）
- [ ] APIエンドポイントに接続できる
- [ ] アドレス検索が動作する
- [ ] グラフビジュアライゼーションが表示される
- [ ] レイアウト変更ボタンが動作する
- [ ] パターン検出結果が表示される
- [ ] リスク評価が表示される
- [ ] AIレポートが生成される
- [ ] 日本語でのレポート生成が動作する

### モニタリング

1. **Vercel Analytics**
   - https://vercel.com/analytics
   - ページビュー、パフォーマンス指標

2. **Railway Logs**
   - https://railway.app/project/logs
   - アプリケーションログ、エラー

3. **Sentry（エラートラッキング）**
   ```bash
   npm install @sentry/nextjs
   ```

---

## トラブルシューティング

### ビルドエラー

**問題**: `Module not found` エラー
**解決**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS エラー

**問題**: フロントエンドからAPIにアクセスできない
**解決**: バックエンドの `CORS_ORIGINS` 環境変数を確認

```python
# backend/simple_api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",  # ここを更新
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### データベース接続エラー

**問題**: `could not connect to server`
**解決**: DATABASE_URLを確認

```bash
# 接続テスト
psql $DATABASE_URL
```

---

## セキュリティのベストプラクティス

1. **環境変数を安全に管理**
   - `.env` ファイルをGitにコミットしない
   - シークレットは環境変数で管理

2. **HTTPS を使用**
   - Let's Encrypt で無料SSL証明書取得
   - すべての通信をHTTPS化

3. **定期的なアップデート**
   ```bash
   npm audit
   pip list --outdated
   ```

4. **バックアップ**
   - データベースの定期バックアップ
   - Railway/Vercelの自動バックアップ機能を利用

---

## パフォーマンス最適化

1. **CDN を使用**
   - Vercel/Cloudflareの自動CDN

2. **画像最適化**
   - Next.js Image コンポーネント使用

3. **キャッシング**
   - Redis でAPIレスポンスをキャッシュ

4. **コード分割**
   - Dynamic Import 使用

---

## サポート

問題が発生した場合：

1. **ドキュメント確認**: このガイドを再確認
2. **ログ確認**: Railway/Vercelのログを確認
3. **GitHub Issues**: https://github.com/Hide9602/block-chain-project/issues
4. **メール**: info@metasleuth-nextgen.com

---

**デプロイ成功を祈ります！** 🚀🎉

*最終更新: 2025-10-28*
