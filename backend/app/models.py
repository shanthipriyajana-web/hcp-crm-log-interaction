from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON

from app.database import Base


class Interaction(Base):
    """A submitted HCP interaction record."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(64), nullable=True)  # Meeting / Call / Email / Conference
    date = Column(String(64), nullable=True)  # "Today", "19-04-2025", etc.
    time = Column(String(32), nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(JSON, nullable=True)  # list[str]
    samples_distributed = Column(JSON, nullable=True)  # list[str]
    sentiment = Column(String(32), nullable=True)  # Positive / Neutral / Negative
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
