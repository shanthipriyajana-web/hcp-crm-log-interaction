import json
from datetime import datetime
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.llm import llm
from app.tools import ALL_TOOLS, TOOL_RUNNERS, _followups_for

llm_with_tools = llm.bind_tools(ALL_TOOLS)

SYSTEM_PROMPT = (
    "You are an AI assistant embedded in a pharma field rep's CRM. Your job "
    "is to manage a 'Log Interaction' form on the user's behalf by calling "
    "the tools available to you. The user NEVER edits the form directly - "
    "every change must go through a tool call. The form has these fields: "
    "HCP Name, Interaction Type (Meeting/Call/Email/Conference), Date, Time, "
    "Attendees, Topics Discussed, Materials Shared, Samples Distributed, "
    "Sentiment (Positive/Neutral/Negative), Outcomes, and Follow-up Actions. "
    "Use log_interaction the first time a visit is described, edit_interaction "
    "for later corrections to specific fields, clear_form to reset, "
    "summarize_interaction to recap the form, and validate_form to check "
    "readiness for submission. Always call exactly one tool per user message "
    "when the message implies a form action. If the message is just small "
    "talk, reply normally without calling a tool."
)


def agent_node(state: AgentState) -> dict:
    """LLM decides which (if any) tool to call, given the chat history and
    a snapshot of the current form so it has context for edits."""
    now = datetime.now()
    time_context = (
        f"Real current date and time: {now.strftime('%Y-%m-%d')} (a {now.strftime('%A')}), "
        f"{now.strftime('%H:%M')}. Use this as the reference point for any relative "
        f"date/time words in the user's message."
    )
    form_snapshot = f"Current form state: {json.dumps(state['form'])}"
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        SystemMessage(content=time_context),
        SystemMessage(content=form_snapshot),
    ] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def tool_executor_node(state: AgentState) -> dict:
    """Executes whichever tool(s) the LLM asked for, mutating the shared
    form state and returning a ToolMessage for each call."""
    last_message = state["messages"][-1]
    tool_messages = []
    updated_form = state["form"]
    tool_called = state.get("tool_called")
    validation = state.get("validation")
    suggested_followups = state.get("suggested_followups")

    for call in last_message.tool_calls:
        name = call["name"]
        args = call["args"] or {}
        runner = TOOL_RUNNERS.get(name)
        if runner is None:
            content = f"Unknown tool: {name}"
        else:
            updated_form, content = runner(updated_form, args)
            tool_called = name
            if name == "validate_form":
                missing = [k for k in ("hcp_name", "date", "interaction_type", "sentiment") if not updated_form.get(k)]
                validation = {"ready": len(missing) == 0, "missing": missing}
            if name in ("log_interaction", "edit_interaction"):
                suggested_followups = _followups_for(updated_form)
            if name == "clear_form":
                suggested_followups = []
        tool_messages.append(
            ToolMessage(content=content, tool_call_id=call["id"], name=name)
        )

    return {
        "messages": tool_messages,
        "form": updated_form,
        "tool_called": tool_called,
        "validation": validation,
        "suggested_followups": suggested_followups,
    }


def should_call_tool(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_executor_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_call_tool, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


app_graph = build_graph()
