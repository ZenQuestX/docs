# SQLAlchemyとFastAPIのための汎用CRUD操作

このリポジトリでは、SQLAlchemyとFastAPIを使用した多数のテーブル構成のデータベースに対して、シンプルかつ効率的にCRUD操作を行うための汎用的な実装を提供しています。

## 特徴
- ...

## 実装詳細

## 1. Pydanticモデル
- Pydanticの基本スキーマ
- モデル別のPydanticスキーマ

## 2. SQLAlchemyモデル
- ユーザー、投稿、コメントモデルの実装

## 3. 汎用CRUD操作の実装 (Pydanticモデル使用)

```python
# db/crud_pydantic.py
from typing import Any, Dict, List, Type, TypeVar, Union, Optional, Generic, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from schemas.models import model_schema_map, relation_schema_map

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD操作のベースクラス
        :param model: SQLAlchemyモデルクラス
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        IDによる単一レコード取得
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        複数レコード取得
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        新規レコード作成 (Pydanticモデル使用)
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_from_dict(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """
        新規レコード作成 (辞書使用)
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        レコード更新
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        レコード削除
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


# Pydanticモデルを使用した汎用CRUD操作
class GenericCRUDWithSchema:
    @staticmethod
    def get_model_and_schema(table_name: str) -> Tuple[Type[ModelType], Type[CreateSchemaType], Type[ReadSchemaType], Type[UpdateSchemaType]]:
        """テーブル名からモデルとスキーマを取得する"""
        # SQLAlchemyモデルを取得
        from db.models import all_models
        model = None
        for m in all_models:
            if m.__tablename__ == table_name:
                model = m
                break
        
        if not model:
            raise ValueError(f"Model with table name '{table_name}' not found")
        
        # Pydanticスキーマを取得
        if table_name not in model_schema_map:
            raise ValueError(f"Schema for table '{table_name}' not found")
        
        create_schema, read_schema, update_schema = model_schema_map[table_name]
        return model, create_schema, read_schema, update_schema

    @staticmethod
    def create_item(db: Session, table_name: str, item_data: Dict[str, Any]) -> Any:
        """
        テーブル名とデータからレコードを作成する汎用メソッド
        """
        model, create_schema, read_schema, _ = GenericCRUDWithSchema.get_model_and_schema(table_name)
        
        # データをPydanticモデルを通して検証
        validated_data = create_schema(**item_data)
        
        # 検証済みデータでレコード作成
        db_item = model(**validated_data.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # 読み取り用スキーマで返却
        return read_schema.from_orm(db_item)

    @staticmethod
    def update_item(db: Session, table_name: str, item_id: int, item_data: Dict[str, Any]) -> Any:
        """
        テーブル名、ID、データからレコードを更新する汎用メソッド
        """
        model, _, read_schema, update_schema = GenericCRUDWithSchema.get_model_and_schema(table_name)
        
        # データをPydanticモデルを通して検証
        validated_data = update_schema(**item_data)
        
        # レコード取得
        db_item = db.query(model).filter(model.id == item_id).first()
        if not db_item:
            return None
        
        # 検証済みデータでレコード更新
        update_data = validated_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_item, field):
                setattr(db_item, field, value)
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # 読み取り用スキーマで返却
        return read_schema.from_orm(db_item)

    @staticmethod
    def get_with_relations(db: Session, table_name: str, item_id: int) -> Any:
        """
        リレーションを含めてレコードを取得する汎用メソッド
        """
        model, _, _, _ = GenericCRUDWithSchema.get_model_and_schema(table_name)
        
        if table_name not in relation_schema_map:
            raise ValueError(f"Relation schema for table '{table_name}' not found")
        
        relation_schema = relation_schema_map[table_name]
        
        # レコード取得
        db_item = db.query(model).filter(model.id == item_id).first()
        if not db_item:
            return None
        
        # リレーションを含むスキーマで返却
        return relation_schema.from_orm(db_item)
```

## 4. リレーション対応のCRUD操作

