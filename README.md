# FinClear

SaaS型経費管理システム（Expense Management System）

## Overview

FinClearは、中小企業向けのSaaS型経費管理システムです。

企業ごとに独立したデータ管理を行うマルチテナント構成を採用し、
経費申請・管理業務の効率化を目的として開発しています。

本システムは個人開発プロジェクトとして、
要件定義、設計、開発、AWS環境構築、デプロイまで一貫して実施しています。


## Features

### Authentication / Authorization
- ユーザー認証
- 権限管理
- ロール管理

### Tenant Management
- テナント管理
- テナント単位でのデータ分離

### User Management
- ユーザー管理
- ユーザー情報管理

### Expense Management
- 経費登録
- 経費管理
- 経費情報検索


## Technology Stack

### Frontend

- Vue.js
- TypeScript
- Vite


### Backend

- Python
- FastAPI
- Mangum


### Database

- PostgreSQL


### Infrastructure / Cloud

- AWS Lambda
- Amazon API Gateway
- Amazon RDS for PostgreSQL
- Amazon S3
- Amazon CloudFront
- Amazon Route 53
- AWS Certificate Manager (ACM)
- AWS Systems Manager Parameter Store
- Amazon CloudWatch


### Infrastructure as Code

- Terraform


## System Architecture
