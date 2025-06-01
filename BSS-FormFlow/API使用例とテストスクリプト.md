# test_api.py
"""
APIテスト用スクリプト
実際のAPIの動作確認に使用
"""
import requests
import json

# API基本設定
API_BASE_URL = "http://localhost:8000"

# サンプルJWTトークン（テスト用 - 実際は Cognito から取得）
SAMPLE_TOKEN_APPLICANT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LWFwcGxpY2FudCIsImdyb3VwcyI6WyJhcHBsaWNhbnQiXX0.test"
SAMPLE_TOKEN_APPROVER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LWFwcHJvdmVyIiwiZ3JvdXBzIjpbImFwcHJvdmVyIl19.test"
SAMPLE_TOKEN_ADMIN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LWFkbWluIiwiZ3JvdXBzIjpbImFkbWluIl19.test"

def get_headers(token):
    """認証ヘッダー生成"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_health_check():
    """ヘルスチェック"""
    print("🔍 ヘルスチェック")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_schema():
    """スキーマ取得テスト"""
    print("🔍 フォームスキーマ取得")
    response = requests.get(f"{API_BASE_URL}/api/schema/application-form")
    print(f"Status: {response.status_code}")
    print(f"Schema keys: {list(response.json().keys())}")
    print()

def test_create_application():
    """申請作成テスト"""
    print("🔍 新規申請作成 (申請者)")
    
    form_data = {
        "applicant_name": "テスト太郎",
        "department": "開発部",
        "email": "test@example.com",
        "phone": "09012345678",
        "application_type": "システム利用申請",
        "reason": "新しいワークフローシステムの利用申請です。業務効率化のために必要です。"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/workflow/applications",
        headers=get_headers(SAMPLE_TOKEN_APPLICANT),
        json=form_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Application ID: {data['application']['id']}")
        print(f"Status: {data['application']['status']}")
        print(f"Available actions: {data['available_actions']}")
        return data['application']['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_submit_application(app_id):
    """申請提出テスト"""
    print(f"🔍 申請提出 (申請者) - ID: {app_id}")
    
    action_data = {
        "action": "submit",
        "comment": "申請を提出します"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/workflow/applications/{app_id}/actions",
        headers=get_headers(SAMPLE_TOKEN_APPLICANT),
        json=action_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"New Status: {data['application']['status']}")
        print(f"Available actions: {data['available_actions']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_approve_by_approver(app_id):
    """承認者による承認テスト"""
    print(f"🔍 承認者による承認 - ID: {app_id}")
    
    action_data = {
        "action": "approve",
        "comment": "所属部署として承認します"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/workflow/applications/{app_id}/actions",
        headers=get_headers(SAMPLE_TOKEN_APPROVER),
        json=action_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"New Status: {data['application']['status']}")
        print(f"Available actions: {data['available_actions']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_approve_by_admin(app_id):
    """管理者による最終承認テスト"""
    print(f"🔍 管理者による最終承認 - ID: {app_id}")
    
    action_data = {
        "action": "approve",
        "comment": "最終承認しました。登録完了です。"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/workflow/applications/{app_id}/actions",
        headers=get_headers(SAMPLE_TOKEN_ADMIN),
        json=action_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Final Status: {data['application']['status']}")
        print(f"Available actions: {data['available_actions']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_applications_list():
    """申請一覧取得テスト"""
    print("🔍 申請一覧取得")
    
    # 申請者として一覧取得
    print("申請者として:")
    response = requests.get(
        f"{API_BASE_URL}/workflow/applications",
        headers=get_headers(SAMPLE_TOKEN_APPLICANT)
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        applications = response.json()
        print(f"申請数: {len(applications)}")
    
    # 承認者として一覧取得
    print("承認者として:")
    response = requests.get(
        f"{API_BASE_URL}/workflow/applications",
        headers=get_headers(SAMPLE_TOKEN_APPROVER)
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        applications = response.json()
        print(f"承認待ち申請数: {len(applications)}")
    
    print()

def run_complete_workflow_test():
    """完全なワークフローテスト"""
    print("🚀 完全ワークフローテスト開始\n")
    
    # 1. ヘルスチェック
    test_health_check()
    
    # 2. スキーマ取得
    test_get_schema()
    
    # 3. 申請作成
    app_id = test_create_application()
    if not app_id:
        print("❌ 申請作成に失敗")
        return
    
    print()
    
    # 4. 申請提出
    test_submit_application(app_id)
    
    # 5. 承認者による承認
    test_approve_by_approver(app_id)
    
    # 6. 管理者による最終承認
    test_approve_by_admin(app_id)
    
    # 7. 申請一覧確認
    test_get_applications_list()
    
    print("✅ 完全ワークフローテスト完了")

if __name__ == "__main__":
    run_complete_workflow_test()

# curl_examples.sh
#!/bin/bash
# cURLを使用したAPIテスト例

API_BASE="http://localhost:8000"
APPLICANT_TOKEN="your_applicant_jwt_token"
APPROVER_TOKEN="your_approver_jwt_token"
ADMIN_TOKEN="your_admin_jwt_token"

echo "=== BSS-FormFlow Workflow API テスト ==="

# 1. ヘルスチェック
echo "1. ヘルスチェック"
curl -X GET "$API_BASE/health" | jq .
echo ""

# 2. フォームスキーマ取得
echo "2. フォームスキーマ取得"
curl -X GET "$API_BASE/api/schema/application-form" | jq .properties
echo ""

# 3. 新規申請作成
echo "3. 新規申請作成"
curl -X POST "$API_BASE/workflow/applications" \
  -H "Authorization: Bearer $APPLICANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "テスト太郎",
    "department": "開発部",
    "email": "test@example.com",
    "phone": "09012345678",
    "application_type": "システム利用申請",
    "reason": "新しいワークフローシステムの利用申請です。"
  }' | jq .
echo ""

# 4. 申請提出
echo "4. 申請提出"
curl -X POST "$API_BASE/workflow/applications/1/actions" \
  -H "Authorization: Bearer $APPLICANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "submit",
    "comment": "申請を提出します"
  }' | jq .
echo ""

# 5. 承認者による承認
echo "5. 承認者による承認"
curl -X POST "$API_BASE/workflow/applications/1/actions" \
  -H "Authorization: Bearer $APPROVER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "comment": "所属部署として承認します"
  }' | jq .
echo ""

# 6. 管理者による最終承認
echo "6. 管理者による最終承認"
curl -X POST "$API_BASE/workflow/applications/1/actions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "comment": "最終承認しました"
  }' | jq .
echo ""

# 7. 申請一覧取得
echo "7. 申請一覧取得"
curl -X GET "$API_BASE/workflow/applications" \
  -H "Authorization: Bearer $APPLICANT_TOKEN" | jq .
echo ""
