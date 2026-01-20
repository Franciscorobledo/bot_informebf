from __future__ import annotations

import json
from typing import Optional

import httpx

from app.config import settings
from app.models import IntentResult


SYSTEM_PROMPT = """You are an assistant that extracts booking intent from user messages.
Return ONLY valid JSON.

Possible intents:
- greet
- book_appointment
- reschedule_appointment
- cancel_appointment
- unknown

Extract these fields when possible:
- service
- date
- time
- time_preference (morning, afternoon, evening)

If data is missing, return null values.

Example output:
{
  "intent": "book_appointment",
  "service": "haircut",
  "date": "2026-01-20",
  "time": null,
  "time_preference": "morning"
}
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

    return IntentResult(
        intent=parsed.get("intent", "unknown"),
        entities={
            "service": parsed.get("service"),
            "date": parsed.get("date"),
            "time": parsed.get("time"),
            "time_preference": parsed.get("time_preference"),
        },
    )


EXAMPLE_PROMPT = {
    "role": "user",
    "content": "I want to book a deep tissue massage next Tuesday at 3pm.",
}

EXAMPLE_RESPONSE = {
    "intent": "book_appointment",
    "service": "deep tissue massage",
    "date": "2024-07-16",
    "time": "15:00",
    "time_preference": None,
}
