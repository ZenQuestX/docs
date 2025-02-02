データベースの実装を抽象化して、様々なORMに対応できるCRUDモジュールを作成しましょう。Repository PatternとDependency Injectionを使用して、柔軟な設計にします。



このコードは以下のような特徴を持っています：

1. 抽象化されたリポジトリパターン
- `BaseRepository`クラスで基本的なCRUD操作を定義
- 具体的なデータベース実装から独立した抽象インターフェース

2. SQLAlchemy実装
- `SQLAlchemyRepository`クラスで実際のデータベース操作を実装
- 作成日時・更新日時の自動管理

3. 型安全性
- Pydanticモデルによるバリデーション
- Genericタイプを使用した柔軟な型システム

4. 依存性注入
- FastAPIのDependsを使用したリポジトリの注入
- テスト容易性の向上

他のデータベースに対応するには、`BaseRepository`を実装した新しいクラスを作成するだけです。例えば：

```python
class MongoDBRepository(BaseRepository[T, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, client: MongoClient, collection: str):
        self.client = client
        self.collection = collection
        # MongoDBの実装...

class RedisRepository(BaseRepository[T, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, redis: Redis):
        self.redis = redis
        # Redisの実装...
```

このような設計により、アプリケーションのビジネスロジックを変更することなく、データベースの実装を簡単に切り替えることができます。

使い方について質問や、特定のデータベース実装についてアドバイスが必要な場合は、お気軽にお聞きください。

# schemas.py
```python
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseSchema(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

T = TypeVar('T')
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(ABC, Generic[T, CreateSchemaType, UpdateSchemaType]):
    @abstractmethod
    async def create(self, schema: CreateSchemaType) -> T:
        pass

    @abstractmethod
    async def get(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        pass

    @abstractmethod
    async def update(self, id: int, schema: UpdateSchemaType) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass
```

# sqlalchemy_repository.py

```python
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Type, List, Optional

class SQLAlchemyRepository(BaseRepository[T, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    async def create(self, schema: CreateSchemaType) -> T:
        db_item = self.model(**schema.dict())
        db_item.created_at = datetime.utcnow()
        db_item.updated_at = datetime.utcnow()
        
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    async def get(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    async def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

    async def update(self, id: int, schema: UpdateSchemaType) -> Optional[T]:
        db_item = await self.get(id)
        if not db_item:
            return None

        for key, value in schema.dict(exclude_unset=True).items():
            setattr(db_item, key, value)
        
        db_item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    async def delete(self, id: int) -> bool:
        db_item = await self.get(id)
        if not db_item:
            return False

        self.db.delete(db_item)
        self.db.commit()
        return True
```

# usage_example.py

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

# モデルの定義
class User(BaseModel):
    id: int
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

# リポジトリの実装
class UserRepository(SQLAlchemyRepository[User, UserCreate, UserUpdate]):
    pass

app = FastAPI()

# 依存性の注入
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db, model=User)

@app.post("/users/", response_model=User)
async def create_user(
    user: UserCreate,
    repo: UserRepository = Depends(get_user_repository)
):
    return await repo.create(user)

@app.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repository)
):
    return await repo.get(user_id)

@app.get("/users/", response_model=List[User])
async def get_users(
    repo: UserRepository = Depends(get_user_repository)
):
    return await repo.get_all()

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    repo: UserRepository = Depends(get_user_repository)
):
    return await repo.update(user_id, user)

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repository)
):
    return await repo.delete(user_id)
```
