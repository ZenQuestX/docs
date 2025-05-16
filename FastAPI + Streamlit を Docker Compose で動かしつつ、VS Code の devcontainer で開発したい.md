
## ✅ やりたいことの整理

| 項目              | 内容                                    |
| --------------- | ------------------------------------- |
| 開発環境            | VS Code の **Dev Containers** 拡張機能で構築  |
| アプリ構成           | FastAPI + Streamlit（2サービス）            |
| 起動方法            | `docker compose up` で両方起動（VS Codeからも） |
| 動作対象            | ローカルPC内（WSL2）                         |
| セキュリティ・rootless | 不要（通常のDockerでOK）                      |

---

## ✅ フォルダ構成（最小構成例）

```
my-app/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── app/
│   ├── main.py             ← FastAPI
│   └── streamlit_app.py    ← Streamlit
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 🧱 1. `.devcontainer/devcontainer.json`

```json
{
  "name": "fastapi-streamlit-dev",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "fastapi",
  "workspaceFolder": "/app",
  "extensions": [
    "ms-python.python",
    "ms-azuretools.vscode-docker"
  ],
  "settings": {
    "terminal.integrated.defaultProfile.linux": "bash"
  }
}
```

* `service: fastapi` → devcontainer はこのサービス内に入ります
* `workspaceFolder: /app` → コンテナ内で作業するディレクトリ

---

## 🧱 2. `.devcontainer/Dockerfile`（FastAPI/Streamlit共通）

```Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

---

## 🧱 3. `docker-compose.yml`

```yaml
version: "3.9"
services:
  fastapi:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ./app:/app
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  streamlit:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ./app:/app
    ports:
      - "8501:8501"
    command: streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🧱 4. `requirements.txt`

```txt
fastapi
uvicorn
streamlit
```

---

## ▶️ 実行手順（VS Code）

1. 左下の「>< Dev Container」アイコン → **「Reopen in Container」**
2. 開発コンテナが `fastapi` サービス上で起動
3. ターミナルから `docker compose up` で `streamlit` も含めて全体起動可能

---

## 🌐 動作確認

* `http://localhost:8000` → FastAPI
* `http://localhost:8501` → Streamlit

Streamlit から FastAPI にアクセスする場合は、`http://host.docker.internal:8000` を使用（Windows/WSL2ならこれでOK）

---

## ✅ 補足

* `streamlit` にも devcontainer 入れたい場合は、`service: streamlit` に切り替える or 別コンテナを開く必要があります
* CI/CD では `docker-compose` のみで動くので、devcontainer は開発者用の便利な拡張です

---

必要であれば、**このテンプレート一式をGitHubレポジトリ用にパッケージ化**して差し上げられます。
「FastAPI + Streamlit + DevContainer 開発テンプレートをZIPで欲しい」などあれば遠慮なくどうぞ！
