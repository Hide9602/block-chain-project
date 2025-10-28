# 🚀 MetaSleuth NextGen - ステップバイステップデプロイガイド

このガイドに従って、**今すぐ**本番環境にデプロイできます！

---

## ✅ 準備完了状態

すべての設定ファイルがGitHubにプッシュされました：

- ✅ Railway設定（railway.json, railway.toml, nixpacks.toml, Procfile）
- ✅ Vercel設定（vercel.json）
- ✅ Docker設定（docker-compose.yml, Dockerfiles）
- ✅ 環境変数テンプレート（.env.example）
- ✅ 自動デプロイスクリプト（deploy.sh）
- ✅ 完全ドキュメント（DEPLOYMENT.md, DEPLOY_NOW.md）

**GitHubリポジトリ**: https://github.com/Hide9602/block-chain-project  
**ブランチ**: main

---

## 🎯 方法1: ワンクリックデプロイ（最速）

### ステップ1: Railway ボタンでデプロイ

**Railway Deploy Button**: 

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/metasleuth?referralCode=genspark)

または手動で：

1. **Railway にアクセス**: https://railway.app/new
2. **"Deploy from GitHub repo"** をクリック
3. **リポジトリを選択**: `Hide9602/block-chain-project`
4. **自動的にデプロイ開始**

### ステップ2: Vercel ボタンでデプロイ

**Vercel Deploy Button**:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FHide9602%2Fblock-chain-project&project-name=metasleuth-nextgen&repository-name=metasleuth-nextgen&root-directory=frontend&env=NEXT_PUBLIC_API_URL)

または手動で：

1. **Vercel にアクセス**: https://vercel.com/new
2. **"Import Git Repository"** をクリック
3. **リポジトリを選択**: `Hide9602/block-chain-project`
4. **Root Directory**: `frontend` を選択
5. **Deploy** をクリック

---

## 🎯 方法2: 手動デプロイ（推奨、完全コントロール）

### Part A: バックエンドをRailwayにデプロイ（5分）

#### ステップ1: Railway アカウント作成

1. https://railway.app にアクセス
2. **「Login With GitHub」** をクリック
3. GitHubアカウントで認証

#### ステップ2: 新しいプロジェクトを作成

1. ダッシュボードで **「New Project」** をクリック
2. **「Deploy from GitHub repo」** を選択
3. **「Hide9602/block-chain-project」** を検索して選択
4. **「Deploy Now」** をクリック

Railway が自動的に：
- リポジトリをクローン
- `railway.toml` を検出
- Python環境をセットアップ
- 依存関係をインストール
- アプリをビルド＆デプロイ

#### ステップ3: PostgreSQL データベースを追加

1. プロジェクトダッシュボードで **「New」** をクリック
2. **「Database」** → **「Add PostgreSQL」** を選択
3. 自動的にプロビジョニングされ、`DATABASE_URL` が設定される

#### ステップ4: Redis を追加

1. 再度 **「New」** をクリック
2. **「Database」** → **「Add Redis」** を選択
3. 自動的にプロビジョニングされ、`REDIS_URL` が設定される

#### ステップ5: 環境変数を設定

1. バックエンドサービスをクリック
2. **「Variables」** タブをクリック
3. 以下の変数を追加：

```env
SECRET_KEY=<ランダムな64文字の文字列>
ENVIRONMENT=production
CORS_ORIGINS=*
```

**SECRET_KEYの生成方法**:
```bash
# ターミナルで実行
openssl rand -hex 32
```

または、https://generate-secret.vercel.app/ を使用

#### ステップ6: デプロイURLを取得

1. **「Settings」** タブをクリック
2. **「Generate Domain」** をクリック
3. URLが生成される（例: `https://block-chain-project-production.up.railway.app`）
4. **このURLをコピー**（後で使用）

✅ **バックエンドデプロイ完了！**

---

### Part B: フロントエンドをVercelにデプロイ（5分）

#### ステップ1: Vercel アカウント作成

1. https://vercel.com/signup にアクセス
2. **「Continue with GitHub」** をクリック
3. GitHubアカウントで認証

