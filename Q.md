React, FastAPI, Amplify, Cognito (クライアントシークレット無効) 構成のシーケンス図 (mermaid 形式)
sequenceDiagram
    participant React App
    participant Amplify SDK
    participant Cognito Authorization Server
    participant Cognito Token Endpoint
    participant FastAPI Backend

    React App->>Amplify SDK: 認可リクエスト (Authorization Code Grant)
    Amplify SDK->>Cognito Authorization Server: 認可リクエスト (クライアントID)
    Cognito Authorization Server-->>React App: 認可コード
    React App->>Amplify SDK: 認可コード
    Amplify SDK->>Cognito Token Endpoint: トークンリクエスト (認可コード, クライアントID)
    Cognito Token Endpoint-->>Amplify SDK: アクセストークン, IDトークン
    Amplify SDK->>React App: アクセストークン, IDトークン
    React App->>FastAPI Backend: APIリクエスト (アクセストークン)
    FastAPI Backend->>Cognito Authorization Server: トークン検証 (アクセストークン)
    Cognito Authorization Server-->>FastAPI Backend: トークン検証結果
    FastAPI Backend-->>React App: APIレスポンス

解説
 * 認可リクエスト: React アプリケーションは、Amplify SDK を通じて Cognito Authorization Server に認可リクエストを送信します。この際、クライアント ID が含まれますが、クライアントシークレットは送信されません。
 * 認可コード発行: Cognito Authorization Server は、ユーザー認証後、React アプリケーションに認可コードを発行します。
 * トークンリクエスト: React アプリケーションは、Amplify SDK を通じて Cognito Token Endpoint にトークンリクエストを送信します。この際、認可コードとクライアント ID が含まれます。
 * アクセストークン発行: Cognito Token Endpoint は、認可コードとクライアント ID を検証し、アクセストークンと ID トークンを発行します。
 * API リクエスト: React アプリケーションは、アクセストークンを Bearer トークンとして含めて FastAPI Backend に API リクエストを送信します。
 * トークン検証: FastAPI Backend は、Cognito Authorization Server にアクセストークンの検証をリクエストします。
 * API レスポンス: Cognito Authorization Server は、アクセストークンの検証結果を FastAPI Backend に返します。FastAPI Backend は、検証結果に基づいて API レスポンスを React アプリケーションに返します。
ポイント
 * クライアントシークレットは送信されません。
 * 認可コードフロー (Authorization Code Grant) が使用されます。
 * アクセストークンは、API リクエストのたびに検証されます。
注意点
 * このシーケンス図は、あくまで基本的な流れを示したものです。実際の実装では、エラー処理やリフレッシュトークンの取得など、より複雑な処理が必要になる場合があります。
 * セキュリティを確保するために、HTTPS を使用し、トークンを安全に保管する必要があります。
ご不明な点がありましたら、お気軽にご質問ください。



`/abc` を開いた状態で **リロード** した場合、ALBのリスナールールによって `/index.html` にリダイレクトされます。  
そのため、ブラウザのURLバーには `https://your-domain.com/index.html` が表示されてしまい、Reactのルーティングが崩れる可能性があります。  

---

## **このままだと起きる問題**
❌ **React Routerで管理しているURLが `index.html` に変わってしまう**
- 例えば `/dashboard` にアクセス → `index.html` にリダイレクト
- Reactアプリ内のルーティングとは関係なく `index.html` がそのまま表示される
- `index.html` の `react-router` の `BrowserRouter` で `/dashboard` に戻せない
- **結果、ページが意図しない挙動になる**

---

## **解決策**
### **① ALBのリスナールールを変更してリダイレクトではなく転送にする（推奨）**
現在のリダイレクト (`RedirectConfig`) ではなく、S3へ**直接転送** (`ForwardConfig`) するようにします。

```sh
aws elbv2 create-rule \
    --listener-arn <LISTENER_ARN> \
    --priority 10 \
    --conditions '[{"Field":"path-pattern","Values":["/*"]}]' \
    --actions '[{"Type":"forward","TargetGroupArn":"<TARGET_GROUP_ARN>"}]'
```

#### **この方法のメリット**
✅ **リロードしてもURLは変わらない**（`/abc` のまま）  
✅ **React Routerが機能する**（`index.html` を返すだけなので）  
✅ **すべてのパスで `index.html` を配信できる**  

**💡 ALBをS3のVPCエンドポイントにフォワードするには、ALBのターゲットグループとしてS3エンドポイントを指定する必要があります。**

---

### **② CloudFrontを利用する**
CloudFrontをALBの前に置いて、**403/404時に `index.html` を返す** ように設定する。

1. **CloudFront のオリジンに ALB を指定**
2. **カスタムエラーページを設定**
   - `403` と `404` のエラー時に `/index.html` を返すようにする
   - **レスポンスコードは `200` に変更**

💡 **この方法なら、React Routerのルーティングも維持される！**

---

## **どっちの方法がいい？**
| 方法 | メリット | デメリット |
|------|--------|-----------|
| **ALBのフォワード（①）** | シンプルで設定が少ない | ALBのターゲットグループにS3エンドポイントを設定する必要がある |
| **CloudFront（②）** | キャッシュで高速化、React Router対応 | CloudFrontの設定が増える |

👉 まず **ALBのフォワード（①）を試して、ダメならCloudFront（②）を追加** するのが良いですね！ 🚀
