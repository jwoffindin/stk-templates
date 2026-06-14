import json
import os
import re

import boto3

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
ALLOWED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split()

sns = boto3.client("sns")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def handler(event, _context):
    headers = event.get("headers") or {}
    origin = headers.get("origin", "")

    if not any(o in origin for o in ALLOWED_ORIGINS):
        return {
            "statusCode": 403,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "forbidden"}),
        }

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "invalid json"}),
        }

    email = (body.get("email") or "").strip().lower()

    if body.get("website", ""):
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"ok": True}),
        }

    if not EMAIL_RE.match(email):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "invalid email"}),
        }

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="New Upright waitlist signup",
        Message=f"Email: {email}\n",
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"ok": True}),
    }
