from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
from uuid import uuid4

from app.models import BotConfig, BookingState, ConversationSession


@dataclass
class InMemoryStore:
    bots: Dict[str, BotConfig] = field(default_factory=dict)
    sessions: Dict[str, ConversationSession] = field(default_factory=dict)

    def seed_demo_bot(self) -> None:
        demo_bot = BotConfig(
            id=str(uuid4()),
            tenant_id=str(uuid4()),
            name="Demo Spa Bot",
            system_prompt="You are a helpful booking assistant for a spa.",
            features={"booking_enabled": True},
            slack_team_id="T_DEMO",
            slack_channel_id="C_DEMO",
            google_calendar_id="primary",
        )
        self.bots[f"{demo_bot.slack_team_id}:{demo_bot.slack_channel_id}"] = demo_bot

    def get_bot_by_slack_channel(self, team_id: str, channel_id: str) -> Optional[BotConfig]:
        return self.bots.get(f"{team_id}:{channel_id}")

    def get_or_create_session(self, bot_id: str, slack_user_id: str) -> ConversationSession:
        key = f"{bot_id}:{slack_user_id}"
        session = self.sessions.get(key)
        if session:
            return session
        session = ConversationSession(
            id=str(uuid4()),
            bot_id=bot_id,
            slack_user_id=slack_user_id,
            state=BookingState.start,
            context={},
        )
        self.sessions[key] = session
        return session

    def save_session(self, session: ConversationSession) -> None:
        key = f"{session.bot_id}:{session.slack_user_id}"
        self.sessions[key] = session


store = InMemoryStore()
store.seed_demo_bot()
