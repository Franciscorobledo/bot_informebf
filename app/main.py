from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, HTTPException, Request

from app.models import BookingState, SlackEvent
from app.services.booking_state import advance_state
from app.services.google_calendar import create_calendar_event
from app.services.openai_intent import extract_intent
from app.services.slack import post_message
from app.storage import store

app = FastAPI(title="Booking Bot SaaS")


@app.post("/webhooks/slack")
async def slack_webhook(request: Request) -> dict:
    payload = await request.json()
    event = SlackEvent.model_validate(payload)

    if event.type == "url_verification" and event.challenge:
        return {"challenge": event.challenge}

    if not event.event:
        raise HTTPException(status_code=400, detail="Missing event payload")

    team_id = event.team_id or ""
    channel_id = event.event.get("channel")
    user_id = event.event.get("user")
    text = event.event.get("text", "")

    if not channel_id or not user_id:
        raise HTTPException(status_code=400, detail="Missing channel or user")

    bot = store.get_bot_by_slack_channel(team_id, channel_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not configured for this channel")

    if not bot.features.get("booking_enabled", False):
        await post_message(channel_id, "Booking is currently disabled for this bot.")
        return {"ok": True}

    session = store.get_or_create_session(bot.id, user_id)

    intent = await extract_intent(text)
    result = advance_state(session, intent)

    session.state = result.next_state
    session.context.update(result.updated_context)
    store.save_session(session)

    if result.should_book and session.state == BookingState.check_availability:
        service = session.context.get("service", "appointment")
        date = session.context.get("date")
        time = session.context.get("time")
        if date and time:
            start_time = datetime.fromisoformat(f"{date}T{time}")
            await create_calendar_event(
                calendar_id=bot.google_calendar_id,
                access_token="GOOGLE_ACCESS_TOKEN",
                summary=f"{service} booking",
                start_time=start_time,
            )
            session.state = BookingState.confirmed
            store.save_session(session)
            await post_message(channel_id, "Your appointment is confirmed. See you soon!")
            return {"ok": True}

    await post_message(channel_id, result.message)
    return {"ok": True}
