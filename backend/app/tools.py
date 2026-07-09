"""
Five LangGraph tools for the HCP Log Interaction agent.

Each tool is declared with @tool purely so LangChain can build a JSON
schema to hand to the Groq LLM for function-calling. The *schemas* below
only describe the arguments the LLM should extract from the user's
message - they intentionally do NOT include the full current form, because
the LLM should only ever emit the fields the user is trying to
add/change. The actual merge with existing form state happens in the
graph's tool-executor node (see graph.py), which calls the matching
`run_<tool>` function with the live form dict.
"""

from typing import Optional
from langchain_core.tools import tool

REQUIRED_FIELDS = ["hcp_name", "date", "interaction_type", "sentiment"]

FIELD_LABELS = {
    "hcp_name": "HCP Name",
    "interaction_type": "Interaction Type",
    "date": "Date",
    "time": "Time",
    "attendees": "Attendees",
    "topics_discussed": "Topics Discussed",
    "materials_shared": "Materials Shared",
    "samples_distributed": "Samples Distributed",
    "sentiment": "Sentiment",
    "outcomes": "Outcomes",
    "follow_up_actions": "Follow-up Actions",
    "notes": "Notes",
}

FOLLOWUP_RULES = {
    "Positive": [
        "Schedule a follow-up meeting in 2 weeks",
        "Send additional product literature",
        "Add HCP to next speaker program invite list",
    ],
    "Neutral": [
        "Share a comparative efficacy one-pager",
        "Schedule a follow-up call in 3-4 weeks",
    ],
    "Negative": [
        "Escalate concerns to medical affairs",
        "Prepare objection-handling material for next visit",
        "Schedule a shorter check-in in 1 week",
    ],
}


# ---------------------------------------------------------------------------
# Tool schemas (bound to the LLM so it knows what it can call)
# ---------------------------------------------------------------------------

@tool
def log_interaction(
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[list[str]] = None,
    samples_distributed: Optional[list[str]] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
) -> str:
    """Create/populate a new HCP interaction from a natural-language description.
    Extract HCP name, interaction type (Meeting/Call/Email/Conference), date,
    time, attendees, topics discussed, materials shared, samples distributed,
    sentiment (Positive/Neutral/Negative), outcomes, and follow-up actions.
    Use this the first time a user describes a visit/meeting with a doctor."""
    return "log_interaction"


@tool
def edit_interaction(
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[list[str]] = None,
    samples_distributed: Optional[list[str]] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Correct or modify ONLY the specific fields the user mentions on an
    already-logged interaction (e.g. 'actually the name was Dr. John').
    Only pass the fields that should change; leave everything else unset."""
    return "edit_interaction"


@tool
def clear_form() -> str:
    """Wipe every field on the form to start a brand new interaction.
    Use when the user says things like 'clear the form' or 'start a new
    interaction'."""
    return "clear_form"


@tool
def summarize_interaction() -> str:
    """Generate a human-readable summary of the CURRENT form contents.
    Use when the user asks to 'summarize' the interaction."""
    return "summarize_interaction"


@tool
def validate_form() -> str:
    """Check whether the current form has all required fields (HCP name,
    date, interaction type, sentiment) and is ready to submit. Use when the
    user asks 'can I submit this?' or 'is this ready?'."""
    return "validate_form"


ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    clear_form,
    summarize_interaction,
    validate_form,
]


# ---------------------------------------------------------------------------
# Real execution logic, invoked by the tool-executor node in graph.py
# ---------------------------------------------------------------------------

def _apply_fields(form: dict, args: dict) -> dict:
    """Merge only the keys the LLM actually supplied (non-None) into form."""
    updated = dict(form)
    for key, value in args.items():
        if value is not None and key in FIELD_LABELS:
            updated[key] = value
    return updated


def _followups_for(form: dict) -> list[str]:
    return FOLLOWUP_RULES.get(form.get("sentiment"), [])


def run_log_interaction(form: dict, args: dict) -> tuple[dict, str]:
    updated = _apply_fields(form, args)
    filled = [FIELD_LABELS[k] for k in args if args.get(k) is not None]
    msg = (
        f"Logged the interaction. Captured: {', '.join(filled)}."
        if filled
        else "I didn't catch enough detail to log anything - could you describe the visit?"
    )
    return updated, msg


def run_edit_interaction(form: dict, args: dict) -> tuple[dict, str]:
    changed = {k: v for k, v in args.items() if v is not None}
    if not changed:
        return form, "I didn't find a specific field to change - which field should I update?"
    updated = _apply_fields(form, changed)
    changes_text = ", ".join(f"{FIELD_LABELS[k]} → {v}" for k, v in changed.items())
    return updated, f"Updated: {changes_text}. Everything else was left as-is."


def run_clear_form(form: dict, args: dict) -> tuple[dict, str]:
    empty = {k: None for k in FIELD_LABELS}
    return empty, "Form cleared. Ready for a new interaction."


def run_summarize_interaction(form: dict, args: dict, llm=None) -> tuple[dict, str]:
    from app.llm import llm as default_llm

    model = llm or default_llm
    prompt = (
        "Write a short, professional field-rep interaction summary from this "
        "data. Use a 'Meeting Summary' header, list each non-empty field on "
        "its own line, and add one closing sentence of overall takeaway. "
        f"Data: {form}"
    )
    result = model.invoke(prompt)
    return form, result.content


def run_validate_form(form: dict, args: dict) -> tuple[dict, str]:
    missing = [FIELD_LABELS[f] for f in REQUIRED_FIELDS if not form.get(f)]
    if missing:
        return form, "Missing fields:\n• " + "\n• ".join(missing)
    return form, "Everything looks good. Ready for submission."


TOOL_RUNNERS = {
    "log_interaction": run_log_interaction,
    "edit_interaction": run_edit_interaction,
    "clear_form": run_clear_form,
    "summarize_interaction": run_summarize_interaction,
    "validate_form": run_validate_form,
}
