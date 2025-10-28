# 🚀 今すぐデプロイする手順

このガイドに従って、MetaSleuth NextGenを5分で本番環境にデプロイできます！

---

## ✅ 準備完了

すべてのファイルがGitHubにプッシュされました：
- **Repository**: https://github.com/Hide9602/block-chain-project
- **Branch**: `main`
- **Status**: ✅ Ready for deployment

---

## 🎯 推奨デプロイ方法

**Vercel（フロントエンド）+ Railway（バックエンド）**

### なぜこの組み合わせ？
- ✅ **完全無料** で始められる（クレジットカード不要）
- ✅ **5分でデプロイ完了**
- ✅ **自動HTTPS** 対応
- ✅ **自動スケーリング**
- ✅ **Git連携** - push するだけで自動デプロイ

---

## 📝 ステップ1: バックエンドをRailwayにデプロイ（2分）

### 1.1 Railway にアクセス
👉 https://railway.app

### 1.2 GitHubでサインアップ
- 「Login With GitHub」をクリック
- GitHubアカウントで認証

### 1.3 新しいプロジェクトを作成
1. 「New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. 「Hide9602/block-chain-project」を検索して選択
4. 「Deploy Now」をクリック

### 1.4 PostgreSQLを追加
1. プロジェクトダッシュボードで「New」をクリック
2. 「Database」→「Add PostgreSQL」を選択
3. 自動的にデプロイされます

### 1.5 Redisを追加
1. 再度「New」をクリック
2. 「Database」→「Add Redis」を選択
3. 自動的にデプロイされます

### 1.6 環境変数を設定
1. バックエンドサービスをクリック
2. 「Variables」タブをクリック
3. 以下の変数を追加：

```env
SECRET_KEY=your-secret-key-here-minimum-32-characters-long
ENVIRONMENT=production
CORS_ORIGINS=*
```

### 1.7 デプロイURLを取得
1. 「Settings」タブをクリック
2. 「Generate Domain」をクリック
3. URLをコピー（例：`https://block-chain-project-production.up.railway.app`）

✅ **バックエンド完了！**

---

## 📝 ステップ2: フロントエンドをVercelにデプロイ（3分）

### 2.1 Vercel にアクセス
👉 https://vercel.com/signup

### 2.2 GitHubでサインアップ
- 「Continue with GitHub」をクリック
- GitHubアカウントで認証

### 2.3 新しいプロジェクトをインポート
1. ダッシュボードで「Add New...」→「Project」をクリック
2. 「Import Git Repository」セクションで「Hide9602/block-chain-project」を探す
3. 「Import」をクリック

### 2.4 プロジェクト設定

**Configure Project** 画面で以下を設定：

```
Project Name: metasleuth-nextgen
Framework Preset: Next.js
Root Directory: frontend (※ 重要！)
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### 2.5 環境変数を設定

「Environment Variables」セクションで追加：

```env
Name: NEXT_PUBLIC_API_URL
Value: https://your-railway-url.up.railway.app
```

（ステップ1.7でコピーしたRailway URLを使用）

### 2.6 デプロイ
1. 「Deploy」ボタンをクリック
2. 約2-3分待つ
3. デプロイ完了！

### 2.7 URLを取得
- デプロイ完了後、URLが表示されます
- 例：`https://metasleuth-nextgen.vercel.app`

✅ **フロントエンド完了！**

---

## 📝 ステップ3: CORS設定を更新（30秒）

### 3.1 Railwayに戻る
1. Railway ダッシュボードに戻る
2. バックエンドサービスをクリック
3. 「Variables」タブを開く

### 3.2 CORS_ORIGINSを更新
```env
CORS_ORIGINS=https://metasleuth-nextgen.vercel.app
```
（ステップ2.7でコピーしたVercel URLを使用）

### 3.3 再デプロイ
- 環境変数を保存すると自動的に再デプロイされます
- 約1分待つ

✅ **設定完了！**

---

## 🎉 デプロイ完了！

### アクセス先

#### フロントエンド（ユーザー向け）
```
https://metasleuth-nextgen.vercel.app
```

#### バックエンドAPI（開発者向け）
```
https://your-railway-url.up.railway.app
```

#### API ドキュメント
```
https://your-railway-url.up.railway.app/docs
```

---

## ✅ 動作確認チェックリスト

### フロントエンド
- [ ] ホームページが表示される
- [ ] 言語切り替えボタンが動作する（地球儀アイコン）
- [ ] 日本語と英語が切り替わる
- [ ] アドレス入力欄がある
- [ ] 「調査」ボタンが表示される

### アドレス検索
- [ ] サンプルアドレスを入力: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
- [ ] 「調査」ボタンをクリック
- [ ] 調査ページに遷移する

