# コントリビューションガイド

**MetaSleuth NextGen へようこそ！**

このドキュメントでは、プロジェクトへの貢献方法を説明します。

---

## 🎯 コントリビューションの種類

### 1. コード貢献
- 新機能の実装
- バグ修正
- パフォーマンス改善
- リファクタリング

### 2. ドキュメント貢献
- README、ガイドの改善
- API ドキュメントの追加
- チュートリアル作成

### 3. 翻訳貢献
- 日英翻訳の品質向上
- ネイティブレビュー
- 専門用語辞書の拡充

### 4. テスト貢献
- ユニットテストの追加
- E2Eテストの作成
- バグレポート

---

## 🚀 開発環境のセットアップ

### 必要要件

- Node.js 18.x 以上
- Python 3.11 以上
- Docker 20.x 以上
- Docker Compose 2.x 以上
- Git 2.x 以上

### セットアップ手順

```bash
# 1. リポジトリをフォーク
# GitHub上で "Fork" ボタンをクリック

# 2. クローン
git clone https://github.com/YOUR_USERNAME/metasleuth-nextgen.git
cd metasleuth-nextgen

# 3. リモートリポジトリ設定
git remote add upstream https://github.com/ORIGINAL_OWNER/metasleuth-nextgen.git

# 4. 環境変数設定
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 5. Docker環境起動
docker-compose up -d

# 6. フロントエンド依存パッケージインストール（ローカル開発の場合）
cd frontend
npm install

# 7. バックエンド依存パッケージインストール（ローカル開発の場合）
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🌳 ブランチ戦略

### メインブランチ

- **main**: 本番環境用の安定版
- **genspark_ai_developer**: 開発ブランチ（GenSpark AI Developer専用）
- **develop**: 統合開発ブランチ

### フィーチャーブランチ命名規則

```
feature/短い説明    # 新機能
bugfix/短い説明     # バグ修正
hotfix/短い説明     # 緊急修正
docs/短い説明       # ドキュメント
refactor/短い説明   # リファクタリング
test/短い説明       # テスト追加
```

**例**:
- `feature/add-graph-export`
- `bugfix/fix-auth-token-expiry`
- `docs/update-api-documentation`

---

## 📝 コミットメッセージ規約

### Conventional Commits形式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type一覧

| Type | 説明 | 例 |
|------|------|---|
| `feat` | 新機能 | `feat(auth): Add OAuth2 support` |
| `fix` | バグ修正 | `fix(graph): Fix node rendering issue` |
| `docs` | ドキュメント | `docs(readme): Update setup instructions` |
| `style` | コードスタイル | `style(frontend): Format with Prettier` |
| `refactor` | リファクタリング | `refactor(api): Simplify auth logic` |
| `test` | テスト | `test(report): Add unit tests for PDF generation` |
| `chore` | その他 | `chore(deps): Update dependencies` |
| `perf` | パフォーマンス | `perf(graph): Optimize Cypher queries` |
| `ci` | CI/CD | `ci(github): Add automated testing` |

### コミットメッセージ例

```bash
# 良い例
feat(analysis): Add pattern detection for smurfing

Implement rule-based pattern matching for detecting smurfing
attacks. The algorithm identifies transactions split into multiple
small amounts to avoid reporting thresholds.

Closes #123

# 悪い例
fix stuff
update code
WIP
```

---

## 🔄 Pull Request (PR) プロセス

### 1. ブランチ作成

```bash
# 最新のdevelopを取得
git checkout genspark_ai_developer
git pull upstream genspark_ai_developer

# 新しいフィーチャーブランチ作成
git checkout -b feature/your-feature-name
```

### 2. 開発

```bash
# コードを書く
# テストを書く
# ドキュメントを更新

# コミット
git add .
git commit -m "feat(scope): Description"
```

### 3. プッシュ前の確認

```bash
# コーディング規約チェック
cd frontend && npm run lint
cd backend && black . && isort . && flake8

# テスト実行
cd frontend && npm test
cd backend && pytest

# ビルド確認
cd frontend && npm run build
```

### 4. プッシュ

```bash
git push origin feature/your-feature-name
```

### 5. Pull Request作成

#### PRテンプレート

```markdown
## 概要
この PR は XXX を実装/修正します。

## 変更内容
- [ ] 機能Aの追加
- [ ] バグBの修正
- [ ] テストCの追加

## スクリーンショット（UI変更の場合）
（スクリーンショットを添付）

## テスト方法
1. XXX を起動
2. YYY を実行
3. ZZZ を確認

## チェックリスト
- [ ] コードレビュー可能な状態
- [ ] テスト追加済み
- [ ] ドキュメント更新済み
- [ ] Breaking Changesがある場合は明記
- [ ] コミットメッセージがConventional Commits形式

