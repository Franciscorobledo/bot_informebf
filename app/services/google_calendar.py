from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict

import httpx

from app.config import settings


async def create_calendar_event(
    calendar_id: str,
    access_token: str,
    summary: str,
    start_time: datetime,
    duration_minutes: int = 60,
) -> Dict[str, str]:
    end_time = start_time + timedelta(minutes=duration_minutes)
    payload = {
        "summary": summary,
        "start": {"dateTime": start_time.isoformat()},
        "end": {"dateTime": end_time.isoformat()},
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{settings.google_api_base}/calendars/{calendar_id}/events",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
    return {"id": data.get("id", ""), "html_link": data.get("htmlLink", "")}
