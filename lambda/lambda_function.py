import json

DOCUMENTS = {
    "incident-response": {
        "id": "incident-response",
        "title": "障害対応演習",
        "summary": "障害対応演習後に、外形監視・内部監視・cron制御まで個人学習で追加実装した。",
        "skills": [
            "Route 53",
            "CloudWatch",
            "SNS",
            "Shell Script",
            "cron"
        ],
        "interview_points": [
            "復旧後の再発防止まで考えた",
            "外形監視と内部監視の役割を分けた",
            "権限制約下で実装できる現実的な監視方法を選んだ",
            "危険な自動実行だけを制御した"
        ]
    }
}


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }


def lambda_handler(event, context):
    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method", "")

    if method == "GET" and path == "/health":
        return response(200, {"status": "ok"})

    if method == "GET" and path == "/documents":
        return response(200, {
            "documents": [
                {
                    "id": doc["id"],
                    "title": doc["title"]
                }
                for doc in DOCUMENTS.values()
            ]
        })

    if method == "GET" and path.startswith("/documents/"):
        document_id = path.split("/")[-1]

        if document_id not in DOCUMENTS:
            return response(404, {
                "error": "document_not_found",
                "message": "The requested document is not allowed or does not exist."
            })

        return response(200, DOCUMENTS[document_id])

    return response(404, {
        "error": "not_found",
        "message": "The requested endpoint was not found."
    })
