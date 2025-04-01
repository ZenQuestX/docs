# SQLAlchemyとFastAPIのための汎用CRUD操作

このリポジトリでは、SQLAlchemyとFastAPIを使用した多数のテーブル構成のデータベースに対して、シンプルかつ効率的にCRUD操作を行うための汎用的な実装を提供しています。

## 特徴

- **汎用CRUD操作**: テーブル名を指定するだけで任意のテーブルに対して操作可能
- **一括操作**: 複数テーブルへの同時処理をサポート
- **リレーション対応**: 親子関係のあるデータを一度に作成・更新可能
- **既存モデルの活用**: SQLAlchemyの既存モデル定義をそのまま利用
- **シンプルなインターフェース**: `{テーブル名: {フィールド: 値}}` という形式でデータ操作

## 実装詳細

### CRUDベースクラス

```python
# db/crud.py
from typing import Any, Dict, List, Type, TypeVar, Union, Optional
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase:
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

    def create(self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        新規レコード作成
        """
        obj_in_data = jsonable_encoder(obj_in) if isinstance(obj_in, BaseModel) else obj_in
        db_obj = self.model(**obj_in_data)  # type: ignore
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
```

### 汎用CRUD操作

```python
# リレーションを考慮したgeneric CRUD操作
class GenericCRUD:
    @staticmethod
    def get_model_by_name(table_name: str) -> Type[ModelType]:
        """テーブル名からモデルクラスを取得する"""
        # ここで、すべてのモデルをインポートして名前で検索する実装が必要
        # 例:
        from db.models import all_models
        for model in all_models:
            if model.__tablename__ == table_name:
                return model
        raise ValueError(f"Model with table name '{table_name}' not found")

    @staticmethod
    def create_item(db: Session, table_name: str, item_data: Dict[str, Any]) -> Any:
        """
        テーブル名とデータからレコードを作成する汎用メソッド
        """
        model = GenericCRUD.get_model_by_name(table_name)
        db_item = model(**item_data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def update_item(db: Session, table_name: str, item_id: int, item_data: Dict[str, Any]) -> Any:
        """
        テーブル名、ID、データからレコードを更新する汎用メソッド
        """
        model = GenericCRUD.get_model_by_name(table_name)
        db_item = db.query(model).filter(model.id == item_id).first()
        if not db_item:
            return None
        
        # 更新可能なカラムを取得
        columns = inspect(model).columns.keys()
        
        # 存在するカラムのみ更新
        for field, value in item_data.items():
            if field in columns:
                setattr(db_item, field, value)
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def bulk_create(
        db: Session, 
        table_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[Any]]:
        """
        複数テーブルに対して一括でデータを作成する
        table_data: {"table_name": [{"field": "value"}, ...], ...}
        """
        results = {}
        
        for table_name, items in table_data.items():
            model = GenericCRUD.get_model_by_name(table_name)
            created_items = []
            
            for item_data in items:
                db_item = model(**item_data)
                db.add(db_item)
                created_items.append(db_item)
            
            results[table_name] = created_items
        
        db.commit()
        
        # refresh all objects
        for items in results.values():
            for item in items:
                db.refresh(item)
                
        return results

    @staticmethod
    def bulk_update(
        db: Session, 
        table_data: Dict[str, Dict[int, Dict[str, Any]]]
    ) -> Dict[str, List[Any]]:
        """
        複数テーブルに対して一括でデータを更新する
        table_data: {"table_name": {id: {"field": "value"}, ...}, ...}
        """
        results = {}
        
        for table_name, id_data_map in table_data.items():
            model = GenericCRUD.get_model_by_name(table_name)
            updated_items = []
            
            for item_id, item_data in id_data_map.items():
                db_item = db.query(model).filter(model.id == item_id).first()
                if db_item:
                    # 更新可能なカラムを取得
                    columns = inspect(model).columns.keys()
                    
                    # 存在するカラムのみ更新
                    for field, value in item_data.items():
                        if field in columns:
                            setattr(db_item, field, value)
                    
                    db.add(db_item)
                    updated_items.append(db_item)
            
            results[table_name] = updated_items
        
        db.commit()
        
        # refresh all objects
        for items in results.values():
            for item in items:
                db.refresh(item)
                
        return results
```

### リレーションを考慮したCRUD操作