## 関連Issue
Closes #123
Refs #456
```

### 6. レビュー対応

- レビュアーからのフィードバックに対応
- 修正をコミットしてプッシュ
- 再レビュー依頼

### 7. マージ

- レビュー承認後、メンテナーがマージ
- Squash Merge を使用（複数コミットを1つに）

---

## 🧪 テストガイドライン

### フロントエンド（Jest + React Testing Library）

```typescript
// components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### バックエンド（Pytest）

```python
# tests/api/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert "id" in response.json()

def test_login_success():
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### テストカバレッジ目標

- **ユニットテスト**: 80%以上
- **統合テスト**: 主要パスをカバー
- **E2Eテスト**: クリティカルパスをカバー

---

## 📚 コーディング規約

### TypeScript / JavaScript

#### ESLint + Prettier設定

```json
{
  "extends": [
    "next/core-web-vitals",
    "airbnb",
    "airbnb-typescript",
    "prettier"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "import/prefer-default-export": "off"
  }
}
```

#### 命名規則

```typescript
// コンポーネント: PascalCase
export const UserProfile = () => { ... }

// 関数: camelCase
const fetchUserData = async () => { ... }

// 定数: UPPER_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';

// 型: PascalCase
interface UserData {
  id: string;
  email: string;
}

// Enum: PascalCase
enum UserRole {
  Admin = 'admin',
  User = 'user',
}
```

### Python

#### Black + isort + flake8設定

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100
```

#### 命名規則

```python
# クラス: PascalCase
class UserService:
    pass

# 関数・変数: snake_case
def get_user_by_id(user_id: str) -> User:
    pass

# 定数: UPPER_SNAKE_CASE
API_BASE_URL = "https://api.example.com"

# 非公開: _で開始
def _internal_function():
    pass
```

---

## 🌐 翻訳ガイドライン

### 翻訳の原則

1. **正確性**: 専門用語は正確に翻訳
2. **自然さ**: 母語話者が自然に感じる表現
3. **一貫性**: 同じ用語は同じ翻訳を使用
4. **文化的配慮**: 文化的文脈を考慮

### 専門用語翻訳例

| English | 日本語 | 備考 |
|---------|--------|------|
| Blockchain | ブロックチェーン | カタカナ表記 |
| Wallet | ウォレット | カタカナ表記 |
| Transaction | トランザクション | カタカナ表記 |
| Money Laundering | マネーロンダリング | カタカナ表記 |
| Forensics | フォレンジック | カタカナ表記 |
| Evidence | 証拠 | 漢字表記 |
| Investigation | 調査 | 漢字表記 |

### 翻訳ファイルの編集

```json
// locales/ja/common.json
{
  "buttons": {
    "submit": "送信",
    "cancel": "キャンセル"
  }
}
```

---

## 🐛 バグレポート

### Issueテンプレート

```markdown
## バグの説明
簡潔に説明してください。

## 再現手順
1. XXX にアクセス
2. YYY をクリック
3. ZZZ が発生

## 期待される動作
XXX が表示されるべき

## 実際の動作
YYY が表示された

## 環境
- OS: macOS 14.0
- ブラウザ: Chrome 120
- バージョン: v1.0.0

## スクリーンショット
（必要に応じて添付）

## 追加情報
その他の関連情報
```

---

## 💡 機能リクエスト

### Issueテンプレート

```markdown
## 機能の説明
XXX 機能を追加してほしい

## ユースケース
XXX の場合に YYY ができると便利

## 提案する解決策
ZZZ を実装することで実現できる

## 代替案
AAA も考えられる

## 優先度
- [ ] Critical
- [x] High
- [ ] Medium
- [ ] Low
```

---

## 📞 コミュニケーション

### GitHub Discussions
- 質問、アイデア、雑談など

### GitHub Issues
- バグレポート
- 機能リクエスト

### Pull Requests
- コードレビュー
- 実装の議論

---

## 🏆 コントリビューター認定

### レベル制度

| レベル | 条件 | 特典 |
|--------|------|------|
| **Contributor** | 1つ以上のPRマージ | READMEに名前掲載 |
| **Active Contributor** | 5つ以上のPRマージ | プロジェクトへの投票権 |
| **Core Contributor** | 20以上のPRマージ | リポジトリ直接アクセス |
| **Maintainer** | プロジェクトリードによる任命 | 全権限 |

---

## 📜 ライセンス

このプロジェクトに貢献することで、あなたの貢献が MIT License の下でライセンスされることに同意したものとみなされます。

---

## 🙏 謝辞

貢献してくださったすべての方に感謝します！

---

**質問がある場合は、遠慮なく Issue を作成してください。**

Happy Contributing! 🎉
