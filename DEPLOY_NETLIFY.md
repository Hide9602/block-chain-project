# 🚀 Netlify でデプロイ（完全無料）

## ワンクリックデプロイ

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Hide9602/block-chain-project)

---

## 手動デプロイ手順

### 1. Netlifyにアクセス
https://app.netlify.com/signup

### 2. GitHubと連携
- 「Deploy with GitHub」を選択
- リポジトリ「Hide9602/block-chain-project」を選択

### 3. ビルド設定
```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/.next
```

### 4. 環境変数（オプション）
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_APP_NAME=MetaSleuth NextGen
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 5. Deploy site をクリック

⏱️ **デプロイ時間**: 約2-3分

---

## ✅ デプロイ完了後

Netlifyが提供するURL（例: `https://metasleuth-nextgen.netlify.app`）にアクセス

---

## 🔧 カスタムドメイン設定

デプロイ後、Netlifyダッシュボードから：
1. Site settings → Domain management
2. Add custom domain
3. DNSレコードを設定

---

## 📝 トラブルシューティング

### ビルドエラーが出る場合
1. Base directoryが `frontend` になっているか確認
2. Build commandが `npm run build` になっているか確認
3. Publish directoryが `frontend/.next` になっているか確認

### 環境変数が必要な場合
Site settings → Environment variables から追加

---

**完全無料・制限なし・超高速デプロイ！** 🚀
