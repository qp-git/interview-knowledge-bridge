# OpenAPI schema メモ

## 目的

Custom GPT Actions から Bridge API を呼び出すための OpenAPI schema について整理します。

## 方針

Custom GPT からは、任意の GitHub パスではなく、`document_id` または `project_id` を指定して Bridge API を呼び出します。

## 想定する操作

### 文書単位の取得

`document_id` を指定して、許可済み Markdown を1件取得します。

利用例:

    document_id: odaibox-design-decisions

### プロジェクト単位の取得

`project_id` を指定して、プロジェクトに紐づく許可済み Markdown を取得します。

利用例:

    project_id: odaibox

## Custom GPT 側の指示

Custom GPT 側には、必要に応じて `document_id` や `project_id` を指定して Bridge API を呼び出すように指示します。

ただし、参照範囲の制御本体は GPT 側の指示ではなく、API 側のホワイトリストで行います。
