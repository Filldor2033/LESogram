"""
Debug report endpoint for the mobile app.

The debug APK collects console output / errors in the WebView
and posts them here; the report is appended to a file on the
server so a failing voice recording can be diagnosed remotely
(Android WebView has no devtools for the user).
"""

import json
import time

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class DebugReport(BaseModel):
    ua: str = ""
    platform: str = ""
    entries: list = []
    diagnostics: dict = {}


REPORT_PATH = "/tmp/lesogram-debug-reports.jsonl"


@router.post("/debug-report")
async def debug_report(
    report: DebugReport,
    request: Request,
):
    line = json.dumps(
        {
            "at": time.time(),
            "ip": request.client.host if request.client else "?",
            "ua": report.ua,
            "platform": report.platform,
            "diagnostics": report.diagnostics,
            "entries": report.entries[-200:],
        },
        ensure_ascii=False,
    )

    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    return {"status": "ok"}
