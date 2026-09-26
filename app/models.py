from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(
        ...,
        description='Stable identifier for long-term memory/preferences.',
        title='User Id',
    )
    conversation_id: str | None = Field(
        None,
        description='Omit to start a new conversation; pass it back on every following turn.',
        title='Conversation Id',
    )
    message: str = Field(
        ...,
        description="The user's message, or their answer to a pending approval request.",
        title='Message',
    )


class Status(Enum):
    completed = 'completed'
    awaiting_approval = 'awaiting_approval'


class ConversationSummary(BaseModel):
    conversation_id: str = Field(
        ...,
        description='Use as-is in a following POST /chat to resume this conversation.',
        title='Conversation Id',
    )
    started_at: str = Field(
        ...,
        description="ISO 8601 timestamp of this conversation's first turn.",
        title='Started At',
    )
    last_message_at: str = Field(
        ...,
        description="ISO 8601 timestamp of this conversation's most recent turn.",
        title='Last Message At',
    )
    preview: str | None = Field(
        '',
        description='Truncated first user message - just a label, not the full transcript.',
        title='Preview',
    )


class Role(Enum):
    user = 'user'
    assistant = 'assistant'
    system = 'system'
    tool = 'tool'


class PendingApproval(BaseModel):
    question: str = Field(
        ...,
        description='The decision/approval being asked of the user.',
        title='Question',
    )
    options: list[str] | None = Field(
        None,
        description='Concrete choices, if any; empty for a plain yes/no approval.',
        title='Options',
    )


class PreferencesResponse(BaseModel):
    user_id: str = Field(..., title='User Id')
    preferences: list[str] | None = Field(
        None,
        description='Long-term preferences remembered for this user (enunt.txt §2.4).',
        title='Preferences',
    )


class ToolCall(BaseModel):
    id: str = Field(
        ...,
        description='Unique id for this call; echoed as tool_call_id on its result message.',
        title='Id',
    )
    name: str = Field(
        ...,
        description="Tool name. Not part of the contract as an exact string - automated evaluation matches it fuzzily/by keyword (e.g. contains 'flight'), never against a hardcoded name, since naming is implementation-specific.",
        title='Name',
    )
    args: dict[str, Any] | None = Field(
        None, description='Arguments the tool was called with.', title='Args'
    )


class ValidationError(BaseModel):
    loc: list[str | int] = Field(..., title='Location')
    msg: str = Field(..., title='Message')
    type: str = Field(..., title='Error Type')
    input: Any | None = Field(None, title='Input')
    ctx: dict[str, Any] | None = Field(None, title='Context')


class ChatResponse(BaseModel):
    conversation_id: str = Field(
        ...,
        description="Echoes the request's conversation_id, or a newly generated one if it was omitted.",
        title='Conversation Id',
    )
    user_id: str = Field(..., title='User Id')
    reply: str = Field(
        ..., description="The assistant's message to show the user.", title='Reply'
    )
    status: Status = Field(
        ...,
        description="'awaiting_approval' means the workflow is suspended pending an explicit human decision.",
        title='Status',
    )
    pending_approval: PendingApproval | None = Field(
        None, description="Only present when status=='awaiting_approval'."
    )


class ConversationListResponse(BaseModel):
    user_id: str = Field(..., title='User Id')
    conversations: list[ConversationSummary] | None = Field(
        None, description='Newest first (by last_message_at).', title='Conversations'
    )


class HTTPValidationError(BaseModel):
    detail: list[ValidationError] | None = Field(None, title='Detail')


class HistoryMessage(BaseModel):
    role: Role = Field(..., title='Role')
    content: str | None = Field(
        '',
        description="The message text; for role=='tool', the tool's result. May be empty on an assistant message that is only issuing tool call(s), with no text for the user.",
        title='Content',
    )
    tool_calls: list[ToolCall] | None = Field(
        None,
        description='Present on an assistant message that invokes one or more tools - one entry per call, several entries for parallel calls on the same turn. Empty for an ordinary text turn.',
        title='Tool Calls',
    )
    tool_call_id: str | None = Field(
        None,
        description="On a role=='tool' message: the id of the ToolCall (see tool_calls above) this is the result of.",
        title='Tool Call Id',
    )


class HistoryResponse(BaseModel):
    conversation_id: str = Field(..., title='Conversation Id')
    messages: list[HistoryMessage] = Field(..., title='Messages')
