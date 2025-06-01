# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.workflow_api import router as workflow_router
from models.form_models import ApplicationFormData
import uvicorn

# FastAPIアプリケーション作成
app = FastAPI(
    title="BSS-FormFlow Workflow API",
    description="ワークフロー管理システム with BSS-FormFlow",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Reactアプリのドメイン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーター登録
app.include_router(workflow_router)

# ヘルスチェック
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "workflow-api"}

# JSON Schema公開エンドポイント
@app.get("/api/schema/application-form")
async def get_application_form_schema():
    """申請フォームのJSON Schemaを公開"""
    return ApplicationFormData.model_json_schema()

# OpenAPI仕様書のカスタマイズ
@app.get("/openapi.json")
async def custom_openapi():
    """カスタムOpenAPI仕様書"""
    return app.openapi()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
