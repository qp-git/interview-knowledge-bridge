# Security Notes

## Overview

Interview Knowledge Bridge allows Custom GPT to retrieve approved Markdown documents from GitHub.

Because Lambda can access GitHub through the GitHub API, this API must be designed carefully.

The most important security idea is that Lambda should not behave as a simple proxy.

It should act as a gatekeeper that controls which documents can be returned.

## Main risk

Lambda may have a GitHub token that can read files from an allowed repository.

If the API accepts arbitrary file paths from the client, a caller could attempt to retrieve files that were not intended to be exposed.

For example, this kind of design should be avoided:

    GET /documents?path=some/arbitrary/file.md

Instead, the API should accept only a document_id:

    GET /documents/public-interview-knowledge-bridge

The document_id is resolved to an approved path only after checking allowed-documents.json.

## Authentication

The API uses Bearer authentication.

Custom GPT sends the API key in the Authorization header.

    Authorization: Bearer <BRIDGE_API_KEY>

Lambda checks this value against the BRIDGE_API_KEY environment variable.

If the token is missing or invalid, Lambda returns 401.

Authentication answers this question:

    Is this caller allowed to use the API?

## Authorization

Authentication alone is not enough.

Even after authentication succeeds, the API must decide which document the caller is allowed to retrieve.

This project uses allowed-documents.json for authorization.

The API only returns documents that are explicitly listed in allowed-documents.json.

Authorization answers this question:

    Which document is this caller allowed to retrieve?

## Document allowlist

allowed-documents.json defines the documents that can be retrieved.

Each entry has:

    id
    title
    path

The client sends only the id.

Lambda uses the id to look up the approved path.

This prevents the client from directly choosing arbitrary paths in the repository.

## Path handling

The API should not accept raw file paths from the client.

The allowed path should be defined only on the server side.

Recommended restrictions:

- Only allow files listed in allowed-documents.json
- Only allow Markdown files
- Keep allowed files under gpt-context/summaries/
- Reject paths that contain ..
- Do not expose repository root browsing
- Do not return files that are not explicitly listed

## GitHub token scope

The GitHub token should have the minimum permissions required.

Recommended:

- Contents: Read-only
- Metadata: Read-only
- Repository access limited to the required repository

Avoid giving the token write permissions.

Avoid using a token that can access unrelated repositories.

## Public and private sources

This API can return documents from both public and private repositories.

The response includes the source field.

    source: public
    source: private

This helps the AI agent distinguish between externally visible information and private context.

Public documents are suitable for portfolio descriptions.

Private documents are suitable for detailed learning notes, troubleshooting records, and interview preparation context.

The application should avoid mixing these purposes.

## Secrets management

Current simple approach:

- Store BRIDGE_API_KEY in Lambda environment variables
- Store GitHub token in Lambda environment variables

Possible improvements:

- Use AWS Secrets Manager
- Use API Gateway Authorizer
- Use GitHub App instead of a long-lived PAT
- Rotate secrets periodically
- Separate public and private access policies

## Logging

Logs should help with troubleshooting without exposing secrets.

Recommended:

- Log request path
- Log document_id
- Log source type
- Log authorization failures without printing tokens
- Log GitHub API failures without printing credentials

Avoid logging:

- BRIDGE_API_KEY
- GitHub token
- Full Authorization header
- Private document content

## OpenAPI schema caution

The OpenAPI schema is used by Custom GPT Actions.

It should be simple and stable.

To avoid encoding and copy-paste issues, examples in openapi.yaml should use ASCII text when possible.

Recommended:

    example: Portfolio index

Avoid:

    example: 公開ポートフォリオ概要

Japanese Markdown content can still be returned by the API response.

The OpenAPI schema itself does not need Japanese examples.

## Lessons learned

The main lesson is that an AI-facing retrieval API needs both convenience and control.

It is useful to let an AI agent retrieve Markdown documents from GitHub.

However, once Lambda has permission to access GitHub, Lambda is responsible for deciding what information can be returned.

A secure design should not rely only on authentication.

It should also control the retrieval target through authorization.

In this project, document_id and allowed-documents.json are used to keep the retrieval target explicit and limited.

This pattern can be reused for other AI agents or internal knowledge retrieval tools.


## Custom GPT Actions 運用メモ

Custom GPT Actions では、OpenAPI schema を編集・再インポートしたあとに、APIキーの設定を入れ直す必要がある場合がある。

schema自体が正しく、curlではAPIが正常に動作していても、Actions側でBearerトークンが保存されていない、またはリクエストに付与されていない場合、403エラーになる。

schema更新後にActionsをテストする場合は、以下を確認する。

- OpenAPI schema が正常に保存されていること
- Authentication type が API Key になっていること
- Auth type が Bearer になっていること
- API Key 欄に実際のキー値を入れ直していること
- Action更新後にGPT本体も保存していること

Actionsから403が返る場合は、まずAPIキーが正しく送信されていない可能性を疑う。

一方、特定のdocument_idで404が返る場合は、APIキーではなく、allowed-documents.jsonやOpenAPI schemaのenumに対象IDが登録されていない可能性を疑う。
