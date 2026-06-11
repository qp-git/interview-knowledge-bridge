# Design Notes

## Purpose

Interview Knowledge Bridge is an API that allows Custom GPT to retrieve approved Markdown documents from GitHub.

The goal is not only to connect Custom GPT and GitHub, but also to control which documents can be returned.

This API is designed as a controlled gateway for AI agents to access project notes, portfolio documents, and learning records stored as Markdown.

## Why a gateway is needed

At first glance, this system looks like a simple relay.

    Custom GPT
      ↓
    API Gateway
      ↓
    Lambda
      ↓
    GitHub Repository

However, Lambda has permission to call the GitHub API.

If Lambda has a GitHub token, it can read files within the repositories allowed by that token. Therefore, if the API accepts arbitrary file paths from the client, a bug or weak validation could cause unintended files to be returned.

For this reason, Lambda is designed not as a simple proxy, but as a gatekeeper.

## Gatekeeper design

The API does not accept raw GitHub file paths from Custom GPT.

Instead, Custom GPT sends a document_id.

Lambda then checks allowed-documents.json and resolves the document_id to an approved Markdown path.

Example:

    Request:
      GET /documents/public-interview-knowledge-bridge

    document_id:
      public-interview-knowledge-bridge

    resolved path:
      gpt-context/summaries/interview-knowledge-bridge.md

Only document IDs listed in allowed-documents.json can be retrieved.

This prevents the client from directly choosing arbitrary files in the repository.

## Authentication and authorization

This project separates authentication and authorization.

Authentication answers this question:

    Who is allowed to call the API?

This is handled by Bearer authentication using BRIDGE_API_KEY.

Authorization answers this question:

    Which document is the authenticated caller allowed to retrieve?

This is handled by allowed-documents.json and document_id based access control.

Even after authentication succeeds, the API only returns documents that are explicitly allowed.

## Public and private documents

The API can retrieve documents from both public and private repositories.

Public documents are mainly used for portfolio information and externally visible project summaries.

Private documents are used for detailed notes, troubleshooting records, and deeper learning context.

The API keeps these sources separated and returns the source type in the response.

    source: public
    source: private

This makes it easier for the AI agent to distinguish between externally visible information and private context.

## OpenAPI schema notes

The OpenAPI schema is used by Custom GPT Actions to understand how to call this API.

The schema should be kept simple and stable.

To avoid copy, paste, and encoding issues, examples in openapi.yaml should use ASCII text when possible.

Japanese Markdown content can still be returned by the API response. The OpenAPI schema itself does not need Japanese examples.

Recommended:

    example: Portfolio index

Avoid:

    example: 公開ポートフォリオ概要

## Main lesson learned

The main lesson from this project is that an AI-facing retrieval API should not be designed as a simple relay.

When Lambda has permission to access GitHub, it becomes responsible for deciding what information can be returned.

That means the API must control the retrieval target, not just forward requests.

Using document_id and allowed-documents.json makes the API safer and easier to extend.

This design can also be applied to other AI agents or internal knowledge retrieval tools.
