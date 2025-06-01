# 権限管理のベストプラクティス DB設計例（BSS-FormFlow前提）

| テーブル名               | 主なカラム（属性）                                                                      | 概要・備考                    |
| ------------------- | ------------------------------------------------------------------------------ | ------------------------ |
| **Users**           | `user_id (PK)`, `username`, `email`, `cognito_sub`                             | ユーザー情報。Cognitoのサブ（ID）と連携 |
| **Applications**    | `app_id (PK)`, `app_name`, `description`                                       | 管理対象アプリ（フォームセットなど）       |
| **Roles**           | `role_id (PK)`, `app_id (FK)`, `role_name`, `description`                      | アプリ単位での役割（例：管理者、編集者、閲覧者） |
| **Permissions**     | `permission_id (PK)`, `app_id (FK)`, `permission_name`, `description`          | 操作権限（例：フォーム作成、編集、承認、閲覧）  |
| **RolePermissions** | `role_id (FK)`, `permission_id (FK)`                                           | 役割に付与された権限の紐付け（多対多）      |
| **UserRoles**       | `user_id (FK)`, `role_id (FK)`                                                 | ユーザーと役割の紐付け（多対多）         |
| **FormAccessRules** | `app_id (FK)`, `form_id`, `role_id (FK)`, `can_edit`, `can_view`, `can_delete` | フォーム単位の権限ルール（役割ごとに設定可能）  |

---

## ポイント解説

* **Users**
  CognitoのユーザーID (`cognito_sub`)をキーにしつつ、システム内で必要なユーザー属性を管理。

* **Applications**
  複数のアプリを管理できるようにし、将来的にアプリごとに権限を分けるベースとする。

* **Roles & Permissions**
  ロール（役割）ごとに権限を割り当てる典型的なRBAC（ロールベースアクセス制御）。
  役割はアプリ単位で分けて、権限（Permission）は操作の具体的内容を粒度細かく設計。

* **RolePermissions**
  多対多の関連テーブルでロールと権限を紐づけ。ロールの粒度を柔軟にできる。

* **UserRoles**
  ユーザーは複数ロールを持てるようにし、複雑な権限体系をカバー。

* **FormAccessRules**
  BSS-FormFlowのフォームごとに、どのロールがどんな操作（閲覧・編集・削除）をできるかを細かく制御。
  フォームIDはアプリ内の特定のフォームを指し、ロール単位で操作許可をカスタマイズ可能。

---

## 拡張例

* **属性ベースアクセス制御（ABAC）対応**
  将来的に「ユーザー属性やフォームデータ属性による細かなアクセス制御」を導入したい場合は、
  ルールテーブルを追加し、属性と権限条件を紐付ける仕組みを用意。

* **権限継承・階層化**
  ロール間の継承を実装すると管理が楽になるケースもあるため、
  `ParentRoleId`カラムを`Roles`に追加する設計も可能。

---

## ER図イメージ（概略）

```
Users --< UserRoles >-- Roles --< RolePermissions >-- Permissions
          |                       |
          |                       +--< FormAccessRules (app_id, form_id, role_id, 権限フラグ)
          |
      Cognito連携

Applications
  |
  +-- Roles (app_id FK)
  +-- Permissions (app_id FK)
  +-- FormAccessRules (app_id FK)
```

---

もし必要ならSQLテーブル定義や、FastAPI + Pydanticモデルでの設計例も作成します。
どうぞご指示ください！
