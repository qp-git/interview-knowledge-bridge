import os
import json
import base64
import urllib.request
import urllib.error


BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY")

# Private repository
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "qp-git")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "engineer-private-notes")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

# Public repository
GITHUB_PUBLIC_OWNER = os.environ.get("GITHUB_PUBLIC_OWNER", GITHUB_OWNER)
GITHUB_PUBLIC_REPO = os.environ.get("GITHUB_PUBLIC_REPO", "engineer-portfolio")
GITHUB_PUBLIC_BRANCH = os.environ.get("GITHUB_PUBLIC_BRANCH", "main")

ALLOWED_DOCS_PATH = "gpt-context/allowed-documents.json"


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


def get_header(event, header_name):
    headers = event.get("headers") or {}

    for key, value in headers.items():
        if key.lower() == header_name.lower():
            return value

    return None


def is_authorized(event):
    if not BRIDGE_API_KEY:
        return False

    authorization = get_header(event, "Authorization")

    if authorization == f"Bearer {BRIDGE_API_KEY}":
        return True

    return False


def github_get_content(owner, repo, branch, path, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "interview-knowledge-bridge",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"GitHub API error: {e.code} {error_body}")

    if data.get("encoding") != "base64":
        raise Exception("Unexpected GitHub content encoding")

    content = base64.b64decode(data["content"]).decode("utf-8")
    return content


def is_safe_summary_path(path):
    return (
        isinstance(path, str)
        and path.startswith("gpt-context/summaries/")
        and path.endswith(".md")
        and ".." not in path
    )


def load_allowed_documents(source):
    if source == "private":
        content = github_get_content(
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            branch=GITHUB_BRANCH,
            path=ALLOWED_DOCS_PATH,
            token=GITHUB_TOKEN,
        )
    elif source == "public":
        content = github_get_content(
            owner=GITHUB_PUBLIC_OWNER,
            repo=GITHUB_PUBLIC_REPO,
            branch=GITHUB_PUBLIC_BRANCH,
            path=ALLOWED_DOCS_PATH,
            token=None,
        )
    else:
        raise Exception("Unknown source")

    data = json.loads(content)
    documents = data.get("documents", [])

    for doc in documents:
        doc["source"] = source

    return documents


def load_document_content(source, path):
    if not is_safe_summary_path(path):
        raise Exception("Unsafe document path")

    if source == "private":
        return github_get_content(
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            branch=GITHUB_BRANCH,
            path=path,
            token=GITHUB_TOKEN,
        )

    if source == "public":
        return github_get_content(
            owner=GITHUB_PUBLIC_OWNER,
            repo=GITHUB_PUBLIC_REPO,
            branch=GITHUB_PUBLIC_BRANCH,
            path=path,
            token=None,
        )

    raise Exception("Unknown source")


def list_all_documents():
    private_docs = load_allowed_documents("private")
    public_docs = load_allowed_documents("public")

    return private_docs + public_docs


def find_document(document_id):
    documents = list_all_documents()

    for doc in documents:
        if doc.get("id") == document_id:
            return doc

    return None


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("rawPath", "")

    if method == "OPTIONS":
        return response(200, {"status": "ok"})

    if path == "/health":
        return response(200, {"status": "ok"})

    if not is_authorized(event):
        return response(401, {
            "error": "unauthorized",
            "message": "Valid Bearer token is required."
        })

    try:
        if path == "/documents":
            documents = list_all_documents()

            return response(200, {
                "documents": [
                    {
                        "id": doc.get("id"),
                        "title": doc.get("title"),
                        "source": doc.get("source"),
                    }
                    for doc in documents
                ]
            })

        if path.startswith("/documents/"):
            document_id = path.replace("/documents/", "", 1)

            doc = find_document(document_id)

            if not doc:
                return response(404, {
                    "error": "document_not_found",
                    "message": f"Document '{document_id}' is not allowed."
                })

            content = load_document_content(
                source=doc.get("source"),
                path=doc.get("path"),
            )

            return response(200, {
                "id": doc.get("id"),
                "title": doc.get("title"),
                "source": doc.get("source"),
                "source_path": doc.get("path"),
                "content": content,
            })

        return response(404, {
            "error": "not_found",
            "message": "Route not found."
        })

    except Exception as e:
        return response(500, {
            "error": "internal_server_error",
            "message": str(e)
        })
