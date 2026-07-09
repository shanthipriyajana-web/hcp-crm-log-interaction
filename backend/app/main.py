from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN
from app.database import Base, engine
from app.routes import chat, interactions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-First CRM - HCP Log Interaction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
