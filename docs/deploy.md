# デプロイメモ

## 概要

Bridge API は、API Gateway と Lambda を組み合わせて動かす想定です。

## デプロイ対象

- Lambda 関数
- API Gateway
- OpenAPI schema
- Lambda 環境変数
- GitHub API 参照用の設定

## 環境変数

実際の値はリポジトリに含めません。

- `GITHUB_OWNER`
- `GITHUB_REPO`
- `GITHUB_BRANCH`
- `GITHUB_TOKEN`

## 注意点

- GitHub token をコードに直書きしない
- `.env` ファイルをコミットしない
- 許可していない Markdown を返さない
- 任意の GitHub URL やファイルパスを API 入力として受け取らない