#### ステップ2: 新しいプロジェクトをインポート

1. ダッシュボードで **「Add New...」** → **「Project」** をクリック
2. **「Import Git Repository」** セクションで `Hide9602/block-chain-project` を探す
3. **「Import」** をクリック

#### ステップ3: プロジェクト設定

**Configure Project** 画面で以下を設定：

| 設定項目 | 値 |
|---------|-----|
| **Project Name** | `metasleuth-nextgen` |
| **Framework Preset** | Next.js |
| **Root Directory** | `frontend` ← **重要！** |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Install Command** | `npm install` |

#### ステップ4: 環境変数を設定

**Environment Variables** セクションで追加：

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `<RailwayのURL>` |

（Part A ステップ6でコピーしたRailway URLを貼り付け）

#### ステップ5: デプロイ

1. **「Deploy」** ボタンをクリック
2. ビルドプロセスが開始（約2-3分）
3. デプロイ完了を待つ

#### ステップ6: URLを取得

デプロイ完了後：
1. URLが表示される（例: `https://metasleuth-nextgen.vercel.app`）
2. **このURLをコピー**（次のステップで使用）

✅ **フロントエンドデプロイ完了！**

---

### Part C: CORS設定を更新（1分）

#### ステップ1: Railway に戻る

1. Railway ダッシュボードに戻る
2. バックエンドサービスをクリック
3. **「Variables」** タブを開く

#### ステップ2: CORS_ORIGINS を更新

**変更前**:
```
CORS_ORIGINS=*
```

**変更後**:
```
CORS_ORIGINS=https://metasleuth-nextgen.vercel.app
```
（Part B ステップ6でコピーしたVercel URLを使用）

#### ステップ3: 保存

- 変更を保存すると自動的に再デプロイされる（約30秒）

✅ **CORS設定完了！**

---

## 🎉 デプロイ完了！テストしましょう

### アクセス先

#### 🌐 フロントエンド（ユーザー向け）
```
https://metasleuth-nextgen.vercel.app
```

#### 🔧 バックエンドAPI（開発者向け）
```
https://block-chain-project-production.up.railway.app
```

#### 📚 API ドキュメント
```
https://block-chain-project-production.up.railway.app/docs
```

---

## ✅ 動作確認チェックリスト

### 基本動作テスト

1. **フロントエンドアクセス**
   - [ ] ホームページが表示される
   - [ ] ロゴとナビゲーションが表示される
   - [ ] 検索バーが表示される

2. **言語切り替え**
   - [ ] 右上の地球儀アイコンをクリック
   - [ ] 「English」と「日本語」が切り替わる
   - [ ] すべてのテキストが翻訳される

3. **アドレス検索**
   - [ ] サンプルアドレスを入力: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
   - [ ] 「調査」（または「Investigate」）ボタンをクリック
   - [ ] 調査ページに遷移する

### 調査ページテスト

4. **グラフ表示**
   - [ ] トランザクショングラフタブが表示される
   - [ ] ノード（円）とエッジ（線）が表示される
   - [ ] レイアウトボタン（ツリー、円形、リスク）が動作する
   - [ ] ノードをクリックすると詳細が表示される

5. **パターン検出**
   - [ ] パターン検出タブをクリック
   - [ ] 検出されたパターンが表示される
   - [ ] 日本語表示（ウォッシュトレーディング等）を確認

6. **リスク評価**
   - [ ] リスク評価タブをクリック
   - [ ] リスクスコア（0-100）が表示される
   - [ ] リスクレベル（高/中/低）が表示される
   - [ ] 寄与要因が表示される

7. **AIレポート**
   - [ ] AIレポートタブをクリック
   - [ ] 日本語または英語でレポートが表示される
   - [ ] 調査概要が読める

すべてチェックが付けば、**完全に動作しています！** 🎉

---

## 🐛 トラブルシューティング

### 問題1: フロントエンドは表示されるが、検索が動作しない

**症状**: "Failed to fetch" エラー

**原因**: バックエンドに接続できていない

**解決策**:
1. Vercelの環境変数を確認
   - `NEXT_PUBLIC_API_URL` が正しく設定されているか
