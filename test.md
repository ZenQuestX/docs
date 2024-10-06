以下は、Dockerを使用してFastAPI、SQLAlchemy、Alembic、SQLiteを組み合わせたバックエンド開発の詳細設計書です。ディレクトリ構成は粒度を細かくしています。

## ディレクトリ構成

```
project/
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   └── items.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── item.py
│   │   ├── session.py
│   ├── main.py
├── docker/
│   ├── api/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── docker-compose.yml
└── tests/
    ├── __init__.py
    ├── test_items.py
```

## 詳細設計

### 1. `alembic/`

- **env.py**: Alembicの設定ファイル。SQLAlchemyの接続設定を記述。
- **script.py.mako**: マイグレーションスクリプトのテンプレート。
- **alembic.ini**: Alembicのメイン設定ファイル。
- **versions/**: マイグレーションファイルを格納するディレクトリ。

### 2. `app/`

#### 2.1 `api/`

- **endpoints/**: APIエンドポイントを定義するディレクトリ。
  - **items.py**: アイテムに関するAPIエンドポイントを定義。

#### 2.2 `core/`

- **config.py**: アプリケーションの設定を管理。

#### 2.3 `db/`

- **base.py**: SQLAlchemyのベースクラスを定義。
- **models/**: データベースモデルを定義するディレクトリ。
  - **item.py**: アイテムモデルを定義。
- **session.py**: データベースセッションを管理。

#### 2.4 `main.py`

- FastAPIアプリケーションのエントリーポイント。

### 3. `docker/`

#### 3.1 `api/`

- **Dockerfile**: APIコンテナのDockerfile。
- **requirements.txt**: 必要なPythonパッケージを記述。

#### 3.2 `docker-compose.yml`

- Docker Composeの設定ファイル。

### 4. `tests/`

- **test_items.py**: アイテムエンドポイントのテスト。

## 主要ファイルの内容

### `app/main.py`

```python
from fastapi import FastAPI
from app.api.endpoints import items
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### `app/db/session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### `app/db/base.py`

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

### `app/db/models/item.py`

```python
from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
```

### `app/api/endpoints/items.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.item import Item

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items
```

### `docker/api/Dockerfile`

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker/requirements.txt`

```
fastapi
uvicorn
sqlalchemy
alembic
sqlite
```

### `docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=sqlite:///./test.db
```

この設計書を基に、Dockerを使用したFastAPIアプリケーションの開発を進めてください。何か質問があれば、いつでもどうぞ！
