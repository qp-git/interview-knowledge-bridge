# Interview Knowledge Bridge

## 概要

Interview Knowledge Bridge は、Custom GPT から Private GitHub リポジトリ上の許可済み Markdown を参照できるようにするための中継 API です。

Custom GPT にプロジェクトの詳細情報を補助的に参照させるため、API Gateway、Lambda、GitHub API を組み合わせて、許可済み Markdown だけを返す構成にしています。

## 作成背景

公開用のポートフォリオには、初見でも読みやすい概要、構成、設計判断、学びを整理しています。

一方で、Private リポジトリには、より細かいコード解説、制作背景、判断理由、作業中の補足メモなどを残しています。これらは AI にプロジェクト全体の把握や説明文の整理を補助させるうえで役立ちます。

ただし、Private リポジトリ内のすべての情報を AI に読ませると、古いメモ、未整理の作業ログ、AI が読み取りづらい資料などが混ざり、回答の質を下げる可能性があります。

そのため、Custom GPT と Private GitHub リポジトリの間に Bridge API を置き、ホワイトリストで許可した Markdown だけを返す構成にしました。

## 全体構成

基本的な流れは以下です。

    Custom GPT
      ↓
    Actions / OpenAPI schema
      ↓
    API Gateway
      ↓
    Lambda
      ↓ document_id / project_id を検証
    Whitelist
      ↓ 許可済みパスに変換
    GitHub API
      ↓
    Private GitHub Markdown

## 主な設計方針

### 任意のGitHubパスを受け取らない

Bridge API では、Custom GPT から任意の GitHub URL やファイルパスを直接受け取らない方針にしています。

任意パスを受け取る設計にすると、ホワイトリストを用意していても、許可していないファイルを指定できる余地が残ります。

そのため、Custom GPT からは `document_id` または `project_id` を受け取り、API 側で許可済みの GitHub パスに変換します。

### document_idで文書単位に制御する

`document_id` は、取得可能な Markdown を1件ずつ識別するための ID です。

API 側では、`document_id` と GitHub 上の Markdown パスの対応を管理します。ホワイトリストにない `document_id` は返しません。

### project_idでプロジェクト単位に制御する

`project_id` は、プロジェクト単位で関連する Markdown を取得するための ID です。

たとえば、OdaiBox、STT + ECS、Interview Knowledge Bridge など、プロジェクト単位で許可済み文書をまとめて返すことを想定しています。

## 使用技術

- Custom GPT Actions
- OpenAPI schema
- Amazon API Gateway
- AWS Lambda
- GitHub API
- Markdown
- ホワイトリストによる参照制御

## 環境変数

実際の値はリポジトリには含めません。

- `GITHUB_OWNER`
- `GITHUB_REPO`
- `GITHUB_BRANCH`
- `GITHUB_TOKEN`

## 関連ドキュメント

- [ホワイトリスト設計メモ](./docs/whitelist-design.md)
- [OpenAPI schema メモ](./docs/openapi-schema.md)
- [デプロイメモ](./docs/deploy.md)
