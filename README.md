# AI-First CRM — HCP Module: Log Interaction Screen

An AI-first "Log Interaction" screen for pharma field reps. The screen is a
**split view**:

- **Left panel** — the Interaction Details form: HCP Name, Interaction Type,
  Date, Time, Attendees, Topics Discussed, Materials Shared, Samples
  Distributed, Observed/Inferred HCP Sentiment, Outcomes, Follow-up
  Actions, an AI Suggested Follow-ups panel, and Submit.
- **Right panel** — a conversational AI assistant ("Log interaction via
  chat").

The form is **never edited directly by the user** — every field change goes
through the AI assistant, which is a **LangGraph agent** backed by a **Groq
LLM (`gemma2-9b-it`)**. The agent decides which of five tools to call based
on what the rep types in the chat, and the tool's result is what actually
updates the form. Changed fields flash briefly in the UI so it's obvious the
AI made the edit, not the user.

## Why this design

A field rep should be able to describe a visit the way they'd tell a
colleague about it ("saw Dr. Smith today, went well, left some brochures")
and have the CRM do the structuring work. The structured form still exists
so the data is clean, auditable, and submittable — it's just populated by
the agent instead of by manual typing.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React + Redux Toolkit (Vite) |
| Backend | Python + FastAPI |
| AI agent framework | LangGraph |
| LLM | Groq `gemma2-9b-it` (via `langchain-groq`) |
| Database | MySQL (SQLAlchemy ORM + PyMySQL; Postgres also works, see below) |
| Font | Google Inter |

## The LangGraph agent

Every chat message goes through a two-node graph:

```
User message
     │
     ▼
 ┌─────────┐   tool_calls present   ┌────────────────┐
 │  agent  │ ─────────────────────► │ tool_executor  │
 │ (LLM)   │ ◄───────────────────── │ (runs tool,    │
 └─────────┘   loops back for       │ mutates form)  │
     │          final reply         └────────────────┘
     │ no tool_calls
     ▼
   END → reply sent to UI
```

The **agent node** calls Groq's `gemma2-9b-it` with the chat history, a
snapshot of the current form (so it has context for edits), and the five
tool schemas bound via `bind_tools`. The **tool_executor node** is custom
(not LangGraph's prebuilt `ToolNode`) because each tool needs to read and
merge into the *live* form state rather than being a stateless function —
so it dispatches by tool name to a small runner in `app/tools.py`, applies
only the fields the LLM actually extracted, and loops back to the agent so
the LLM can phrase a natural confirmation.

### The five tools

1. **`log_interaction`** — Parses a natural-language description of a visit
   (e.g. *"Today I met with Dr. Smith, a meeting, and discussed Product X
   efficiency. Sentiment was positive, and I shared brochures."*) and
   extracts HCP name, interaction type, date, time, attendees, topics
   discussed, materials shared, samples distributed, sentiment, outcomes,
   and follow-up actions, using the LLM's own entity extraction via
   function-calling. Only the fields the model finds are written to the
   form. A rule-based "AI Suggested Follow-ups" list is also generated from
   the sentiment.
2. **`edit_interaction`** — Takes a correction (e.g. *"the name was actually
   Dr. John and the sentiment is negative"*) and updates **only** the
   fields mentioned, leaving everything else on the form untouched.
3. **`clear_form`** — Resets every field to empty so the rep can start a new
   interaction ("start a new interaction" / "clear all fields").
4. **`summarize_interaction`** — Reads the current form and makes a second
   LLM call to produce a short "Meeting Summary" write-up.
5. **`validate_form`** — Checks that HCP name, date, interaction type, and
   sentiment are all present before submission, and reports exactly what's
   missing if not.

If the model's message isn't about the form (small talk, a question), the
agent just replies without calling a tool.

## Project structure

```
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router mounting
│   │   ├── config.py          # env var loading
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # Interaction ORM model
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── state.py           # LangGraph AgentState (TypedDict)
│   │   ├── llm.py             # ChatGroq client (gemma2-9b-it)
│   │   ├── tools.py           # 5 tool schemas + real execution logic
│   │   ├── graph.py           # LangGraph StateGraph wiring
│   │   └── routes/
│   │       ├── chat.py        # POST /api/chat — drives the agent
│   │       └── interactions.py# POST/GET /api/interactions — persistence
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── store/              # Redux slices: form, chat
    │   ├── components/         # Layout, InteractionForm, ChatPanel
    │   ├── api/client.js        # fetch wrapper for the backend
    │   └── main.jsx / App.jsx
    ├── index.html               # loads Google Inter
    └── package.json
```

## Running it locally

### 1. Database (MySQL)

```sql
CREATE DATABASE hcp_crm;
```

### 2. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set GROQ_API_KEY (get one at https://console.groq.com/keys)
# and DATABASE_URL, e.g.
# mysql+pymysql://root:password@localhost:3306/hcp_crm
uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on first run via SQLAlchemy.

To use Postgres instead, set `DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/hcp_crm`
and swap `pymysql`/`cryptography` for `psycopg2-binary` in `requirements.txt`.

The API is now at `http://localhost:8000`, docs at `/docs`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. If your backend runs somewhere other than
`localhost:8000`, set `VITE_API_URL` in a `.env` file in `frontend/`.

## Try it

1. Type: *"I met Dr. Smith today, it was a meeting, we discussed Product X
   efficiency, sentiment was positive, and I shared brochures."* →
   `log_interaction` fires, the form fills in and flashes, and an AI
   Suggested Follow-ups list appears.
2. Type: *"Actually the name was Dr. John and the sentiment is negative."*
   → `edit_interaction` fires, only those two fields change (and the
   follow-up suggestions update to match the new sentiment).
3. Type: *"Summarize today's interaction."* → `summarize_interaction`
   fires, agent writes a short recap.
4. Type: *"Can I submit this?"* → `validate_form` fires, confirms
   readiness or lists what's missing.
5. Type: *"Start a new interaction."* → `clear_form` fires, everything
   resets.
6. Click **Submit Interaction** once required fields are filled — this
   persists the record to MySQL via `POST /api/interactions`.
