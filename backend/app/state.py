from typing import Optional, TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State object threaded through the LangGraph agent.

    `messages` holds the running chat history (agent scratchpad included).
    `form` holds the current values of the Interaction Details form, which
    the tools read and mutate. The React app never edits `form` directly -
    only tool calls triggered by the LLM are allowed to change it.
    """

    messages: Annotated[list, add_messages]
    form: dict
    tool_called: Optional[str]
    validation: Optional[dict]
    suggested_followups: Optional[list]
