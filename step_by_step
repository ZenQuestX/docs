プロジェクトを段階的に進めることで、複雑さを管理しやすくなります。以下のステップに従って、基本的な部分から始めて徐々に機能を追加していくと良いでしょう。

### ステップ1: 基本的なFastAPIアプリケーションのセットアップ

1. **プロジェクトディレクトリの作成**
   ```bash
   mkdir project
   cd project
   ```

2. **仮想環境の作成と有効化**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windowsの場合は `venv\Scripts\activate`
   ```

3. **必要なパッケージのインストール**
   ```bash
   pip install fastapi uvicorn
   ```

4. **基本的なFastAPIアプリケーションの作成**
   - `main.py`を作成し、以下の内容を追加
     ```python
     from fastapi import FastAPI

     app = FastAPI()

     @app.get("/")
     def read_root():
         return {"message": "Hello World"}
     ```

5. **アプリケーションの起動**
   ```bash
   uvicorn main:app --reload
   ```

### ステップ2: データベースのセットアップ

1. **SQLAlchemyとSQLiteのインストール**
   ```bash
   pip install sqlalchemy sqlite
   ```

2. **データベースモデルの作成**
   - `db/models/item.py`を作成し、以下の内容を追加
     ```python
     from sqlalchemy import Column, Integer, String
     from sqlalchemy.ext.declarative import declarative_base

     Base = declarative_base()

     class Item(Base):
         __tablename__ = "items"

         id = Column(Integer, primary_key=True, index=True)
         name = Column(String, index=True)
         description = Column(String, index=True)
     ```

3. **データベースセッションの設定**
   - `db/session.py`を作成し、以下の内容を追加
     ```python
     from sqlalchemy import create_engine
     from sqlalchemy.orm import sessionmaker

     SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

     engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
     ```

### ステップ3: CRUD操作の追加

1. **CRUD操作の定義**
   - `db/crud/item.py`を作成し、以下の内容を追加
     ```python
     from sqlalchemy.orm import Session
     from db.models.item import Item

     def get_items(db: Session, skip: int = 0, limit: int = 10):
         return db.query(Item).offset(skip).limit(limit).all()

     def create_item(db: Session, item: Item):
         db.add(item)
         db.commit()
         db.refresh(item)
         return item
     ```

2. **APIエンドポイントの作成**
   - `api/endpoints/items.py`を作成し、以下の内容を追加
     ```python
     from fastapi import APIRouter, Depends, HTTPException
     from sqlalchemy.orm import Session
     from typing import List
     from db.session import SessionLocal
     from db.models.item import Item
     from db.crud import item as crud_item

     router = APIRouter()

     def get_db():
         db = SessionLocal()
         try:
             yield db
         finally:
             db.close()

     @router.get("/", response_model=List[Item])
     def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
         items = crud_item.get_items(db, skip=skip, limit=limit)
         return items

     @router.post("/", response_model=Item)
     def create_item(item: Item, db: Session = Depends(get_db)):
         return crud_item.create_item(db=db, item=item)
     ```

3. **ルーターの追加**
   - `main.py`を修正し、以下の内容を追加
     ```python
     from fastapi import FastAPI
     from api.endpoints import items
     from db.session import engine
     from db.models.item import Base

     Base.metadata.create_all(bind=engine)

     app = FastAPI()

     app.include_router(items.router, prefix="/items", tags=["items"])

     @app.get("/")
     def read_root():
         return {"message": "Hello World"}
     ```

### ステップ4: ログ設定の追加

1. **ログ設定の追加**
   - `core/logging.py`を作成し、以下の内容を追加
     ```python
     import logging
     from logging.config import dictConfig

     LOGGING_CONFIG = {
         "version": 1,
         "disable_existing_loggers": False,
         "formatters": {
             "default": {
                 "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
             },
         },
         "handlers": {
             "console": {
                 "class": "logging.StreamHandler",
                 "formatter": "default",
             },
             "file": {
                 "class": "logging.FileHandler",
                 "formatter": "default",
                 "filename": "app.log",
             },
         },
         "root": {
             "level": "INFO",
             "handlers": ["console", "file"],
         },
     }

     def setup_logging():
         dictConfig(LOGGING_CONFIG)
     ```

2. **ログ設定の読み込み**
   - `main.py`を修正し、以下の内容を追加
     ```python
     from core.logging import setup_logging

     setup_logging()
     ```

### ステップ5: Dockerのセットアップ

1. **Dockerfileの作成**
   - `docker/api/Dockerfile`を作成し、以下の内容を追加
     ```dockerfile
     FROM python:3.9

     WORKDIR /app

     COPY requirements.txt .

     RUN pip install --no-cache-dir -r requirements.txt

     COPY . .

     CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
     ```

2. **requirements.txtの作成**
   - `docker/api/requirements.txt`を作成し、以下の内容を追加
     ```
     fastapi
     uvicorn
     sqlalchemy
     alembic
     sqlite
     ```

3. **docker-compose.ymlの作成**
   - `docker/docker-compose.yml`を作成し、以下の内容を追加
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
           - ./logs:/app/logs  # ホストのlogsディレクトリをコンテナの/app/logsにマウント
         environment:
           - DATABASE_URL=sqlite:///./test.db
           - LOG_FILE_PATH=/app/logs/app.log
     ```

### ステップ6: マイグレーションの設定

1. **Alembicのインストール**
   ```bash
   pip install alembic
   ```

2. **Alembicの初期化**
   ```bash
   alembic init alembic
   ```

3. **`alembic.ini`の設定**
   - `alembic.ini`を修正し、データベースURLを設定
     ```ini
     sqlalchemy.url = sqlite:///./test.db
     ```

4. **`env.py`の修正**
   - `alembic/env.py`を修正し、モデルをインポート
     ```python
     from db.base import Base
     from db.models import item
     ```

これで、基本的な機能を段階的に構築しながら、最終的な構成に近づけることができます。何か質問があれば、いつでもどうぞ！

ソース: Copilot との会話、 2024/10/6
(1) github.com. https://github.com/TimouZ/weather-station/tree/ad31cb804ca1e24c4d1e08db8d2e8586030dff6f/config.py.
