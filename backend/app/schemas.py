from typing import Optional, Literal
from pydantic import BaseModel


class FormState(BaseModel):
    """Mirrors the fields on the Interaction Details form in the UI."""

    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None  # Meeting / Call / Email / Conference
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[list[str]] = None
    samples_distributed: Optional[list[str]] = None
    sentiment: Optional[Literal["Positive", "Neutral", "Negative"]] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    notes: Optional[str] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    form_state: FormState
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    form_state: FormState
    tool_called: Optional[str] = None
    validation: Optional[dict] = None
    suggested_followups: Optional[list[str]] = None


class SubmitRequest(BaseModel):
    form_state: FormState


class InteractionOut(BaseModel):
    id: int
    hcp_name: Optional[str]
    interaction_type: Optional[str]
    date: Optional[str]
    time: Optional[str]
    attendees: Optional[str]
    topics_discussed: Optional[str]
    materials_shared: Optional[list[str]]
    samples_distributed: Optional[list[str]]
    sentiment: Optional[str]
    outcomes: Optional[str]
    follow_up_actions: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True
