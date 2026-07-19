"""FinClear Lambda bootstrap handler for Mangum/FastAPI deployment."""

from __future__ import annotations

import json
import os


def handler(event, context):
    return {
        "statusCode": 503,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            {
                "message": "FinClear API infrastructure is deployed. Application package pending.",
                "log_level": os.environ.get("LOG_LEVEL", "INFO"),
            }
        ),
    }
