# services/cognito_service.py
import boto3
import jwt
from typing import Optional, List
from models.form_models import UserRole

class CognitoService:
    def __init__(self, user_pool_id: str, region: str = 'us-east-1'):
        self.user_pool_id = user_pool_id
        self.region = region
        self.cognito_client = boto3.client('cognito-idp', region_name=region)
    
    async def get_user_role(self, user_id: str) -> UserRole:
        """ユーザーの役割を取得"""
        try:
            response = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=user_id
            )
            
            # ユーザーのグループを取得
            groups_response = self.cognito_client.admin_list_groups_for_user(
                UserPoolId=self.user_pool_id,
                Username=user_id
            )
            
            groups = [group['GroupName'] for group in groups_response.get('Groups', [])]
            
            # グループ名から役割を判定
            if 'admin' in groups:
                return UserRole.ADMIN
            elif 'approver' in groups:
                return UserRole.APPROVER
            else:
                return UserRole.APPLICANT
                
        except Exception as e:
            print(f"Error getting user role: {e}")
            return UserRole.APPLICANT
    
    async def verify_token(self, token: str) -> Optional[dict]:
        """JWTトークンを検証してユーザー情報を取得"""
        try:
            # 実際の実装では、Cognitoの公開鍵でトークンを検証
            # ここでは簡略化
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            print(f"Token verification error: {e}")
            return None

# database/repository.py
import asyncpg
from typing import Optional, List
from models.form_models import WorkflowApplication, WorkflowHistory, WorkflowStatus
import json
from datetime import datetime

