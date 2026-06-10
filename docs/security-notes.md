# Security Notes

## Overview

Interview Knowledge Bridge では、Custom GPT から GitHub リポジトリを直接参照させず、API Gateway と Lambda を中継させています。

Lambda は GitHub fine-grained PAT を利用して Private Repository を参照しますが、API利用者へ返す情報は allowed-documents.json によって制御しています。

## Authentication and Authorization

この構成では、認証と認可を分けて考えています。

### Authentication

API利用者が正しい相手かを確認するため、Bearer認証を利用しています。

Custom GPT は API呼び出し時に、Authorization ヘッダーへ Bearer 形式で BRIDGE_API_KEY を送信します。

例:

    Authorization: Bearer <BRIDGE_API_KEY>

Lambda はリクエストヘッダーの値を確認し、環境変数に保存された BRIDGE_API_KEY と一致する場合のみ処理を続行します。

### Authorization

Bearer認証に成功しても、API利用者が Private Repository 内の任意ファイルを読めるわけではありません。

取得できる文書は、allowed-documents.json に定義された document_id のみです。

例:

    GET /documents/incident-response

API利用者はファイルパスを直接指定できず、document_id のみ指定します。

Lambda は document_id をもとに allowed-documents.json を参照し、許可されたパスのみ取得します。

## allowed-documents.json

allowed-documents.json は、API利用者に返してよい文書のホワイトリストです。

例:

    {
      "documents": [
        {
          "id": "incident-response",
          "title": "障害対応演習",
          "path": "gpt-context/summaries/incident-response.md"
        }
      ]
    }

Lambda はこの一覧に存在する document_id だけを受け付けます。

## GitHub PAT Scope

Private Repository の参照には GitHub fine-grained PAT を使用しています。

PATには必要最小限の権限のみ付与します。

- Repository access: engineer-private-notes のみ
- Contents: Read-only
- Metadata: Read-only

このPATは Lambda の環境変数として保持し、GitHub上には保存しません。

## Public and Private Repositories

このAPIは、Private Repository と Public Repository の両方を参照します。

### Private Repository

Private Repository には、面接準備や学習メモなど、外部公開しない情報を配置します。

構成例:

    engineer-private-notes/
    └── gpt-context/
        ├── allowed-documents.json
        └── summaries/

### Public Repository

Public Repository には、公開可能なポートフォリオ情報を配置します。

構成例:

    engineer-portfolio/
    └── gpt-context/
        ├── allowed-documents.json
        └── summaries/

APIレスポンスでは、各文書に source を付け、Private/Public の区別ができるようにしています。

例:

    {
      "id": "public-portfolio-index",
      "title": "公開ポートフォリオ概要",
      "source": "public"
    }

## Important Risk

Lambda は GitHub PAT を持っているため、権限上は Private Repository 内のファイルを読むことができます。

そのため、Lambdaコードに不備があると、PATの権限内で本来返すべきでないファイルを返してしまうリスクがあります。

このリスクを抑えるため、以下の制御を行っています。

- API利用者から任意のファイルパスを受け取らない
- document_id のみ受け取る
- document_id からパスへの変換は allowed-documents.json でのみ行う
- 取得可能なパスを gpt-context/summaries/ 配下に制限する
- 取得対象を .md ファイルのみに制限する
- .. を含むパスを拒否する

## Current Limitations

現在の構成はMVPです。

今後の改善点は以下です。

- GitHub PAT を AWS Secrets Manager に移行する
- GitHub App 方式に変更する
- API Gateway Authorizer の利用を検討する
- CloudWatch Logs を整理する
- エラー時に内部情報を返しすぎないようにする
- CI/CDでLambdaコードとOpenAPI schemaの反映を自動化する

## Summary

この構成では、Custom GPT に Private Repository の権限を直接渡さず、API Gateway + Lambda を中継させています。

Lambdaは強い権限を持つため、外部へ返す情報をコード上で明確に制御する必要があります。

認証によってAPI利用者を確認し、認可によって取得可能な文書を制限することで、Privateな情報を扱うAI連携における安全性を高めています。
