# インフラ設計書（Infrastructure Design）

- Project：FinClear
- Version：1.0
- Author：GRS-CLOUD
- Last Update：2026-07-20

---

# 1. 概要

本ドキュメントでは、FinClear SaaS経費精算システムのAWSインフラ構成について定義する。

本システムはサーバーレスアーキテクチャを採用し、TerraformによるInfrastructure as Code（IaC）で環境を構築・管理する。

採用方針は以下の通り。

- フロントエンド：Vue.js
- バックエンド：FastAPI
- Lambda Adapter：Mangum
- IaC：Terraform
- DB：Amazon RDS PostgreSQL
- ファイル保存：Amazon S3
- CDN：Amazon CloudFront
- API：Amazon API Gateway（HTTP API）
- DNS：Amazon Route53
- ドメイン：finclear.grs-co.jp

---

# 2. システム構成

```
Internet
      │
      ▼
 Route53
      │
      ▼
 CloudFront
 ┌──────────────┴──────────────┐
 │                             │
 ▼                             ▼
S3(Vue.js)                API Gateway
                                │
                                ▼
                           Lambda(Mangum)
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
          Amazon RDS                  Amazon S3
        PostgreSQL                Upload Files
                 │
                 ▼
      Systems Manager Parameter Store
```

---

# 3. 採用サービス一覧

|分類|AWSサービス|
|-------|-----------------------------|
|DNS|Route53|
|SSL証明書|AWS Certificate Manager|
|CDN|CloudFront|
|Frontend Hosting|Amazon S3|
|API|API Gateway HTTP API|
|Application|AWS Lambda|
|Database|Amazon RDS PostgreSQL|
|File Storage|Amazon S3|
|Secret管理|Systems Manager Parameter Store|
|Monitoring|CloudWatch|
|IAM|IAM Role / Policy|
|IaC|Terraform|

---

# 4. 採用アーキテクチャ

## フロントエンド

Vue.jsをビルドし、静的コンテンツとしてS3へ配置する。

CloudFrontを経由して公開し、高速配信およびHTTPS通信を実現する。

---

## バックエンド

FastAPIをAWS Lambda上で動作させる。

ASGI AdapterとしてMangumを採用する。

API Gateway HTTP APIからLambdaを呼び出す構成とする。

採用理由

- Lambdaとの親和性が高い
- サーバ管理不要
- オートスケール
- コスト最適化

---

## API Gateway

HTTP APIを採用する。

REST APIより低コストであり、FastAPIとの相性も良いため採用する。

URL例

```
https://finclear.grs-co.jp/api/login
https://finclear.grs-co.jp/api/users
https://finclear.grs-co.jp/api/expenses
```

CloudFrontのBehaviorにより、

```
/api/*
```

をAPI Gatewayへルーティングする。

---

## データベース

Amazon RDS PostgreSQLを利用する。

基本設定

- PostgreSQL
- Single-AZ
- Auto Storage Scaling
- Backup 7日
- Private Subnet配置

Lambdaからのみ接続可能とする。

---

## ファイル保存

Amazon S3を利用する。

保存対象

- 領収書
- 添付ファイル
- PDF
- CSV Export
- Company Logo

---

## シークレット管理

以下の情報はParameter Storeへ保存する。

- Database Password
- JWT Secret
- SMTP Password
- API Keys
- OpenAI API Key

LambdaはIAM Role経由で取得する。

---

# 5. ネットワーク構成

VPCを作成する。

構成

```
VPC

├── Public Subnet A
├── Public Subnet B
│
├── Private Subnet A
└── Private Subnet B
```

配置

|サービス|Subnet|
|---------|--------|
|Lambda|Private|
|RDS|Private|

InternetアクセスはNAT Gateway経由とする。

RDSはPublic Accessを無効化する。

---

# 6. ドメイン構成

独自ドメイン

```
grs-co.jp
```

サブドメイン

```
finclear.grs-co.jp
```

Route53でDNS管理を行う。

CloudFrontへAlias Recordを設定する。

SSL証明書はACMで管理する。

---

# 7. Terraform構成

TerraformはModule構成を採用する。

```
terraform/

├── environments/
│   ├── dev/
│   └── prod/
│
├── modules/
│   ├── network/
│   ├── iam/
│   ├── ssm/
│   ├── rds/
│   ├── lambda/
│   ├── api_gateway/
│   ├── s3/
│   ├── cloudfront/
│   ├── acm/
│   ├── route53/
│   └── cloudwatch/
│
└── global/
```

各Moduleは以下の構成とする。

```
main.tf

variables.tf

outputs.tf

locals.tf
```

---

# 8. マルチ環境

Terraformでは複数環境を管理する。

対象環境

- Development
- Production

環境ごとの差異は

- terraform.tfvars
- backend.tf

で管理する。

Terraform Moduleは共通利用する。

---

# 9. Terraform構築順序

Terraformでは以下の順番で環境を構築する。

1. Backend(S3 / DynamoDB)
2. Provider
3. VPC
4. Security Group
5. IAM
6. Parameter Store
7. RDS
8. S3
9. Lambda
10. API Gateway
11. CloudFront
12. ACM
13. Route53
14. CloudWatch

---

# 10. 今後追加予定

今後以下の機能を追加予定。

- AWS WAF
- AWS Backup
- Cost Anomaly Detection
- CloudWatch Alarm
- AWS Budgets
- GitHub Actions CI/CD
- Terraform Plan / Apply Pipeline
- Blue/Green Deployment
- Multi Region対応（将来）

---

# 11. 設計方針

本システムは以下を設計思想とする。

- Serverless First
- Infrastructure as Code
- Security by Default
- Least Privilege Principle
- Multi Environment
- Reusable Terraform Module
- Low Cost Operation
- High Maintainability
