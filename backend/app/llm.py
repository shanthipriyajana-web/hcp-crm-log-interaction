from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY, GROQ_MODEL

# gemma2-9b-it is the required model. llama-3.3-70b-versatile can be swapped
# in via GROQ_MODEL if you need stronger tool-calling behavior.
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0,
)
