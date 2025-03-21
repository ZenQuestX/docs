FastAPIのPydantic v2モデルで、ネストされたモデルから必要なフィールドだけをフラットに出力する方法について説明します。

Pydantic v2では、モデルの継承やフィールドの再利用を行う方法がいくつかあります。ネストされたモデルから必要なフィールドだけを抽出してフラットな形で出力するには、主に以下の方法が使えます。

from typing import Optional, List
from pydantic import BaseModel, Field, model_validator


# 元のネストされたモデル構造
class Address(BaseModel):
    street: str
    city: str
    zip_code: str
    country: str


class Contact(BaseModel):
    email: str
    phone: Optional[str] = None
    address: Address


class User(BaseModel):
    id: int
    name: str
    age: int
    contact: Contact
    tags: List[str] = []


# 方法1: モデルコンフィグでフィールド選択
class FlatUserResponse(BaseModel):
    id: int
    name: str
    email: str = Field(alias="contact.email")
    city: str = Field(alias="contact.address.city")
    country: str = Field(alias="contact.address.country")
    
    @model_validator(mode="before")
    @classmethod
    def flatten_nested_fields(cls, data):
        if isinstance(data, dict):
            return data
        
        # User型のインスタンスをフラット化
        flattened = {
            "id": data.id,
            "name": data.name,
            "contact.email": data.contact.email,
            "contact.address.city": data.contact.address.city,
            "contact.address.country": data.contact.address.country,
        }
        return flattened


# 方法2: computed_fieldを使用する方法（Pydantic v2の新機能）
from pydantic import computed_field

class ComputedFlatUser(BaseModel):
    user: User
    
    @computed_field
    @property
    def id(self) -> int:
        return self.user.id
    
    @computed_field
    @property
    def name(self) -> str:
        return self.user.name
    
    @computed_field
    @property
    def email(self) -> str:
        return self.user.contact.email
    
    @computed_field
    @property
    def city(self) -> str:
        return self.user.contact.address.city
    
    @computed_field
    @property
    def country(self) -> str:
        return self.user.contact.address.country


# 方法3: model_dumpを使用してカスタム出力を生成
class UserWithCustomOutput(User):
    def flat_output(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.contact.email,
            "city": self.contact.address.city,
            "country": self.contact.address.country
        }


# 使用例
def create_sample_user():
    return User(
        id=1,
        name="山田太郎",
        age=30,
        contact=Contact(
            email="taro@example.com",
            phone="090-1234-5678",
            address=Address(
                street="東京都渋谷区1-2-3",
                city="渋谷",
                zip_code="150-0001",
                country="日本"
            )
        ),
        tags=["vip", "developer"]
    )


# APIエンドポイントの例
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}/flat", response_model=FlatUserResponse)
def get_flat_user(user_id: int):
    user = create_sample_user()  # 実際はDBから取得するなど
    return user  # model_validatorによって自動的に変換

@app.get("/users/{user_id}/computed")
def get_computed_user(user_id: int):
    user = create_sample_user()
    return ComputedFlatUser(user=user).model_dump()

@app.get("/users/{user_id}/custom")
def get_custom_user(user_id: int):
    user = create_sample_user()
    return user.flat_output()

上記のコードでは、3つの主要なアプローチを示しています：

1. **model_validatorを使用した変換**：
   - ネストされたフィールドへのパスをaliasとして定義
   - model_validatorを使って元のモデルから必要なフィールドを取り出してフラット化

2. **computed_fieldを使用する方法**：
   - Pydantic v2の新機能であるcomputed_fieldを使用
   - 元のモデルを参照として持ち、必要なフィールドをプロパティとして公開

3. **カスタムメソッドによるフラット化**：
   - 元のモデルを拡張し、特定のフラット出力を返すメソッドを追加

実際のAPIエンドポイントでの使用例も含めています。それぞれのアプローチには利点があります：

- 方法1は、単純なマッピングに適しています
- 方法2は、元のモデルの構造を保持しながらフラット表示したい場合に有用
- 方法3は、特定のケースだけでフラット化したい場合に柔軟性があります

実際のユースケースに応じて最適な方法を選択してください。もし特定のフィールドについて詳しく知りたい場合や、他のパターンについて質問があれば、お気軽にお聞きください。