```python
# Pydanticモデルを使用したリレーション対応CRUD操作
class RelationalCRUDWithSchema(GenericCRUDWithSchema):
    @staticmethod
    def create_with_relations(
        db: Session, 
        main_table: str, 
        main_data: Dict[str, Any],
        relations: Dict[str, List[Dict[str, Any]]] = None
    ) -> Any:
        """
        メインテーブルとリレーション先のデータを一括で作成
        
        :param main_table: メインテーブル名
        :param main_data: メインテーブルのデータ
        :param relations: {"relation_name": [{"field": "value"}, ...], ...}
        """
        # メインテーブルのモデルとスキーマを取得
        main_model, main_create_schema, _, _ = GenericCRUDWithSchema.get_model_and_schema(main_table)
        
        # メインデータをPydanticモデルを通して検証
        validated_main_data = main_create_schema(**main_data)
        
        # メインレコード作成
        main_obj = main_model(**validated_main_data.dict())
        db.add(main_obj)
        db.flush()  # IDを生成するためにflush
        
        # リレーション先レコード作成
        if relations:
            for relation_name, relation_data_list in relations.items():
                # リレーションの情報を取得
                relation_attr = getattr(main_model, relation_name, None)
                if relation_attr is None:
                    continue
                
                # リレーション先のモデルを取得
                relation_model = relation_attr.property.mapper.class_
                relation_table_name = relation_model.__tablename__
                
                # リレーション先のスキーマを取得
                if relation_table_name not in model_schema_map:
                    continue
                
                relation_create_schema = model_schema_map[relation_table_name][0]
                
                # 外部キー名を取得
                foreign_key = None
                for local_col, remote_col in relation_attr.property.local_remote_pairs:
                    if local_col.name == 'id':
                        foreign_key = remote_col.name
                
                if not foreign_key:
                    continue
                
                # リレーション先レコード作成
                for relation_data in relation_data_list:
                    relation_data[foreign_key] = main_obj.id
                    validated_relation_data = relation_create_schema(**relation_data)
                    relation_obj = relation_model(**validated_relation_data.dict())
                    db.add(relation_obj)
        
        db.commit()
        db.refresh(main_obj)
        
        # リレーションを含むスキーマで返却
        if main_table in relation_schema_map:
            return relation_schema_map[main_table].from_orm(main_obj)
        else:
            return model_schema_map[main_table][1].from_orm(main_obj)  # 通常のReadスキーマで返却
```

## 5. FastAPIエンドポイント

```python
# api/endpoints/generic_pydantic.py
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.crud_pydantic import GenericCRUDWithSchema, RelationalCRUDWithSchema
from db.database import get_db
from schemas.base import (
    GenericCreateRequest, 
    GenericUpdateRequest, 
    BulkCreateRequest,
    RelationalCreateRequest,
    RelationalUpdateRequest
)

router = APIRouter()


@router.post("/{table_name}/")
def create_item(
    request: GenericCreateRequest,
    db: Session = Depends(get_db)
):
    """
    どのテーブルに対しても汎用的にレコードを作成できるエンドポイント
    """
    try:
        result = GenericCRUDWithSchema.create_item(
            db, 
            request.table_name, 
            request.data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{table_name}/{item_id}")
def update_item(
    request: GenericUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    どのテーブルに対しても汎用的にレコードを更新できるエンドポイント
    """
    try:
        result = GenericCRUDWithSchema.update_item(
            db, 
            request.table_name, 
            request.item_id, 
            request.data
        )
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Item with id {request.item_id} not found"
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{table_name}/{item_id}/relations")
def get_item_with_relations(
    table_name: str,
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    リレーションを含めてレコードを取得するエンドポイント
    """
    try:
        result = GenericCRUDWithSchema.get_with_relations(db, table_name, item_id)
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Item with id {item_id} not found"
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relational/create/")
def create_with_relations(
    request: RelationalCreateRequest,
    db: Session = Depends(get_db)
):
    """
    メインテーブルとリレーション先のデータを一括で作成するエンドポイント
    """
    try:
        result = RelationalCRUDWithSchema.create_with_relations(
            db, 
            request.main_table, 
            request.main_data, 
            request.relations
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 6. FastAPIエンドポイントの使用例

### リレーションを含むユーザー作成リクエスト

```json
POST /api/generic-pydantic/relational/create/
{
  "main_table": "users",
  "main_data": {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  },
  "relations": {
    "posts": [
      {
        "title": "My first post",
        "content": "This is the content of my first post"
      },
      {
        "title": "My second post",
        "content": "This is the content of my second post"
      }
    ]
  }
}
```

### 汎用的なレコード作成リクエスト

```json
POST /api/generic-pydantic/users/
{
  "table_name": "users",
  "data": {
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
  }
}
```

### 汎用的なレコード更新リクエスト

```json
PUT /api/generic-pydantic/users/1
{
  "table_name": "users",
  "item_id": 1,
  "data": {
    "username": "updateduser",
    "email": "updated@example.com"
  }
}
```

### リレーションを含むレコード取得リクエスト

```
GET /api/generic-pydantic/users/1/relations
```

## メリットと特徴

1. **型安全性**: Pydanticモデルによるデータ検証
2. **自動ドキュメント生成**: FastAPIの自動OpenAPI/Swagger生成に対応
3. **スキーマの再利用**: 同じPydanticモデルをAPIとデータベース操作の両方で使用
4. **リレーション処理の簡素化**: 複雑なリレーションを持つデータも単一リクエストで操作可能
5. **拡張性**: 新しいモデルを追加する際にも共通処理を再利用可能

## 注意事項

- `get_model_and_schema`メソッドはプロジェクトの構造に合わせて調整が必要です
- 本番環境では、セキュリティ上の理由から許可するテーブルやフィールドを制限することをお勧めします
- このコードはSQLAlchemyのリレーションシップを最大限に活用するため、モデル間のリレーションが適切に定義されている必要があります
- Pydanticモデルとの整合性を保つために、モデルの変更時は両方を更新する必要があります

## ライセンス

MIT 特徴

- **汎用CRUD操作**: テーブル名を指定するだけで任意のテーブルに対して操作可能
- **一括操作**: 複数テーブルへの同時処理をサポート
- **リレーション対応**: 親子関係のあるデータを一度に作成・更新可能
- **既存モデルの活用**: SQLAlchemyとPydanticの既存モデル定義をそのまま利用
- **シンプルなインターフェース**: `{テーブル名: {フィールド: 値}}` という形式でデータ操作
- **データ検証**: Pydanticモデルによる入力データの検証機能

## 実装詳細

## 1. Pydanticモデル

### Pydanticの基本スキーマ

```python
# schemas/base.py
from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# SQLAlchemyモデルの型変数
T = TypeVar('T')