class WorkflowRepository:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    async def get_connection(self):
        """データベース接続を取得"""
        return await asyncpg.connect(self.connection_string)
    
    async def create_application(self, application: WorkflowApplication) -> int:
        """申請を作成"""
        conn = await self.get_connection()
        try:
            query = """
                INSERT INTO workflow_applications 
                (form_data, status, applicant_id, current_approver_id, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """
            now = datetime.utcnow()
            application_id = await conn.fetchval(
                query,
                json.dumps(application.form_data.dict()),
                application.status.value,
                application.applicant_id,
                application.current_approver_id,
                now,
                now
            )
            return application_id
        finally:
            await conn.close()
    
    async def get_application(self, application_id: int) -> Optional[WorkflowApplication]:
        """申請を取得"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT id, form_data, status, applicant_id, current_approver_id, 
                       created_at, updated_at
                FROM workflow_applications
                WHERE id = $1
            """
            row = await conn.fetchrow(query, application_id)
            
            if not row:
                return None
            
            # 履歴も取得
            history = await self._get_application_history(conn, application_id)
            
            return WorkflowApplication(
                id=row['id'],
                form_data=json.loads(row['form_data']),
                status=WorkflowStatus(row['status']),
                applicant_id=row['applicant_id'],
                current_approver_id=row['current_approver_id'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                workflow_history=history
            )
        finally:
            await conn.close()
    
    async def update_application(self, application: WorkflowApplication):
        """申請を更新"""
        conn = await self.get_connection()
        try:
            query = """
                UPDATE workflow_applications
                SET form_data = $1, status = $2, current_approver_id = $3, updated_at = $4
                WHERE id = $5
            """
            await conn.execute(
                query,
                json.dumps(application.form_data.dict()),
                application.status.value,
                application.current_approver_id,
                datetime.utcnow(),
                application.id
            )
        finally:
            await conn.close()
    
    async def get_applications_by_applicant(self, applicant_id: str) -> List[WorkflowApplication]:
        """申請者による申請一覧取得"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT id, form_data, status, applicant_id, current_approver_id, 
                       created_at, updated_at
                FROM workflow_applications
                WHERE applicant_id = $1
                ORDER BY created_at DESC
            """
            rows = await conn.fetch(query, applicant_id)
            
            applications = []
            for row in rows:
                applications.append(WorkflowApplication(
                    id=row['id'],
                    form_data=json.loads(row['form_data']),
                    status=WorkflowStatus(row['status']),
                    applicant_id=row['applicant_id'],
                    current_approver_id=row['current_approver_id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    workflow_history=[]  # 一覧では履歴は含めない
                ))
            
            return applications
        finally:
            await conn.close()
    
    async def get_applications_by_status(self, status: WorkflowStatus) -> List[WorkflowApplication]:
        """ステータス別申請一覧取得"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT id, form_data, status, applicant_id, current_approver_id, 
                       created_at, updated_at
                FROM workflow_applications
                WHERE status = $1
                ORDER BY created_at DESC
            """
            rows = await conn.fetch(query, status.value)
            
            applications = []
            for row in rows:
                applications.append(WorkflowApplication(
                    id=row['id'],
                    form_data=json.loads(row['form_data']),
                    status=WorkflowStatus(row['status']),
                    applicant_id=row['applicant_id'],
                    current_approver_id=row['current_approver_id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    workflow_history=[]
                ))
            
            return applications
        finally:
            await conn.close()
    
    async def add_history(self, history: WorkflowHistory):
        """ワークフロー履歴追加"""
        conn = await self.get_connection()
        try:
            query = """
                INSERT INTO workflow_history 
                (application_id, actor_id, action, from_status, to_status, comment, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            await conn.execute(
                query,
                history.application_id,
                history.actor_id,
                history.action.value,
                history.from_status.value if history.from_status else None,
                history.to_status.value,
                history.comment,
                datetime.utcnow()
            )
        finally:
            await conn.close()
    
    async def _get_application_history(self, conn, application_id: int) -> List[WorkflowHistory]:
        """申請の履歴を取得"""
        query = """
            SELECT id, application_id, actor_id, action, from_status, to_status, 
                   comment, timestamp
            FROM workflow_history
            WHERE application_id = $1
            ORDER BY timestamp ASC
        """
        rows = await conn.fetch(query, application_id)
        
        history = []
        for row in rows:
            history.append(WorkflowHistory(
                id=row['id'],
                application_id=row['application_id'],
                actor_id=row['actor_id'],
                action=row['action'],
                from_status=WorkflowStatus(row['from_status']) if row['from_status'] else None,
                to_status=WorkflowStatus(row['to_status']),
                comment=row['comment'],
                timestamp=row['timestamp']
            ))
        
        return history

# database/migrations.sql
-- テーブル作成用SQL

-- 申請テーブル
CREATE TABLE IF NOT EXISTS workflow_applications (
    id SERIAL PRIMARY KEY,
    form_data JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    applicant_id VARCHAR(255) NOT NULL,
    current_approver_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 履歴テーブル
CREATE TABLE IF NOT EXISTS workflow_history (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES workflow_applications(id),
    actor_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    comment TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_workflow_applications_applicant_id ON workflow_applications(applicant_id);
CREATE INDEX IF NOT EXISTS idx_workflow_applications_status ON workflow_applications(status);
CREATE INDEX IF NOT EXISTS idx_workflow_applications_current_approver_id ON workflow_applications(current_approver_id);
CREATE INDEX IF NOT EXISTS idx_workflow_history_application_id ON workflow_history(application_id);

# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.cognito_service import CognitoService
from services.workflow_service import WorkflowService
from database.repository import WorkflowRepository
import os

# 設定値（環境変数から取得）
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DATABASE_URL = os.getenv("DATABASE_URL")

# セキュリティ
security = HTTPBearer()

# サービスインスタンス（シングルトン）
_cognito_service = None
_workflow_repository = None
_workflow_service = None

def get_cognito_service() -> CognitoService:
    global _cognito_service
    if _cognito_service is None:
        _cognito_service = CognitoService(USER_POOL_ID, AWS_REGION)
    return _cognito_service

def get_workflow_repository() -> WorkflowRepository:
    global _workflow_repository
    if _workflow_repository is None:
        _workflow_repository = WorkflowRepository(DATABASE_URL)
    return _workflow_repository

def get_workflow_service(
    cognito_service: CognitoService = Depends(get_cognito_service),
    repository: WorkflowRepository = Depends(get_workflow_repository)
) -> WorkflowService:
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService(cognito_service, repository)
    return _workflow_service

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cognito_service: CognitoService = Depends(get_cognito_service)
):
    """現在のユーザー情報を取得"""
    token = credentials.credentials
    user_info = await cognito_service.verify_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info
