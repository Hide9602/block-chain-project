# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージのアップデートとインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python依存パッケージのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# 一時ディレクトリの作成
RUN mkdir -p /tmp/metasleuth/uploads /tmp/metasleuth/reports

# 実行ユーザーの作成（セキュリティのため）
RUN useradd -m -u 1000 metasleuth && \
    chown -R metasleuth:metasleuth /app /tmp/metasleuth

# ユーザー切替
USER metasleuth

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# ポート公開
EXPOSE 8000

# デフォルトコマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
