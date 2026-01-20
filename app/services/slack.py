from __future__ import annotations

import httpx

from app.config import settings


async def post_message(channel: str, text: str) -> None:
    if not settings.slack_bot_token:
        return
    payload = {"channel": channel, "text": text}
    headers = {"Authorization": f"Bearer {settings.slack_bot_token}"}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post("https://slack.com/api/chat.postMessage", json=payload, headers=headers)
        response.raise_for_status()
