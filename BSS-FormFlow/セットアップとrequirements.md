# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
asyncpg==0.29.0
boto3==1.34.0
PyJWT==2.8.0
python-multipart==0.0.6
python-dotenv==1.0.0

# .env (環境変数設定ファイル)
# Cognito設定
COGNITO_USER_POOL_ID=your_user_pool_id
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# データベース設定
DATABASE_URL=postgresql://username:password@localhost:5432/workflow_db

# アプリケーション設定
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# docker-compose.yml (開発環境用)
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: workflow_db
      POSTGRES_USER: workflow_user
      POSTGRES_PASSWORD: workflow_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations.sql:/docker-entrypoint-initdb.d/init.sql

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://workflow_user:workflow_pass@postgres:5432/workflow_db
      - COGNITO_USER_POOL_ID=${COGNITO_USER_POOL_ID}
      - AWS_REGION=${AWS_REGION}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - postgres
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:

# run_setup.py
"""
セットアップスクリプト
開発環境の初期化を行います
"""
import asyncio
import os
import asyncpg
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

async def setup_database():
    """データベースセットアップ"""
    database_url = os.getenv("DATABASE_URL")
    
    try:
        # データベース接続
        conn = await asyncpg.connect(database_url)
        
        # マイグレーション実行
        with open("database/migrations.sql", "r") as f:
            migration_sql = f.read()
        
        await conn.execute(migration_sql)
        print("✅ データベースマイグレーション完了")
        
        # サンプルデータ挿入（オプション）
        await insert_sample_data(conn)
        
        await conn.close()
        print("✅ データベースセットアップ完了")
        
    except Exception as e:
        print(f"❌ データベースセットアップエラー: {e}")

async def insert_sample_data(conn):
    """サンプルデータ挿入"""
    # 実際の運用では不要だが、開発・テスト用に
    sample_form_data = {
        "applicant_name": "山田太郎",
        "department": "開発部",
        "email": "yamada@example.com",
        "phone": "09012345678",
        "application_type": "新規システム申請",
        "reason": "業務効率化のため新しいワークフローシステムを導入したいです。"
    }
    
    # サンプル申請作成
    query = """
        INSERT INTO workflow_applications 
        (form_data, status, applicant_id)
        VALUES ($1, $2, $3)
        RETURNING id
    """
    
    import json
    app_id = await conn.fetchval(
        query,
        json.dumps(sample_form_data),
        'draft',
        'sample-user-123'
    )
    
    # サンプル履歴
    history_query = """
        INSERT INTO workflow_history 
        (application_id, actor_id, action, to_status, comment)
        VALUES ($1, $2, $3, $4, $5)
    """
    
    await conn.execute(
        history_query,
        app_id,
        'sample-user-123',
        'save_draft',
        'draft',
        'サンプル申請作成'
    )
    
    print("✅ サンプルデータ挿入完了")

def create_cognito_groups():
    """Cognitoグループ作成のガイド"""
    print("""
📋 Cognitoグループ設定手順:
1. AWS Cognitoコンソールにログイン
2. ユーザープールを選択
3. 「グループ」タブから以下のグループを作成:
   - applicant (申請者)
   - approver (承認者)  
   - admin (管理者)
4. テストユーザーを各グループに割り当て

サンプルユーザー設定例:
- test-applicant@example.com → applicant グループ
- test-approver@example.com → approver グループ
- test-admin@example.com → admin グループ
    """)

if __name__ == "__main__":
    print("🚀 BSS-FormFlow Workflow セットアップ開始")
    
    # データベースセットアップ
    asyncio.run(setup_database())
    
    # Cognito設定ガイド表示
    create_cognito_groups()
    
    print("""
✅ セットアップ完了！

🚀 起動方法:
1. 環境変数設定: .envファイルを編集
2. サーバー起動: python main.py
3. API確認: http://localhost:8000/docs

📝 次のステップ:
1. Cognitoグループ設定
2. フロントエンド側の実装
3. 実際のフロー動作確認
    """)

# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポート公開
EXPOSE 8000

# アプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
