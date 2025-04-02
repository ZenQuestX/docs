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
models/student.py
```python
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from database import Base
from models.base import TimeStampMixin

class StudentStatus(enum.Enum):
    ACTIVE = "active"
    LEAVE = "leave"
    GRADUATED = "graduated"
    EXPELLED = "expelled"

class Student(Base, TimeStampMixin):
    """学生モデル"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), nullable=False, unique=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    enrollment_date = Column(Date, nullable=False)
    birth_date = Column(Date, nullable=True)
    gpa = Column(Float, nullable=True)
    status = Column(Enum(StudentStatus), default=StudentStatus.ACTIVE)
    is_scholarship = Column(Boolean, default=False)

    # 外部キー
    department_id = Column(Integer, ForeignKey("departments.id"))
    mentor_id = Column(Integer, ForeignKey("professors.id"), nullable=True)
    
    # リレーションシップ
    department = relationship("Department", back_populates="students")
    mentor = relationship("Professor", back_populates="mentored_students")
```
次に、Pydantic v2のモデルをschemasディレクトリに作成します：

schemas/__init__.py
```python
from schemas.department import (
    DepartmentBase, 
    DepartmentCreate, 
    DepartmentUpdate, 
    DepartmentResponse
)
from schemas.professor import (
    ProfessorBase, 
    ProfessorCreate, 
    ProfessorUpdate, 
    ProfessorResponse
)
from schemas.student import (
    StudentBase, 
    StudentCreate, 
    StudentUpdate, 
    StudentResponse
)

__all__ = [
    "DepartmentBase", "DepartmentCreate", "DepartmentUpdate", "DepartmentResponse",
    "ProfessorBase", "ProfessorCreate", "ProfessorUpdate", "ProfessorResponse",
    "StudentBase", "StudentCreate", "StudentUpdate", "StudentResponse"
]
```
schemas/department.py
```python
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict

# ベースモデル
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="学科名")
    code: str = Field(..., min_length=2, max_length=10, description="学科コード")
    description: Optional[str] = Field(None, description="学科の説明")
    foundation_date: Optional[date] = Field(None, description="設立日")
    website: Optional[HttpUrl] = Field(None, description="学科のウェブサイト")
    email: Optional[EmailStr] = Field(None, description="学科の連絡先メール")
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\-\s]{7,20}$", description="学科の電話番号")
    address: Optional[str] = Field(None, max_length=255, description="学科の住所")
    is_active: bool = Field(True, description="学科がアクティブかどうか")

# 作成用モデル
class DepartmentCreate(DepartmentBase):
    pass

# 更新用モデル（すべてのフィールドがオプショナル）
class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    description: Optional[str] = None
    foundation_date: Optional[date] = None
    website: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\-\s]{7,20}$")
    address: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

# レスポンス用モデル（IDとタイムスタンプを含む）
class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # このクラスのモデル設定
    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemy モデルからの変換を許可
        validate_assignment=True, # 代入時の検証を有効化
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "コンピュータサイエンス学科",
                "code": "CS",
                "description": "コンピュータサイエンスと情報技術に関する教育と研究を行う学科です。",
                "foundation_date": "1985-04-01",
                "website": "https://example.com/cs",
                "email": "cs@example.com",
                "phone": "+81-3-1234-5678",
                "address": "東京都新宿区○○ 1-2-3",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    )

# 関連するPydanticモデルを使用するため、教授と学生のモデルを含むリスト対応モデル
class DepartmentWithRelations(DepartmentResponse):
    professors: List["ProfessorResponse"] = []
    students: List["StudentResponse"] = []

# 循環インポートを避けるため、"ProfessorResponse"と"StudentResponse"の型アノテーションを文字列にしています
# 実際には__init__.pyでこれらの依存性を解決し、更新した型を使用します
```
schemas/professor.py
```python
from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# 学術ランクの列挙型
class AcademicRank(str, Enum):
    ASSISTANT = "assistant"
    ASSOCIATE = "associate"
    PROFESSOR = "professor"
    DISTINGUISHED = "distinguished"

# ベースモデル
class ProfessorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="名")
    last_name: str = Field(..., min_length=1, max_length=50, description="姓")
    email: EmailStr = Field(..., description="メールアドレス")
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\-\s]{7,20}$", description="電話番号")
    hire_date: date = Field(..., description="雇用日")
    birth_date: Optional[date] = Field(None, description="生年月日")
    specialization: Optional[str] = Field(None, max_length=100, description="専門分野")
    academic_rank: AcademicRank = Field(..., description="学術ランク")
    is_tenured: bool = Field(False, description="終身在職権があるかどうか")
    biography: Optional[str] = Field(None, description="経歴")
    department_id: int = Field(..., description="所属学科ID")

# 作成用モデル
class ProfessorCreate(ProfessorBase):
    pass

# 更新用モデル（すべてのフィールドがオプショナル）
class ProfessorUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\-\s]{7,20}$")
    hire_date: Optional[date] = None
    birth_date: Optional[date] = None
    specialization: Optional[str] = Field(None, max_length=100)
    academic_rank: Optional[AcademicRank] = None
    is_tenured: Optional[bool] = None
    biography: Optional[str] = None
    department_id: Optional[int] = None

# レスポンス用モデル（IDとタイムスタンプを含む）
class ProfessorResponse(ProfessorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # このクラスのモデル設定
    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemy モデルからの変換を許可
        validate_assignment=True, # 代入時の検証を有効化
        json_schema_extra={
            "example": {
                "id": 1,
                "first_name": "太郎",
                "last_name": "山田",
                "email": "taro.yamada@example.com",
                "phone": "+81-90-1234-5678",
                "hire_date": "2015-04-01",
                "birth_date": "1975-06-15",
                "specialization": "人工知能",
                "academic_rank": "professor",
                "is_tenured": True,
                "biography": "AIとマシンラーニングの研究者として10年以上の経験を持つ。",
                "department_id": 1,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    )

# 関連情報を含むモデル（学科情報と指導学生情報）
class ProfessorWithRelations(ProfessorResponse):
    department: "DepartmentResponse"
    mentored_students: List["StudentResponse"] = []

# 循環インポートを避けるため、"DepartmentResponse"と"StudentResponse"の型アノテーションを文字列にしています
```
schemas/Student.py
```python
from datetime import date, datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# 学生ステータスの列挙型
class StudentStatus(str, Enum):
    ACTIVE = "active"
    LEAVE = "leave"
    GRADUATED = "graduated"
    EXPELLED = "expelled"

# ベースモデル
class StudentBase(BaseModel):
    student_id: str = Field(..., min_length=3, max_length=20, description="学籍番号")
    first_name: str = Field(..., min_length=1, max_length=50, description="名")
    last_name: str = Field(..., min_length=1, max_length=50, description="姓")
    email: EmailStr = Field(..., description="メールアドレス")
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\-\s]{7,20}$", description="電話番号")
    enrollment_date: date = Field(..., description="入学日")
    birth_date: Optional[date] = Field(None, description="生年月日")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA (0.0-4.0)")
    status: StudentStatus = Field(StudentStatus.ACTIVE, description="学生のステータス")
    is_scholarship: bool = Field(False, description="奨学金を受けているかどうか")
    department_id: int = Field(..., description="所属学科ID")
    mentor_id: Optional[int] = Field(None, description="メンターの教授ID")

# 作成用モデル
class StudentCreate(StudentBase):
    pass

# 更新用モデル（すべてのフィールドがオプショナル）
class StudentUpdate(BaseModel):
    student_id: Optional[str] = Field(None, min_length=3, max_length=20)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\-\s]{7,20}$")
    enrollment_date: Optional[date] = None
    birth_date: Optional[date] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    status: Optional[StudentStatus] = None
    is_scholarship: Optional[bool] = None
    department_id: Optional[int] = None
    mentor_id: Optional[int] = None

# レスポンス用モデル（IDとタイムスタンプを含む）
class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # このクラスのモデル設定
    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemy モデルからの変換を許可
        validate_assignment=True, # 代入時の検証を有効化
        json_schema_extra={
            "example": {
                "id": 1,
                "student_id": "CS2020001",
                "first_name": "花子",
                "last_name": "佐藤",
                "email": "hanako.sato@example.com",
                "phone": "+81-80-1234-5678",
                "enrollment_date": "2020-04-01",
                "birth_date": "2001-11-23",
                "gpa": 3.8,
                "status": "active",
                "is_scholarship": True,
                "department_id": 1,
                "mentor_id": 1,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    )

# 関連情報を含むモデル（学科情報とメンター情報）
class StudentWithRelations(StudentResponse):
    department: "DepartmentResponse"
    mentor: Optional["ProfessorResponse"] = None

# 循環インポートを避けるため、"DepartmentResponse"と"ProfessorResponse"の型アノテーションを文字列にしています
```

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
