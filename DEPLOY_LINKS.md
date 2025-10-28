# 🚀 MetaSleuth NextGen - デプロイリンク集

**すぐにデプロイ！これらのリンクをクリックするだけ！**

---

## 📍 ステップ1: バックエンドをRailwayにデプロイ（2分）

### 🔗 Railway デプロイリンク

**クリックしてデプロイ**: 

👉 https://railway.app/new/template?template=https://github.com/Hide9602/block-chain-project

または手動で：

1. 👉 https://railway.app/new
2. **"Deploy from GitHub repo"** を選択
3. **"Hide9602/block-chain-project"** を検索
4. **"Deploy Now"** をクリック

### ⚙️ 必要な設定

デプロイ後、以下の環境変数を追加：

```env
SECRET_KEY=<下記コマンドで生成>
ENVIRONMENT=production
CORS_ORIGINS=*
```

**SECRET_KEY生成**:
```bash
openssl rand -hex 32
```

または、この値を使用:
```
4a8f7e2b9c1d6e3f5a8b7c2d4e6f8a9b1c3d5e7f9a2b4c6d8e1f3a5b7c9d2e4f6
```

### 📦 データベース追加

1. **PostgreSQL**: New → Database → Add PostgreSQL
2. **Redis**: New → Database → Add Redis

### 🌐 URLを取得

Settings → Generate Domain → URLをコピー

例: `https://block-chain-project-production.up.railway.app`

---

## 📍 ステップ2: フロントエンドをVercelにデプロイ（3分）

### 🔗 Vercel デプロイリンク

**クリックしてデプロイ**:

👉 https://vercel.com/new/clone?repository-url=https://github.com/Hide9602/block-chain-project&project-name=metasleuth-nextgen&root-directory=frontend&env=NEXT_PUBLIC_API_URL

または手動で：

1. 👉 https://vercel.com/new
2. **"Import Git Repository"** を選択
3. **"Hide9602/block-chain-project"** を検索
4. **"Import"** をクリック

### ⚙️ プロジェクト設定

| 設定 | 値 |
|-----|---|
| **Framework** | Next.js |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |

### 🔑 環境変数

```env
NEXT_PUBLIC_API_URL=<RailwayのURL>
```

ステップ1で取得したRailway URLを入力

### 🌐 URLを取得

デプロイ完了後、Vercel URLをコピー

例: `https://metasleuth-nextgen.vercel.app`

---

## 📍 ステップ3: CORS設定を更新（30秒）

### Railway に戻る

1. Railway ダッシュボードを開く
2. バックエンドサービスをクリック
3. **Variables** タブを開く
4. `CORS_ORIGINS` を更新:

```env
CORS_ORIGINS=<VercelのURL>
```

例:
```env
CORS_ORIGINS=https://metasleuth-nextgen.vercel.app
```

5. 保存（自動再デプロイ）

---

## ✅ デプロイ完了！

### 🌐 アクセス先

**フロントエンド（ユーザー向け）**:
```
https://metasleuth-nextgen.vercel.app
```

**バックエンドAPI（開発者向け）**:
```
https://block-chain-project-production.up.railway.app
```

**API ドキュメント**:
```
https://block-chain-project-production.up.railway.app/docs
```

---

## 🧪 動作テスト

### 基本テスト

1. フロントエンドURLにアクセス
2. 言語切り替えボタン（🌐）をクリック
3. サンプルアドレスを検索: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
4. すべてのタブ（Graph, Patterns, Risk, AI Report）を確認

すべて動作すれば、**成功です！** 🎉

---

## 🐛 トラブルシューティング

### エラー: "Failed to fetch"

**解決策**:
1. Vercelの環境変数 `NEXT_PUBLIC_API_URL` を確認
2. Railway URLが正しいか確認
3. Railwayサービスが起動しているか確認

### エラー: "CORS policy"

**解決策**:
1. Railwayの `CORS_ORIGINS` を確認
2. Vercel URLが正しく設定されているか確認
3. 末尾のスラッシュ（/）がないことを確認

### エラー: "Application error"

**解決策**:
1. Railwayのログを確認
2. 環境変数 `SECRET_KEY` が設定されているか確認
3. PostgreSQLとRedisが追加されているか確認

---

## 📞 サポート

- 📖 **完全ガイド**: `DEPLOY_STEP_BY_STEP.md`
- 🐛 **GitHub Issues**: https://github.com/Hide9602/block-chain-project/issues
- 💬 **Railway Discord**: https://discord.gg/railway
- 💬 **Vercel Support**: https://vercel.com/support

---

## 🎉 おめでとうございます！

**MetaSleuth NextGen が世界中からアクセス可能になりました！** 🌍🚀

---

*作成日: 2025-10-28*
