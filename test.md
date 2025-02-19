```mermaid
graph TD
  A[React Frontend] -->|API Requests| B[API Gateway]
  B -->|Invoke| C[FastAPI Backend]
  C -->|Database Access| D[RDS or DynamoDB]
  A -->|Cognito Auth| E[AWS Cognito]
  E -->|Authentication| F[Cognito User Pool]
  F -->|Tokens (JWT)| A
  B -->|Secure API Calls| G[AWS WAF]
  G -->|IP Control| B
  C -->|Calls APIs| H[AWS Lambda]
  H -->|Invoke| D
  subgraph Cognito Flow
    F
    E
  end
  subgraph Amplify Setup
    A
    B
  end
```
