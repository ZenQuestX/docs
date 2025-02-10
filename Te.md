from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel, Field

# SQLAlchemy モデル
class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(50))
    email_address: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

# Pydantic モデル（エイリアス使用）
class UserSchema(BaseModel):
    id: int
    name: str = Field(validation_alias="user_name")  # user_name → name
    email: str = Field(validation_alias="email_address")  # email_address → email
    created: datetime = Field(validation_alias="created_at")  # created_at → created
    updated: Optional[datetime] = Field(validation_alias="updated_at")  # updated_at → updated
    
    class Config:
        from_attributes = True  # SQLAlchemy モデルからの変換を有効化

# 使用例
def convert_orm_to_pydantic(user_orm: UserORM) -> UserSchema:
    return UserSchema.model_validate(user_orm)

# 使用例
if __name__ == "__main__":
    # ORMオブジェクトの作成例
    user = UserORM(
        id=1,
        user_name="yamada_taro",
        email_address="yamada@example.com",
        created_at=datetime.now(),
        updated_at=None
    )
    
    # Pydanticモデルに変換
    user_schema = convert_orm_to_pydantic(user)
    print(user_schema.model_dump())
