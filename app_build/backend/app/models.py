import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    bert_score: Mapped[float] = mapped_column(Float, default=0.0)
    rule_hits: Mapped[dict] = mapped_column(JSON, default=dict)
    anomaly_flags: Mapped[list] = mapped_column(JSON, default=list)
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)

    sender: Mapped["Agent"] = relationship(foreign_keys=[sender_id])
    receiver: Mapped["Agent"] = relationship(foreign_keys=[receiver_id])


class TrustEdge(Base):
    __tablename__ = "trust_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    score: Mapped[float] = mapped_column(Float, default=0.5)
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    last_interaction: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    source: Mapped["Agent"] = relationship(foreign_keys=[source_id])
    target: Mapped["Agent"] = relationship(foreign_keys=[target_id])