### グラフ表示
- [ ] トランザクショングラフタブが表示される
- [ ] ノード（円）とエッジ（線）が表示される
- [ ] レイアウトボタン（ツリー、円形、リスク）が表示される
- [ ] ノードをクリックすると詳細が表示される

### パターン検出
- [ ] パターン検出タブをクリック
- [ ] 検出されたパターンが表示される
- [ ] 日本語で表示される（ウォッシュトレーディング、ポンジスキームなど）
- [ ] 証拠リストが表示される

### リスク評価
- [ ] リスク評価タブをクリック
- [ ] リスクスコア（0-100）が表示される
- [ ] リスクレベル（高/中/低）が日本語で表示される
- [ ] 寄与要因リストが日本語で表示される

### AIレポート
- [ ] AIレポートタブをクリック
- [ ] 日本語でレポートが表示される
- [ ] 調査概要が読める

---

## 🐛 トラブルシューティング

### 問題: フロントエンドは表示されるが、検索が動作しない

**原因**: バックエンドに接続できていない

**解決策**:
1. Vercelの環境変数 `NEXT_PUBLIC_API_URL` を確認
2. RailwayのURLが正しいか確認
3. Railwayの `CORS_ORIGINS` が正しいか確認

### 問題: "Failed to fetch" エラー

**原因**: CORS設定の問題

**解決策**:
```bash
# Railwayで確認
CORS_ORIGINS=https://metasleuth-nextgen.vercel.app

# または一時的に全て許可（開発時のみ）
CORS_ORIGINS=*
```

### 問題: バックエンドが起動しない

**原因**: 環境変数が不足

**解決策**:
Railwayで以下を確認：
- `SECRET_KEY` が設定されているか
- PostgreSQLとRedisが追加されているか
- `DATABASE_URL` と `REDIS_URL` が自動設定されているか

---

## 🔄 自動デプロイ設定

### mainブランチへのpushで自動デプロイ

**Vercel**:
- mainブランチへのpushで自動的にデプロイされます
- プレビュー環境も自動作成されます

**Railway**:
- mainブランチへのpushで自動的にデプロイされます
- ロールバックも簡単にできます

### デプロイステータスの確認

**Vercel**:
- ダッシュボード: https://vercel.com/dashboard
- デプロイ履歴、パフォーマンス指標を確認

**Railway**:
- ダッシュボード: https://railway.app/dashboard
- ログ、メトリクス、使用状況を確認

---

## 📊 モニタリング

### Vercel Analytics
- ページビュー数
- レスポンスタイム
- ユーザーエクスペリエンススコア

### Railway Logs
```
1. プロジェクトを開く
2. サービスをクリック
3. 「View Logs」をクリック
```

---

## 💰 コスト見積もり

### 無料枠（個人プロジェクト、開発環境）
- **Vercel**: 100GB帯域幅/月、無制限デプロイ
- **Railway**: $5クレジット/月、500時間実行時間
- **合計**: 完全無料で開始可能

### 本番環境（月間1000ユーザー）
- **Vercel Pro**: $20/月
- **Railway**: $10-20/月（使用量に応じて）
- **合計**: 約$30-40/月

### エンタープライズ（月間10000ユーザー）
- **Vercel Enterprise**: $150/月〜
- **Railway**: $100/月〜
- または自己ホスティング（AWS/GCPで$50/月〜）

---

## 🎯 次のステップ

### 1. カスタムドメインを設定
```
Vercelで:
1. Settings → Domains
2. カスタムドメインを追加
3. DNSレコードを設定
```

### 2. SSL証明書（自動）
- VercelとRailwayは自動的にHTTPSを設定
- Let's Encryptで無料SSL証明書

### 3. 監視とアラート
- Vercel Analyticsを有効化
- Sentryでエラートラッキング
- UptimeRobotで死活監視

### 4. パフォーマンス最適化
- 画像最適化（Next.js Image）
- CDN活用（自動）
- キャッシング設定

---

## 📞 サポート

デプロイで問題が発生した場合：

1. **ドキュメント**: `DEPLOYMENT.md` を確認
2. **GitHub Issues**: https://github.com/Hide9602/block-chain-project/issues
3. **Railway Discord**: https://discord.gg/railway
4. **Vercel Support**: https://vercel.com/support

---

## 🎉 おめでとうございます！

MetaSleuth NextGenが本番環境で稼働しています！

**デプロイされたアプリケーション**:
- ✅ フロントエンド: Vercel
- ✅ バックエンド: Railway
- ✅ データベース: PostgreSQL（Railway）
- ✅ キャッシュ: Redis（Railway）
- ✅ 完全多言語対応（日英）
- ✅ HTTPS対応
- ✅ 自動デプロイ設定済み

**世界中からアクセス可能です！** 🌍🚀

---

*最終更新: 2025-10-28*
