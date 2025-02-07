FastAPI × SQLAlchemy × PostgreSQL で CRUD 処理をオブジェクト指向で作成すると、以下のような構成になります。

### **1. 基本の設計方針**
オブジェクト指向の観点で、以下のような分離を意識します：
- **モデル層（models）**: SQLAlchemy を用いたデータベースのテーブル定義
- **スキーマ層（schemas）**: Pydantic を用いたデータバリデーション
- **リポジトリ層（repositories）**: データ操作をカプセル化
- **サービス層（services）**: ビジネスロジックを実装
- **ルーター層（routers）**: FastAPI のエンドポイントを定義

---

## **2. 実装例**
### **(1) models.py（SQLAlchemyモデル）**
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
```
➡ **OOP的なポイント**  
- `User` クラスが `Base` を継承し、データベースのテーブルをオブジェクトとして表現
- クラスインスタンスがデータの操作対象になる

---

### **(2) schemas.py（Pydanticスキーマ）**
```python
from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
```
➡ **OOP的なポイント**  
- `UserBase` を継承し、`UserCreate` や `UserResponse` で拡張
- `UserResponse` に `id` を追加し、レスポンス用スキーマとして設計

---

### **(3) repositories.py（データアクセス層）**
```python
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        user = User(name=user_data.name, email=user_data.email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
```
➡ **OOP的なポイント**  
- `UserRepository` をインスタンス化し、`self.db` を保持することで依存性注入が可能に
- クラスの責務が明確になり、テスト時にモックしやすくなる

---

### **(4) services.py（ビジネスロジック層）**
```python
from fastapi import HTTPException

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        user = self.repository.create_user(user_data)
        return UserResponse.model_validate(user)

    def get_user(self, user_id: int) -> UserResponse:
        user = self.repository.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)
```
➡ **OOP的なポイント**  
- `UserService` も DI 可能になり、テストが容易に
- `HTTPException` を使い、適切なエラーハンドリングを実装

---

### **(5) main.py（FastAPI ルーター）**
```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from services import UserService
from repositories import UserRepository
from schemas import UserCreate, UserResponse

app = FastAPI()

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)
    return service.create_user(user)

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)
    return service.get_user(user_id)
```
➡ **OOP的なポイント**  
- `UserRepository` を `UserService` に依存性注入し、拡張しやすくする
- `Depends(get_db)` を利用し、データベースセッションの管理を明確化

---

## **3. まとめ**
| 層 | 役割 | OOP的ポイント |
|----|----|----|
| `models.py` | DBモデル定義 | ORM を OOP で実装 |
| `schemas.py` | データバリデーション | Pydantic の継承構造 |
| `repositories.py` | データ操作 | クラスを分離し責務を明確化 |
| `services.py` | ビジネスロジック | `UserRepository` を利用してカプセル化 |
| `main.py` | API ルーター | `UserService` を使い関心の分離 |

**この構成のメリット**  
✅ 責務が明確で OOP の原則（カプセル化・分離）に従っている  
✅ `UserRepository` や `UserService` を Mock できるので、テストしやすい  
✅ 変更に強く、拡張が容易（新しいロジックを `services.py` に追加しやすい）

