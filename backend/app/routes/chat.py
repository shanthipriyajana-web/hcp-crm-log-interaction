from fastapi import APIRouter
from langchain_core.messages import HumanMessage, AIMessage

from app.graph import app_graph
from app.schemas import ChatRequest, ChatResponse, FormState

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    history = []
    for m in payload.history:
        history.append(HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content))
    history.append(HumanMessage(content=payload.message))

    result = app_graph.invoke(
        {
            "messages": history,
            "form": payload.form_state.model_dump(),
            "tool_called": None,
            "validation": None,
            "suggested_followups": None,
        }
    )

    final_message = result["messages"][-1]
    reply = final_message.content if isinstance(final_message.content, str) else str(final_message.content)

    return ChatResponse(
        reply=reply,
        form_state=FormState(**result["form"]),
        tool_called=result.get("tool_called"),
        validation=result.get("validation"),
        suggested_followups=result.get("suggested_followups"),
    )
