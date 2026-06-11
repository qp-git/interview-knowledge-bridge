# Interview Knowledge Bridge

Interview Knowledge Bridge is an API that allows Custom GPT to retrieve approved Markdown documents from GitHub.

It was built to help organize and reuse learning portfolio records, project notes, and Markdown-based documentation with AI assistance.

The API is designed not only as a relay between Custom GPT and GitHub, but also as a controlled gateway that limits which documents can be returned.

## Purpose

When learning projects and portfolio notes are stored as Markdown in GitHub, it is useful for an AI agent to retrieve those documents and use them as context.

However, allowing an AI agent to freely access repository files is not desirable.

This project solves that by placing API Gateway and Lambda between Custom GPT and GitHub.

Custom GPT can request documents through the API, but Lambda only returns documents that are explicitly allowed.

## Architecture

    Custom GPT
      ↓ Bearer Auth
    API Gateway
      ↓
    Lambda
      ↓
    GitHub Repository

Custom GPT sends an HTTP request to API Gateway.

API Gateway invokes Lambda.

Lambda checks authentication, validates the requested document_id, retrieves the approved Markdown file from GitHub, and returns it to Custom GPT.

## Features

- List available documents
- Retrieve approved Markdown documents by document_id
- Support both public and private GitHub repositories
- Bearer authentication with BRIDGE_API_KEY
- Document allowlist using allowed-documents.json
- Prevent arbitrary file path access
- OpenAPI schema for Custom GPT Actions

## API Endpoints

    GET /health
      Health check endpoint.
      Authentication is not required.

    GET /documents
      Returns the list of approved documents.
      Bearer authentication is required.

    GET /documents/{document_id}
      Returns the Markdown content for an approved document.
      Bearer authentication is required.

## Document allowlist

The API does not accept raw GitHub file paths from the client.

Instead, the client sends a document_id.

Lambda checks allowed-documents.json and resolves the document_id to an approved Markdown path.

Example:

    document_id:
      public-interview-knowledge-bridge

    resolved path:
      gpt-context/summaries/interview-knowledge-bridge.md

This design keeps the retrieval target explicit and prevents clients from selecting arbitrary files.

## Authentication

The API uses Bearer authentication.

Custom GPT sends the API key in the Authorization header.

    Authorization: Bearer <BRIDGE_API_KEY>

Lambda compares this token with the BRIDGE_API_KEY environment variable.

## Repository structure

    lambda/
      Lambda function source code

    openapi/
      OpenAPI schema for Custom GPT Actions

    docs/
      Architecture, design, and security notes

## Documents

- [Architecture](docs/architecture.md)
- [Design Notes](docs/design-notes.md)
- [Security Notes](docs/security-notes.md)

## Key design idea

The most important design point is that Lambda is not treated as a simple proxy.

Because Lambda can call the GitHub API, it is responsible for deciding what information can be returned.

This project uses document_id and allowed-documents.json to separate authentication from authorization.

Authentication answers:

    Who can call this API?

Authorization answers:

    Which document can be returned?

This makes the API safer and easier to extend to other AI agents or internal knowledge retrieval tools.

## Notes for OpenAPI schema

The OpenAPI schema is used by Custom GPT Actions.

To avoid encoding and copy-paste issues, examples in openapi.yaml should use ASCII text when possible.

Japanese Markdown content can still be returned by the API response.

The schema itself does not need Japanese examples.

## Future improvements

- Use AWS Secrets Manager for API keys and GitHub tokens
- Use API Gateway Authorizer
- Replace GitHub PAT with GitHub App
- Improve CloudWatch logging
- Add automated schema validation
- Keep OpenAPI enum and allowed-documents.json in sync
