# Interview Knowledge Bridge

Private GitHubに整理した面接準備・研修メモを、Custom GPTなどの外部クライアントから安全に参照するための中継APIです。

## Purpose

Privateリポジトリを直接GPTに読ませるのではなく、中継APIを挟み、参照可能な文書をホワイトリスト化します。

## Phase 1

まずはGitHub APIには接続せず、固定JSONを返すLambda/APIとして構築します。

## Endpoints

- GET /health
- GET /documents
- GET /documents/{document_id}

## Security Concept

- クライアントにGitHub tokenを持たせない
- 任意のファイルパスを受け付けない
- 許可済みのdocument_idのみ返す
- 将来的にGitHub Appまたはfine-grained PATでPrivate repoを読む

## Documents

- [Architecture](docs/architecture.md)
- [Security Notes](docs/security-notes.md)
