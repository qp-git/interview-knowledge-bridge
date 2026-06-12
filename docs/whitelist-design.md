# ホワイトリスト設計メモ

## 目的

このドキュメントでは、Bridge API で利用するホワイトリスト制御の考え方を整理します。

## 基本方針

Bridge API では、Custom GPT から任意の GitHub URL やファイルパスを直接受け取りません。

代わりに、`document_id` または `project_id` を受け取り、API 側で許可済みの GitHub パスに変換します。

## document_id

`document_id` は、取得可能な Markdown を1件ずつ識別するための ID です。

例:

    odaibox-readme
    odaibox-design-decisions
    stt-ecs-architecture
    bridge-design-decisions

API 側では、これらの ID と GitHub 上の Markdown パスの対応を管理します。

## project_id

`project_id` は、プロジェクト単位で許可済み Markdown をまとめて取得するための ID です。

例:

    odaibox
    stt-ecs
    interview-knowledge-bridge

## ホワイトリストで防ぎたいこと

- 古いメモが回答に混ざること
- 未整理の作業ログが回答に混ざること
- AI が読み取りづらいファイルが回答材料になること
- 許可していないファイルが取得されること
- 関係ないプロジェクトの情報が混ざること

## 注意点

ホワイトリストは、一覧を作るだけでは不十分です。

API が任意のパスや URL を受け付ける設計だと、ホワイトリストに登録していないファイルを指定できる余地が残ります。

そのため、API の入力値を `document_id` や `project_id` に限定し、実際の GitHub パスは API 側でのみ管理する必要があります。