class BaseSchema(BaseModel):
    """全てのスキーマの基底クラス"""
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# 入力スキーマの基底クラス (作成用)
class BaseCreateSchema(BaseSchema):
    pass


# 入力スキーマの基底クラス (更新用)
class BaseUpdateSchema(BaseSchema):
    pass


# 出力スキーマの基底クラス
class BaseReadSchema(BaseSchema):
    id: int


# 汎用的なページネーション応答スキーマ
class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


# 汎用的なCRUD操作リクエストスキーマ
class GenericCreateRequest(BaseModel):
    table_name: str
    data: Dict[str, Any]


class GenericUpdateRequest(BaseModel):
    table_name: str
    item_id: int
    data: Dict[str, Any]


class BulkCreateRequest(BaseModel):
    data: Dict[str, List[Dict[str, Any]]]


# リレーション付きCRUD操作リクエストスキーマ
class RelationalCreateRequest(BaseModel):
    main_table: str
    main_data: Dict[str, Any]
    relations: Optional[Dict[str, List[Dict[str, Any]]]] = None


class RelationalUpdateRequest(BaseModel):
    main_table: str
    main_id: int
    main_data: Optional[Dict[str, Any]] = None
    relations: Optional[Dict[str, Dict[int, Dict[str, Any]]]] = None
    new_relations: Optional[Dict[str, List[Dict[str, Any]]]] = None
```

### モデル別のPydanticスキーマ

```python
# schemas/models.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from schemas.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


# ユーザー関連スキーマ
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase, BaseCreateSchema):
    password: str


class UserUpdate(BaseModel, BaseUpdateSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserRead(UserBase, BaseReadSchema):
    pass


class UserWithRelations(UserRead):
    posts: List["PostRead"] = []
    comments: List["CommentRead"] = []


# 投稿関連スキーマ
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase, BaseCreateSchema):
    author_id: Optional[int] = None


class PostUpdate(BaseModel, BaseUpdateSchema):
    title: Optional[str] = None
    content: Optional[str] = None


class PostRead(PostBase, BaseReadSchema):
    author_id: int
    created_at: datetime


class PostWithRelations(PostRead):
    author: UserRead
    comments: List["CommentRead"] = []


# コメント関連スキーマ
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase, BaseCreateSchema):
    author_id: Optional[int] = None
    post_id: int


class CommentUpdate(BaseModel, BaseUpdateSchema):
    content: Optional[str] = None


class CommentRead(CommentBase, BaseReadSchema):
    author_id: int
    post_id: int
    created_at: datetime


class CommentWithRelations(CommentRead):
    author: UserRead
    post: PostRead


# 循環参照を解決
UserWithRelations.update_forward_refs()
PostWithRelations.update_forward_refs()
CommentWithRelations.update_forward_refs()


# Pydanticとテーブル名を紐づけるマッピング
model_schema_map = {
    # テーブル名: (create_schema, read_schema, update_schema)
    "users": (UserCreate, UserRead, UserUpdate),
    "posts": (PostCreate, PostRead, PostUpdate),
    "comments": (CommentCreate, CommentRead, CommentUpdate),
}

# リレーションを含むスキーマのマッピング
relation_schema_map = {
    "users": UserWithRelations,
    "posts": PostWithRelations,
    "comments": CommentWithRelations,
}
```

## 2. SQLAlchemyモデル

```python
# db/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # リレーション
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author_id = Column(Integer, ForeignKey("users.id"))
    
    # リレーション
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    
    # リレーション
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


# すべてのモデルをリストとして持っておく
all_models = [User, Post, Comment]
```

##
