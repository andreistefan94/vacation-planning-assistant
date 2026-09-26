"""FastAPI app implementing api/vacation-planning-assistant.yaml and serving ui/.

Run with:  uvicorn app.main:app --reload
"""
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Path as PathParam
from fastapi.staticfiles import StaticFiles

from app import storage
from app.models import (
    ChatRequest,
    ChatResponse,
    ConversationListResponse,
    ConversationSummary,
    HistoryMessage,
    HistoryResponse,
    PreferencesResponse,
    Role,
    Status,
)

UI_DIR = Path(__file__).resolve().parent.parent / "ui"

app = FastAPI(title="Vacation Planning Assistant API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, Any]:
    """Liveness check, no authentication."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Send a user message (or their answer to a pending approval) and get the assistant's reply."""
    conversation_id = request.conversation_id or str(uuid.uuid4())
    storage.append_message(
        conversation_id, request.user_id, HistoryMessage(role=Role.user, content=request.message)
    )

    # TODO: replace with the LangGraph agent (thread_id=conversation_id). When the
    # graph hits an interrupt, return status=awaiting_approval + pending_approval.
    reply = f"(stub) You said: {request.message}"

    storage.append_message(
        conversation_id, request.user_id, HistoryMessage(role=Role.assistant, content=reply)
    )
    return ChatResponse(
        conversation_id=conversation_id,
        user_id=request.user_id,
        reply=reply,
        status=Status.completed,
    )


@app.get("/conversations/{conversation_id}", response_model=HistoryResponse)
def get_history(
    conversation_id: str = PathParam(description="A conversation_id previously returned by POST /chat."),
) -> HistoryResponse:
    """Full transcript of one conversation; 404 if the conversation_id is unknown."""
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return HistoryResponse(conversation_id=conversation_id, messages=conversation.messages)


@app.get("/users/{user_id}/conversations", response_model=ConversationListResponse)
def list_user_conversations(
    user_id: str = PathParam(description="Same user_id used in POST /chat."),
) -> ConversationListResponse:
    """This user's conversations, newest first; empty list if they have none."""
    conversations = [
        ConversationSummary(
            conversation_id=c.conversation_id,
            started_at=c.started_at,
            last_message_at=c.last_message_at,
            preview=c.preview,
        )
        for c in storage.list_conversations(user_id)
    ]
    return ConversationListResponse(user_id=user_id, conversations=conversations)


@app.get("/users/{user_id}/preferences", response_model=PreferencesResponse)
def get_user_preferences(
    user_id: str = PathParam(description="Same user_id used in POST /chat."),
) -> PreferencesResponse:
    """Long-term preferences remembered for this user; empty list if none are stored."""
    return PreferencesResponse(user_id=user_id, preferences=storage.get_preferences(user_id))


@app.delete("/users/{user_id}/preferences")
def delete_user_preferences(
    user_id: str = PathParam(description="Same user_id used in POST /chat."),
) -> dict[str, Any]:
    """Forget all of this user's long-term preferences."""
    deleted = storage.delete_preferences(user_id)
    return {"user_id": user_id, "deleted": deleted}


app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")