```python
# リレーションを考慮した高度なCRUD操作
class RelationalCRUD(GenericCRUD):
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
        # メインレコード作成
        main_model = GenericCRUD.get_model_by_name(main_table)
        main_obj = main_model(**main_data)
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
                    relation_obj = relation_model(**relation_data)
                    db.add(relation_obj)
        
        db.commit()
        db.refresh(main_obj)
        return main_obj

    @staticmethod
    def update_with_relations(
        db: Session,
        main_table: str,
        main_id: int,
        main_data: Dict[str, Any] = None,
        relations: Dict[str, Dict[int, Dict[str, Any]]] = None,
        new_relations: Dict[str, List[Dict[str, Any]]] = None
    ) -> Any:
        """
        メインテーブルとリレーション先のデータを一括で更新
        
        :param main_table: メインテーブル名
        :param main_id: メインレコードのID
        :param main_data: メインテーブルの更新データ
        :param relations: {"relation_name": {id: {"field": "value"}, ...}, ...}
        :param new_relations: {"relation_name": [{"field": "value"}, ...], ...}
        """
        # メインレコード取得
        main_model = GenericCRUD.get_model_by_name(main_table)
        main_obj = db.query(main_model).filter(main_model.id == main_id).first()
        if not main_obj:
            return None
        
        # メインレコード更新
        if main_data:
            columns = inspect(main_model).columns.keys()
            for field, value in main_data.items():
                if field in columns:
                    setattr(main_obj, field, value)
        
        # 既存リレーション先レコード更新
        if relations:
            for relation_name, relation_data_map in relations.items():
                relation_attr = getattr(main_model, relation_name, None)
                if relation_attr is None:
                    continue
                
                relation_model = relation_attr.property.mapper.class_
                
                for relation_id, relation_data in relation_data_map.items():
                    relation_obj = db.query(relation_model).filter(relation_model.id == relation_id).first()
                    if relation_obj:
                        columns = inspect(relation_model).columns.keys()
                        for field, value in relation_data.items():
                            if field in columns:
                                setattr(relation_obj, field, value)
                        db.add(relation_obj)
        
        # 新規リレーション先レコード作成
        if new_relations:
            for relation_name, relation_data_list in new_relations.items():
                relation_attr = getattr(main_model, relation_name, None)
                if relation_attr is None:
                    continue
                
                relation_model = relation_attr.property.mapper.class_
                
                # 外部キー名を取得
                foreign_key = None
                for local_col, remote_col in relation_attr.property.local_remote_pairs:
                    if local_col.name == 'id':
                        foreign_key = remote_col.name
                
                if not foreign_key:
                    continue
                
                for relation_data in relation_data_list:
                    relation_data[foreign_key] = main_obj.id
                    relation_obj = relation_model(**relation_data)
                    db.add(relation_obj)
        
        db.commit()
        db.refresh(main_obj)
        return main_obj
```

## FastAPI エンドポイント例

```python
# api/endpoints/generic.py
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.crud import GenericCRUD, RelationalCRUD
from db.database import get_db

router = APIRouter()


@router.post("/{table_name}/")
def create_item(
    table_name: str, 
    item_data: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    """
    どのテーブルに対しても汎用的にレコードを作成できるエンドポイント
    """
    try:
        result = GenericCRUD.create_item(db, table_name, item_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{table_name}/{item_id}")
def update_item(
    table_name: str, 
    item_id: int, 
    item_data: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    """
    どのテーブルに対しても汎用的にレコードを更新できるエンドポイント
    """
    try:
        result = GenericCRUD.update_item(db, table_name, item_id, item_data)
        if not result:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/create/")
def bulk_create(
    table_data: Dict[str, List[Dict[str, Any]]],
    db: Session = Depends(get_db)
):
    """
    複数テーブルに対して一括でデータを作成するエンドポイント
    """
    try:
        results = GenericCRUD.bulk_create(db, table_data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relational/create/")
def create_with_relations(
    main_table: str,
    main_data: Dict[str, Any],
    relations: Dict[str, List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
):
    """
    メインテーブルとリレーション先のデータを一括で作成するエンドポイント
    """
    try:
        result = RelationalCRUD.create_with_relations(db, main_table, main_data, relations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## モデル定義例

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

## 使用例

### リレーションを持つデータの作成

```json
// POST /api/generic/relational/create/
{
  "main_table": "users",
  "main_data": {
    "username": "testuser",
    "email": "test@example.com",
    "hashed_password": "hashedpassword123"
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

### 複数テーブルへの一括作成

```json
// POST /api/generic/bulk/create/
{
  "users": [
    {
      "username": "user1",
      "email": "user1@example.com",
      "hashed_password": "password1"
    },
    {
      "username": "user2",
      "email": "user2@example.com",
      "hashed_password": "password2"
    }
  ],
  "posts": [
    {
      "title": "Post 1",
      "content": "Content 1",
      "author_id": 1
    }
  ]
}
```

## 注意事項

- `get_model_by_name`メソッドはプロジェクトの構造に合わせて調整が必要です
- 本番環境では、セキュリティ上の理由から許可するテーブルやフィールドを制限することをお勧めします
- このコードはSQLAlchemyのリレーションシップを最大限に活用するため、モデル間のリレーションが適切に定義されている必要があります

## ライセンス

MIT
