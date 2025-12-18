承知しました。まずはローカル環境だけで足回りを整えましょう。

ローカル環境（Docker Compose + Pytest）において、SQLファイル管理を廃止し、Pythonコードベースの高速なテスト環境へ移行するための手順をまとめました。

---

# ローカル環境移行手順書 (Docker Compose & Pytest)

## Step 1: `docker-compose.yml` の修正

DBコンテナにSQLファイルを読み込ませている記述（volumes）を削除またはコメントアウトします。これだけでコンテナ起動が速くなります。

**修正前（例）:**

```yaml
  db:
    image: postgres:15
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql # 削除

```

**修正後:**

```yaml
  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: test_db # テスト用のDB名を指定

```

## Step 2: `conftest.py` の実装

テスト実行時に自動でテーブルを作り、終わったら消す仕組みを作ります。
`tests/conftest.py` を作成（または修正）してください。

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 【重要】ここにあなたのモデル定義をimportしてください
# これがないとテーブルが作成されません
from myapp.database import Base
from myapp import models 

# ローカルのDockerへの接続情報
DATABASE_URL = "postgresql://user:password@localhost:5432/test_db"

@pytest.fixture(scope="session")
def db_engine():
    """
    テスト開始時に1回だけテーブルを作成し、終了時に削除する
    """
    engine = create_engine(DATABASE_URL)

    # 念のため、前のテストの残りカスを消去
    Base.metadata.drop_all(engine)
    
    # ここでモデル定義に基づいてテーブル作成 (init.sqlの代わり)
    Base.metadata.create_all(engine)

    yield engine

    # テストが終わったらテーブルを削除して綺麗にする
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    テストケースごとにデータをリセットする (ロールバック方式)
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    # コミットせずにロールバック (データは保存されない)
    session.close()
    transaction.rollback()
    connection.close()

```

## Step 3: モデル読み込みの確認

`Base.metadata.create_all(engine)` が正しく動くには、すべてのモデルファイルが読み込まれている必要があります。
`myapp/models/__init__.py` などで、作成したモデル（Userなど）をimportしているか確認してください。

```python
# myapp/models/__init__.py の例
from .user import User
from .item import Item
# ここに書いてあるモデルがテーブル化されます

```

## Step 4: 動作確認

設定ができたら、一度コンテナを作り直してテストを実行します。

1. **コンテナの再起動** (古いボリュームを消すため)
```bash
docker-compose down -v
docker-compose up -d

```


※ `-v` オプションで古いデータボリュームを削除し、真っさらな状態で起動させます。
2. **テスト実行**
```bash
pytest

```



これでエラーなくテストが通り、かつDBコンテナのログにエラーが出ていなければ移行完了です！

### 補足：デバッグ時にデータを残したい場合

テストが失敗したとき、DBの中身を見て調査したいことがありますよね。
その場合は、一時的に `conftest.py` の最後の `drop_all` をコメントアウトしてください。

```python
    yield engine

    # Base.metadata.drop_all(engine)  <-- コメントアウトすると、テスト後もテーブルが残る
    engine.dispose()

```

これでローカル開発環境が「コードファースト」になり、SQLファイル管理の手間から解放されます。
