# ---- Stage 1: build with proxy and cert ----
FROM python:3.11-slim as builder

ARG http_proxy
ARG https_proxy

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

# 証明書を追加して update-ca-certificates
COPY proxy.crt /usr/local/share/ca-certificates/proxy.crt
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl build-essential gcc && \
    update-ca-certificates

# 作業ディレクトリ作成
WORKDIR /app

# 必要ファイルをコピーして pip install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# アプリ本体をコピー
COPY app/ ./app/

# ---- Stage 2: runtime with non-root user ----
FROM python:3.11-slim as final

# 非rootユーザー作成
RUN useradd -m fastapiuser

# 作業ディレクトリ
WORKDIR /home/fastapiuser/app

# builder から必要ファイルのみコピー
COPY --from=builder /install /usr/local
COPY --from=builder /app /home/fastapiuser/app

# 権限変更
RUN chown -R fastapiuser:fastapiuser /home/fastapiuser

# 非rootユーザーに切り替え
USER fastapiuser

# FastAPI 起動（uvicorn）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


docker build \
  --build-arg http_proxy=http://proxy.local:8080 \
  --build-arg https_proxy=http://proxy.local:8080 \
  -t fastapi-app .