2. RailwayのURLが正しいか確認
3. Railwayのサービスが起動しているか確認

### 問題2: "CORS error" が表示される

**症状**: コンソールに CORS エラー

**原因**: CORS設定の問題

**解決策**:
1. Railwayの環境変数を確認:
   ```
   CORS_ORIGINS=https://metasleuth-nextgen.vercel.app
   ```
2. 末尾のスラッシュ（/）がないことを確認
3. 環境変数を保存して再デプロイ

### 問題3: バックエンドが起動しない

**症状**: Railway でビルドエラー

**原因**: 環境変数が不足

**解決策**:
Railwayで以下を確認：
- [ ] `SECRET_KEY` が設定されている
- [ ] PostgreSQL が追加されている
- [ ] Redis が追加されている
- [ ] `DATABASE_URL` が自動設定されている
- [ ] `REDIS_URL` が自動設定されている

### 問題4: Vercel ビルドエラー

**症状**: "Module not found" エラー

**解決策**:
1. Root Directory が `frontend` に設定されているか確認
2. Vercel ダッシュボード → Settings → General
3. Root Directory を `frontend` に変更
4. Redeploy

---

## 📊 次のステップ

### 1. カスタムドメインを設定（オプション）

#### Vercel でカスタムドメイン:
1. Vercel ダッシュボード → Settings → Domains
2. カスタムドメインを入力（例: `metasleuth.com`）
3. DNSレコードを設定（Vercelが指示）
4. SSL証明書が自動発行される

#### Railway でカスタムドメイン:
1. Railway ダッシュボード → Settings → Domains
2. カスタムドメインを入力（例: `api.metasleuth.com`）
3. CNAMEレコードを設定
4. SSL証明書が自動発行される

### 2. 監視とアラートを設定

#### Vercel Analytics:
- 自動的に有効（無料）
- ページビュー、パフォーマンスを追跡

#### Railway Monitoring:
- CPU、メモリ、ネットワーク使用量を確認
- アラート設定可能

#### エラートラッキング（推奨）:
- **Sentry**: https://sentry.io
- フロントエンドとバックエンドのエラーを追跡

### 3. パフォーマンス最適化

- [ ] 画像最適化（Next.js Image コンポーネント）
- [ ] CDN活用（Vercelの自動CDN）
- [ ] キャッシング設定（Redis）
- [ ] データベースインデックス

---

## 💰 コスト見積もり

### 無料枠（個人、開発環境）

**Vercel**:
- 100GB 帯域幅/月
- 無制限デプロイ
- 100 ビルド時間/月

**Railway**:
- $5 クレジット/月
- 500時間実行時間
- PostgreSQL + Redis 込み

**合計**: **完全無料で開始可能**

### 本番環境（月間1000ユーザー）

**Vercel Pro**: $20/月
**Railway**: $10-20/月

**合計**: 約 **$30-40/月**

### エンタープライズ（月間10000ユーザー）

**Vercel Enterprise**: $150/月〜
**Railway**: $100/月〜

**合計**: 約 **$250/月〜**

---

## 📞 サポート

### ドキュメント
- **完全デプロイガイド**: `DEPLOYMENT.md`
- **クイックガイド**: `DEPLOY_NOW.md`
- **プロジェクトREADME**: `README.md`

### コミュニティ
- **GitHub Issues**: https://github.com/Hide9602/block-chain-project/issues
- **Railway Discord**: https://discord.gg/railway
- **Vercel Support**: https://vercel.com/support

---

## 🎊 おめでとうございます！

**MetaSleuth NextGen が本番環境で稼働しています！**

✅ フロントエンド: Vercel でホスティング  
✅ バックエンド: Railway でホスティング  
✅ データベース: PostgreSQL（Railway）  
✅ キャッシュ: Redis（Railway）  
✅ 完全多言語対応（日英）  
✅ HTTPS 対応  
✅ 自動デプロイ設定済み  

**世界中からアクセス可能です！** 🌍🚀

---

*作成日: 2025-10-28*  
*最終更新: 2025-10-28*
