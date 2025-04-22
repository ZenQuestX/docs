# プロンプト: SQLAlchemyで動的にフィールドを指定できる汎用的なクエリ関数の作成

SQLAlchemyでリレーションが張られた複数のデータベースモデルから、必要なフィールドだけを選択的に取得できる汎用的な関数を作成したいです。

## 要件:

1. 複数のモデル間のリレーションシップを活用できること
2. 各モデルから取得したいフィールドを動的に指定できること
3. フィルター条件を柔軟に指定できること
4. 結果を辞書のリストとして返すこと
5. N+1問題に対応できること

## モデル構造の例:

```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="comments")
```

## 使用例のイメージ:

```python
# 取得するフィールド
fields = {
    User: ['id', 'name'],
    Post: ['title'],
    Comment: ['content']
}

# 関連モデルとリレーションシップ
related_models = [(Post, User.posts), (Comment, Post.comments)]

# フィルター条件
filters = [Comment.content.contains('検索ワード'), User.name != 'Admin']

# 関数の呼び出し
results = query_related_fields(User, related_models, fields, filters)
```

返される結果は以下のようなイメージです:

```python
[
    {
        'users': {'id': 1, 'name': 'Tanaka'},
        'posts': {'title': 'SQLAlchemyについて'},
        'comments': {'content': '検索ワードを含むコメント'}
    },
    # 他の結果...
]
```

パフォーマンスを考慮した実装と、関数の使い方の詳細な説明も含めていただけると助かります。
