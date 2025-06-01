# BSS-FormFlow統合ワークフロー 4営業日実装ガイド

## 📅 実装スケジュール

### Day 1: 基盤セットアップ
**所要時間: 6-8時間**

#### 午前 (3-4時間)
- [ ] プロジェクト構造作成
- [ ] 依存関係インストール (`pip install -r requirements.txt`)
- [ ] PostgreSQL環境準備
- [ ] 環境変数設定 (`.env`ファイル)
- [ ] データベーススキーマ作成

```bash
# セットアップコマンド
git clone <your-repo>
cd workflow-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_setup.py
```

#### 午後 (3-4時間)
- [ ] Cognitoユーザープール設定
- [ ] テストユーザー作成 (申請者、承認者、管理者)
- [ ] 基本API動作確認
- [ ] ヘルスチェック・スキーマ取得テスト

### Day 2: コアワークフロー実装
**所要時間: 6-8時間**

#### 午前 (3-4時間)
- [ ] `WorkflowService` 実装・テスト
- [ ] `CognitoService` 実装・テスト
- [ ] データベースリポジトリ実装

#### 午後 (3-4時間)
- [ ] 申請作成API実装・テスト
- [ ] ワークフローアクションAPI実装・テスト
- [ ] 権限制御ロジック実装・テスト

### Day 3: API完成・統合テスト
**所要時間: 6-8時間**

#### 午前 (3-4時間)
- [ ] 申請一覧API実装
- [ ] フォームスキーマ動的生成
- [ ] エラーハンドリング強化

#### 午後 (3-4時間)
- [ ] 完全ワークフローテスト実行
- [ ] API仕様書確認・調整
- [ ] フロントエンド連携準備

### Day 4: 最終調整・デプロイ準備
**所要時間: 4-6時間**

#### 午前 (2-3時間)
- [ ] パフォーマンス最適化
- [ ] セキュリティチェック
- [ ] ログ・監視設定

#### 午後 (2-3時間)
- [ ] フロントエンド連携テスト
- [ ] ドキュメント整備
- [ ] デプロイ・本番確認

## 🛠️ 技術実装詳細

### 1. 環境セットアップ

```bash
# 1. プロジェクト初期化
mkdir bss-formflow-workflow
cd bss-formflow-workflow

# 2. 仮想環境作成
python -m venv venv
source venv/bin/activate

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. データベース準備
docker-compose up -d postgres
python run_setup.py
```

### 2. Cognito設定

#### 必要なグループ作成
- `applicant` - 申請者グループ
- `approver` - 承認者グループ  
- `admin` - 管理者グループ

#### テストユーザー例
```
test-applicant@example.com (applicant グループ)
test-approver@example.com (approver グループ)
test-admin@example.com (admin グループ)
```

### 3. API起動・テスト

```bash
# サーバー起動
python main.py

# 別ターミナルでテスト実行
python test_api.py

# cURLでのテスト
chmod +x curl_examples.sh
./curl_examples.sh
```

## 🎯 重要な実装ポイント

### BSS-FormFlow統合のコア機能

1. **型安全性の確保**
   - PydanticモデルからJSON Schema自動生成
   - フロントエンドとの型共有

2. **権限ベースUI制御**
   - ユーザー役割に応じたフォーム制御
   - 実行可能アクション動的生成

3. **ワークフロー状態管理**
   - ステータス遷移の制御
   - 履歴追跡

4. **セキュリティ**
   - JWT認証
   - 権限チェック（クライアント・サーバー両方）

### 簡略化された部分（本格運用では要改善）

1. **JWT検証**: シンプルな実装（本番では公開鍵検証必要）
2. **承認者割り当て**: 固定ロジック（本番では動的割り当て）
3. **エラーハンドリング**: 基本的な実装
4. **ログ・監視**: 最小限

## 📊 API動作フロー例

### 完全なワークフロー実行例

```
1. 申請者: 新規申請作成 (draft)
   POST /workflow/applications
   
2. 申請者: 申請提出 (draft → pending)
   POST /workflow/applications/{id}/actions
   {"action": "submit"}
   
3. 承認者: 所属承認 (pending → department_approved)
   POST /workflow/applications/{id}/actions
   {"action": "approve"}
   
4. 管理者: 最終承認 (department_approved → registered)
   POST /workflow/applications/{id}/actions
   {"action": "approve"}
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

1. **データベース接続エラー**
   ```bash
   # PostgreSQLが起動しているか確認
   docker-compose ps
   # 接続文字列確認
   echo $DATABASE_URL
   ```

2. **Cognito認証エラー**
   ```bash
   # 環境変数確認
   echo $COGNITO_USER_POOL_ID
   # ユーザープールID・リージョン確認
   ```

3. **API 404エラー**
   ```bash
   # ルーター登録確認
   # app.include_router(workflow_router)
   ```

## 📈 次の改善ステップ（5営業日目以降）

1. **セキュリティ強化**
   - 本格的なJWT検証
   - レート制限
   - 入力値サニタイゼーション

2. **パフォーマンス最適化**
   - データベースインデックス最適化
   - キャッシュ機能
   - 非同期処理改善

3. **機能拡張**
   - 通知機能
   - ファイル添付
   - 承認ルート設定

4. **運用機能**
   - ログ管理
   - 監視・アラート
   - バックアップ

## ✅ 完了チェックリスト

### Day 1
- [ ] 開発環境構築完了
- [ ] データベース接続確認
- [ ] Cognito設定完了

### Day 2  
- [ ] 基本API実装完了
- [ ] 単体テスト通過

### Day 3
- [ ] 統合テスト通過
- [ ] 完全ワークフロー動作確認

### Day 4
- [X] フロントエンド連携準備完了
- [ ] ドキュメント整備
- [ ] 本番デプロイ準備

## 🚀 起動コマンド要約

```bash
# 開発環境起動
docker-compose up -d
python main.py

# テスト実行
python test_api.py

# API仕様確認
open http://localhost:8000/docs
```

この実装により、4営業日で**申請者→承認者→管理者**のワークフローが動作するBSS-FormFlow統合バックエ
