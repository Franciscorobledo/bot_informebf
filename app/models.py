from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BookingState(str, Enum):
    start = "START"
    ask_service = "ASK_SERVICE"
    ask_date = "ASK_DATE"
    ask_time = "ASK_TIME"
    check_availability = "CHECK_AVAILABILITY"
    confirmed = "CONFIRMED"


class SlackEvent(BaseModel):
    type: str
    team_id: Optional[str] = None
    event: Optional[Dict[str, Any]] = None
    challenge: Optional[str] = None


class BotConfig(BaseModel):
    id: str
    tenant_id: str
    name: str
    system_prompt: str
    features: Dict[str, Any] = Field(default_factory=dict)
    slack_team_id: str
    slack_channel_id: str
    google_calendar_id: str


class ConversationSession(BaseModel):
    id: str
    bot_id: str
    slack_user_id: str
    state: BookingState
    context: Dict[str, Any] = Field(default_factory=dict)


class IntentResult(BaseModel):
    intent: str
    entities: Dict[str, Any] = Field(default_factory=dict)
