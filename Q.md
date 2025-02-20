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



`/` で S3 のターゲットグループに転送している場合、S3 側の設定によっては **React Router のルーティングが正常に動作しない** 可能性があります。  

---

### **問題の原因**
1. **S3 は "静的ウェブサイトホスティング" を使用している**
   - S3 の静的ウェブホスティングは、リクエストされたパス (`/abc`) に対応するオブジェクトが **そのまま** 存在することを前提にしています。
   - `/abc` というオブジェクトが S3 に無い場合、`403` や `404` エラーになり、`index.html` が返らない。

2. **React Router の `BrowserRouter` を使用している**
   - React の `BrowserRouter` は **クライアントサイドでルーティングを管理** するため、初回ロード時に `/abc` のデータを直接取得しようとします。
   - しかし、S3 には `/abc` というオブジェクトが無いため、エラー (`403/404`) になってしまう。

---

### **解決策**
#### **✅ 方法①: S3 の静的ウェブホスティングで 404 エラー時に `index.html` を返す**
もし **S3 の静的ウェブホスティングを有効化できる場合** は、**カスタムエラーページを設定** して `index.html` を返すようにできます。

1. **S3 バケットのプロパティで「静的ウェブサイトホスティング」を有効化**
2. **「エラードキュメント」の設定に `index.html` を指定**
   - **404 Not Found の場合でも `index.html` を返す**

💡 これにより、`/abc` にアクセスしても `index.html` をロードできるようになります。

---

#### **✅ 方法②: ALB で 404 / 403 エラーを `index.html` にリダイレクト**
S3 の静的ウェブホスティングを **使わずに**、ALB で 404 / 403 エラー時に `index.html` を返す方法もあります。

```sh
aws elbv2 create-rule \
    --listener-arn <LISTENER_ARN> \
    --priority 10 \
    --conditions '[{"Field": "path-pattern", "Values": ["/*"]}]' \
    --actions '[{"Type": "fixed-response", "FixedResponseConfig": { "StatusCode": "200", "ContentType": "text/html", "MessageBody": "<html><head><meta http-equiv=\"refresh\" content=\"0; url=/index.html\" /></head></html>" }}]'
```

**この方法のメリット**
- **S3 の設定変更なし** で実装可能
- すべてのパス (`/*`) を `index.html` にリダイレクト

---

#### **✅ 方法③: CloudFront を追加してエラーページを `index.html` にする**
CloudFront を ALB の前段に追加し、**エラーページ設定** で `index.html` を返すようにする方法です。

1. **CloudFront のオリジンに ALB を設定**
2. **エラーページのカスタマイズ**
   - `403` / `404` エラーが発生した場合に `index.html` を返す
   - ステータスコードは `200` に変更

```sh
aws cloudfront create-distribution \
    --origin-domain-name <ALB_DNS_NAME> \
    --default-root-object "index.html" \
    --custom-error-responses '[
        {"ErrorCode": 403, "ResponsePagePath": "/index.html", "ResponseCode": 200},
        {"ErrorCode": 404, "ResponsePagePath": "/index.html", "ResponseCode": 200}
    ]'
```

**この方法のメリット**
- React Router のルーティングを維持できる
- `403/404` エラー時でも `index.html` を表示
- CloudFront のキャッシュでパフォーマンス向上

---

### **どの方法を選ぶべきか？**
| 方法 | メリット | デメリット |
|------|---------|------------|
| **方法①: S3のエラードキュメント設定** | 設定が簡単で、S3側で解決 | S3 の静的ホスティングを有効にする必要あり |
| **方法②: ALBで `index.html` にリダイレクト** | S3 の設定変更なし | `meta refresh` を使うためリダイレクト動作が遅い |
| **方法③: CloudFront で `index.html` を返す** | キャッシュ最適化、最もパフォーマンスが良い | CloudFront の設定が必要 |

---

## **結論**
**S3 の静的ウェブホスティングが有効なら「方法①」が一番簡単！**  
もし **S3 の静的ウェブホスティングを使えない場合** は、**CloudFront（方法③）がベスト！** 🚀
