from __future__ import annotations

import json
from typing import Optional

import httpx

from app.config import settings
from app.models import IntentResult


SYSTEM_PROMPT = """You are an intent extraction engine.
Return ONLY valid JSON with keys: intent, entities.
Allowed intents: book_appointment, reschedule, cancel, affirm, deny, other.
Entities schema:
  service: string | null
  date: string | null (ISO-8601 date)
  time: string | null (HH:MM 24h)
"""


async def extract_intent(message: str) -> Optional[IntentResult]:
    if not settings.openai_api_key:
        return None

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "temperature": 0,
    }

    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return None

    return IntentResult(intent=parsed.get("intent", "other"), entities=parsed.get("entities", {}))


EXAMPLE_PROMPT = {
    "role": "user",
    "content": "I want to book a deep tissue massage next Tuesday at 3pm.",
}

EXAMPLE_RESPONSE = {
    "intent": "book_appointment",
    "entities": {"service": "deep tissue massage", "date": "2024-07-16", "time": "15:00"},
}
