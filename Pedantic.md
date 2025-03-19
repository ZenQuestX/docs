わかりました。SQLAlchemyのクエリの結果はデータベースから正しく取得できているのに、Pydanticモデルに変換するとテーブルCの内容だけがNoneになる問題ですね。

この問題の解決策としては、以下のポイントを確認してみてください：

### 1. Pydanticモデルの定義を確認する

Pydantic v2では、モデル定義の方法が少し変わっています。特に注意すべき点は：

```python
# schemas/table_c.py
from pydantic import BaseModel, Field

class TableCModel(BaseModel):
    id: int
    name: str
    
    model_config = {
        "from_attributes": True  # v2では Config クラスではなく model_config を使用
    }

# schemas/table_b.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .table_c import TableCModel

class TableBModel(BaseModel):
    id: int
    name: str
    table_c: Optional[List[TableCModel]] = None
    
    model_config = {
        "from_attributes": True
    }
```

### 2. モデル変換の方法を確認する

Pydantic v2では、`from_orm`は非推奨となり、代わりに`model_validate`を使います：

```python
# 正しい変換方法（v2）
result = session.query(TableA).options(
    joinedload(TableA.table_b).joinedload(TableB.table_c)
).first()

if result:
    # 明示的に from_attributes=True を指定する
    model = TableAModel.model_validate(result, from_attributes=True)
    print(model.model_dump_json())  # json() ではなく model_dump_json() を使用
```

### 3. リレーションの属性名を確認する

SQLAlchemyとPydanticのモデルで、リレーションの属性名が一致していることを確認してください：

```python
# SQLAlchemy
class TableB(Base):
    # ...
    table_c = relationship("TableC", back_populates="table_b")

# Pydantic
class TableBModel(BaseModel):
    # ...
    table_c: Optional[List[TableCModel]] = None  # 属性名が同じか確認
```

### 4. デバッグ用のコードを追加する

変換前後のデータを確認するコードを追加してみましょう：

```python
# デバッグコード
result = session.query(TableA).options(
    joinedload(TableA.table_b).joinedload(TableB.table_c)
).first()

if result:
    # SQLAlchemyのデータ構造を確認
    print("SQLAlchemy Result:")
    print(f"TableA: {result.id}")
    for b in result.table_b:
        print(f"  TableB: {b.id}")
        print(f"    TableC: {[c.id for c in b.table_c]}")
    
    # Pydanticへの変換を試みる
    model = TableAModel.model_validate(result, from_attributes=True)
    
    # Pydanticのデータ構造を確認
    print("\nPydantic Result:")
    print(f"TableA: {model.id}")
    for b in model.table_b:
        print(f"  TableB: {b.id}")
        print(f"    TableC: {b.table_c}")  # これがNoneになっている
```

### 5. アトリビュート名の不一致を確認する

テーブルBからテーブルCへのリレーションの属性名が、SQLAlchemyとPydanticで一致していることを確認してください。特に、複数形/単数形の違いなどに注意してください。

```python
# SQLAlchemy
table_c = relationship("TableC", back_populates="table_b")

# Pydantic
table_c: Optional[List[TableCModel]] = None  # 属性名が同じことを確認
```

これらの点を確認しても問題が解決しない場合は、実際のコードの一部を共有していただけると、より具体的なアドバイスができます。
