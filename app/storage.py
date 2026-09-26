"""In-memory storage for conversations and long-term user preferences.

Placeholder until the SQLite / LangGraph checkpointer is wired in - all data
is lost when the server restarts.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.models import HistoryMessage, Role

PREVIEW_LENGTH = 60


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Conversation:
    conversation_id: str
    user_id: str
    started_at: str = field(default_factory=_now)
    last_message_at: str = field(default_factory=_now)
    messages: list[HistoryMessage] = field(default_factory=list)

    @property
    def preview(self) -> str:
        first_user = next((m for m in self.messages if m.role == Role.user), None)
        return (first_user.content or "")[:PREVIEW_LENGTH] if first_user else ""


_conversations: dict[str, Conversation] = {}
_preferences: dict[str, list[str]] = {}


def get_conversation(conversation_id: str) -> Conversation | None:
    return _conversations.get(conversation_id)


def append_message(conversation_id: str, user_id: str, message: HistoryMessage) -> None:
    conversation = _conversations.setdefault(
        conversation_id, Conversation(conversation_id=conversation_id, user_id=user_id)
    )
    conversation.messages.append(message)
    conversation.last_message_at = _now()


def list_conversations(user_id: str) -> list[Conversation]:
    """This user's conversations, newest first."""
    owned = [c for c in _conversations.values() if c.user_id == user_id]
    return sorted(owned, key=lambda c: c.last_message_at, reverse=True)


def get_preferences(user_id: str) -> list[str]:
    return list(_preferences.get(user_id, []))


def add_preference(user_id: str, preference: str) -> None:
    prefs = _preferences.setdefault(user_id, [])
    if preference not in prefs:
        prefs.append(preference)


def delete_preferences(user_id: str) -> int:
    """Forget all preferences for this user; returns how many were removed."""
    return len(_preferences.pop(user_id, []))
