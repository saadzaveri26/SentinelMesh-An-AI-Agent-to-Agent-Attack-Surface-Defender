from pydantic import BaseModel
from datetime import datetime


class MessageIn(BaseModel):
    sender: str
    receiver: str
    content: str


class MessageOut(BaseModel):
    id: str
    sender: str
    receiver: str
    content: str
    timestamp: datetime
    bert_score: float
    rule_hits: dict | list | int | None = None
    anomaly_flags: list | None = None
    flagged: bool

    model_config = {"from_attributes": True}


class AgentOut(BaseModel):
    id: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TrustEdgeOut(BaseModel):
    id: str
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    score: float
    interaction_count: int
    last_interaction: datetime

    model_config = {"from_attributes": True}
