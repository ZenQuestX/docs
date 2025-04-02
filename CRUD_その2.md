Pydantic v2とSQLAlchemyを使って学科、教授、学生の3つのテーブルをリレーションありで実装します。

```
├── models
│   ├── __init__.py
│   ├── base.py
│   ├── department.py
│   ├── professor.py
│   └── student.py
├── schemas
│   ├── __init__.py
│   ├── department.py
│   ├── professor.py
│   └── student.py
└── database.py
```

まず基本となるモデルを作成しましょう：

database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベース接続URLを設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./university.db"
# PostgreSQLの場合は以下のような形式になります
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# SQLAlchemyエンジンを作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# セッションファクトリを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルの基底クラスを作成
Base = declarative_base()

# データベースセッションを取得する依存関係を定義
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
次に、SQLAlchemyのORM定義をmodelsディレクトリに作成します：

models/base.py
```python
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from database import Base

class TimeStampMixin:
    """全てのモデルに適用されるタイムスタンプを持つMixin"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```
models/__init__.py
```python
from models.department import Department
from models.professor import Professor
from models.student import Student

__all__ = ["Department", "Professor", "Student"]
```
models/department.py
```python
from sqlalchemy import Column, Integer, String, Boolean, Date, Text
from sqlalchemy.orm import relationship
from database import Base
from models.base import TimeStampMixin

class Department(Base, TimeStampMixin):
    """学科モデル"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(10), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    foundation_date = Column(Date, nullable=True)
    website = Column(String(255), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # リレーションシップ
    professors = relationship("Professor", back_populates="department")
    students = relationship("Student", back_populates="department")
```
models/professor.py
```python
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from database import Base
from models.base import TimeStampMixin

class AcademicRank(enum.Enum):
    ASSISTANT = "assistant"
    ASSOCIATE = "associate"
    PROFESSOR = "professor"
    DISTINGUISHED = "distinguished"

class Professor(Base, TimeStampMixin):
    """教授モデル"""
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    hire_date = Column(Date, nullable=False)
    birth_date = Column(Date, nullable=True)
    specialization = Column(String(100), nullable=True)
    academic_rank = Column(Enum(AcademicRank), nullable=False)
    is_tenured = Column(Boolean, default=False)
    biography = Column(Text, nullable=True)

    # 外部キー
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # リレーションシップ
    department = relationship("Department", back_populates="professors")
    mentored_students = relationship("Student", back_populates="mentor")
```













次に、Pydantic v2のモデルをschemasディレクトリに作成します：



















以上でPydantic v2を使用した3つのテーブル（学科・教授・学生）のモデル定義が完成しました。各モデルについての説明をします：

### プロジェクト構造
- `models/`: SQLAlchemy ORMモデルを格納
- `schemas/`: Pydantic v2モデルを格納
- `database.py`: データベース接続の設定

### SQLAlchemy ORMモデル

1. **Department（学科）モデル**
   - 基本的な学科情報（名前、コード、説明など）
   - 教授と学生へのリレーションシップ定義

2. **Professor（教授）モデル**
   - 個人情報（名前、メール、電話番号など）
   - 学術的な情報（ランク、専門分野など）
   - 学科へのリレーションと学生へのメンターシップ関係

3. **Student（学生）モデル**
   - 個人情報（学籍番号、名前、メールなど）
   - 学業情報（GPA、状態など）
   - 学科とメンター教授へのリレーション

### Pydantic v2モデル

各エンティティ（学科・教授・学生）に対して複数のPydanticモデルを作成：

1. **BaseModel**: 基本フィールドとバリデーション
2. **CreateModel**: 作成時に使用
3. **UpdateModel**: 更新時に使用（全てのフィールドがオプション）
4. **ResponseModel**: レスポンス用（ID、タイムスタンプを含む）
5. **WithRelationsModel**: リレーションシップデータを含むモデル

### 主な特徴

1. **Pydantic v2の新機能**
   - `ConfigDict`を使用したモデル設定
   - `model_config`の使用
   - バリデーション強化

2. **SQLAlchemyとの互換性**
   - `from_attributes=True`設定で、ORMモデルからの変換をサポート

3. **リレーションシップ**
   - 3テーブル間のリレーションをORM側とPydantic側で定義
   - 前方参照問題を文字列型アノテーションで解決

4. **バリデーション**
   - フィールドにバリデーションルールを適用
   - 電話番号、メールアドレス、GPA値など

5. **タイムスタンプ**
   - 全モデルに作成日時と更新日時を自動設定

このプロジェクトをベースに、FastAPIなどのAPIフレームワークと連携して実際のアプリケーションを構築できます。必要に応じて、モデルの調整や追加機能の実装が可能です。
