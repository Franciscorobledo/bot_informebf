from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from app.models import BookingState, ConversationSession, IntentResult


@dataclass
class StateResponse:
    next_state: BookingState
    message: str
    updated_context: Dict[str, str]
    should_book: bool = False


def advance_state(
    session: ConversationSession,
    intent: Optional[IntentResult],
) -> StateResponse:
    context = dict(session.context)
    intent_name = (intent.intent if intent else "").lower()
    entities = intent.entities if intent else {}

    if session.state == BookingState.start:
        if intent_name in {"book_appointment", "affirm"}:
            return StateResponse(
                next_state=BookingState.ask_service,
                message="Great! What service would you like to book?",
                updated_context=context,
            )
        return StateResponse(
            next_state=BookingState.start,
            message="Would you like to book an appointment?",
            updated_context=context,
        )

    if session.state == BookingState.ask_service:
        service = entities.get("service")
        if service:
            context["service"] = service
            return StateResponse(
                next_state=BookingState.ask_date,
                message="Awesome. What date works for you?",
                updated_context=context,
            )
        return StateResponse(
            next_state=BookingState.ask_service,
            message="Which service should I book for you?",
            updated_context=context,
        )

    if session.state == BookingState.ask_date:
        date = entities.get("date")
        if date:
            context["date"] = date
            return StateResponse(
                next_state=BookingState.ask_time,
                message="Thanks! What time do you prefer?",
                updated_context=context,
            )
        return StateResponse(
            next_state=BookingState.ask_date,
            message="What date would you like?",
            updated_context=context,
        )

    if session.state == BookingState.ask_time:
        time = entities.get("time")
        if time:
            context["time"] = time
            return StateResponse(
                next_state=BookingState.check_availability,
                message="Checking availability...",
                updated_context=context,
                should_book=True,
            )
        return StateResponse(
            next_state=BookingState.ask_time,
            message="What time works for you?",
            updated_context=context,
        )

    if session.state == BookingState.check_availability:
        return StateResponse(
            next_state=BookingState.confirmed,
            message="You're all set!",
            updated_context=context,
        )

    return StateResponse(
        next_state=BookingState.confirmed,
        message="Your appointment is confirmed.",
        updated_context=context,
    )
