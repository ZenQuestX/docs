
# ✅ ゴール

* WSL2（Ubuntuなど）上に **完全な Docker エンジン** を直接導入
* `docker` と `docker compose` が CLI で動作
* rootless も可（今回は root 権限を使った標準構成を紹介）

---

# 🔧 ステップ一覧（Ubuntuベース）

1. 必要なパッケージのインストール
2. Docker Engine のインストール
3. Docker Compose v2 の導入
4. 動作確認
5. オプション：sudo不要にする設定

---

## 🔸 1. パッケージのインストール

```bash
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

---

## 🔸 2. Docker公式GPGキーの追加

```bash
sudo mkdir -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

---

## 🔸 3. Dockerリポジトリを追加

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

---

## 🔸 4. Docker Engine のインストール

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
```

---

## 🔸 5. Docker Compose v2 のインストール（プラグインとして）

```bash
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins

curl -SL https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-linux-$(uname -m) \
  -o $DOCKER_CONFIG/cli-plugins/docker-compose

chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```

> ✅ 最新バージョンはこちらで確認：
> [https://github.com/docker/compose/releases](https://github.com/docker/compose/releases)

---

## 🔸 6. 動作確認

```bash
docker version
docker compose version
```

期待される出力例：

```txt
Docker version 24.x.x, build xxxx
Docker Compose version v2.27.1
```

---

## 🔸 7. （オプション）sudo不要でdockerを使えるようにする

```bash
sudo usermod -aG docker $USER
```

その後、**一度WSLを完全に再起動**（`exit` → `wsl --shutdown`）してからログインし直してください。

---

# ✅ 動作確認コマンド

```bash
docker run hello-world
docker compose version
```

---

## ✅ まとめ

これで WSL2（Ubuntu）上に Docker + Docker Compose v2 を**完全に手動インストール**できました。
Docker Desktop は不要で、軽量・制御性の高い開発環境になります。

---

### 💡補足

* WSLのディスク容量が小さい場合、`/var/lib/docker` の保存場所を変更する構成も可能です（ご希望あればご案内できます）
* rootless（非sudo）構成や systemd連携も可能ですが、やや高度な設定が必要です

---

必要であれば、**FastAPI + Streamlit 用の Compose テンプレート** もこの環境用にカスタマイズしてお渡しできます。必要ですか？
