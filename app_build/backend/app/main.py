from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine, get_db, Base
from app.models import Agent, Message, TrustEdge
from app.schemas import MessageIn, MessageOut, AgentOut, TrustEdgeOut
from app.kafka_client import publish, start_consumer
from app.detector import analyze
from app.trust import update_trust, get_graph, get_agent_edges


def handle_outbound(payload: dict):
    from app.db import Session
    db = Session()
    try:
        sender = db.execute(
            select(Agent).where(Agent.name == payload["sender"])
        ).scalar_one_or_none()
        if not sender:
            sender = Agent(name=payload["sender"])
            db.add(sender)
            db.flush()

        receiver = db.execute(
            select(Agent).where(Agent.name == payload["receiver"])
        ).scalar_one_or_none()
        if not receiver:
            receiver = Agent(name=payload["receiver"])
            db.add(receiver)
            db.flush()

        result = analyze(payload["content"])
        trust = update_trust(db, sender.id, receiver.id, result["score"], result["flagged"])

        anomaly_flags = trust.get("flags", [])
        bert_score = result.get("bert_score", result["score"])

        msg = Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=payload["content"],
            bert_score=bert_score,
            rule_hits=result["rule_detail"].get("hits", {}),
            anomaly_flags=anomaly_flags,
            flagged=result["flagged"],
        )
        db.add(msg)
        db.commit()

        if not msg.flagged:
            publish("agent.inbound", {
                "id": str(msg.id),
                "sender": payload["sender"],
                "receiver": payload["receiver"],
                "content": payload["content"],
                "bert_score": msg.bert_score,
                "rule_hits": msg.rule_hits,
                "anomaly_flags": msg.anomaly_flags,
                "flagged": msg.flagged,
                "category": result["category"],
                "trust": trust,
                "timestamp": msg.timestamp.isoformat(),
            })
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(a: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_consumer(["agent.outbound"], "sentinel-intercept", handle_outbound)
    yield


app = FastAPI(title="SentinelMesh", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


class ClassifyIn(BaseModel):
    content: str


@app.post("/classify")
def classify_message(body: ClassifyIn):
    return analyze(body.content)


@app.post("/api/messages")
def send_message(body: MessageIn):
    publish("agent.outbound", body.model_dump())
    return {"status": "accepted", "message": body.model_dump()}


@app.get("/api/messages", response_model=list[MessageOut])
def list_messages(limit: int = 50, db: DbSession = Depends(get_db)):
    rows = db.execute(
        select(Message).order_by(Message.timestamp.desc()).limit(limit)
    ).scalars().all()
    out = []
    for m in rows:
        s = db.get(Agent, m.sender_id)
        r = db.get(Agent, m.receiver_id)
        out.append(MessageOut(
            id=str(m.id),
            sender=s.name if s else "unknown",
            receiver=r.name if r else "unknown",
            content=m.content,
            timestamp=m.timestamp,
            bert_score=m.bert_score,
            rule_hits=m.rule_hits,
            anomaly_flags=m.anomaly_flags,
            flagged=m.flagged,
        ))
    return out


@app.get("/api/agents", response_model=list[AgentOut])
def list_agents(db: DbSession = Depends(get_db)):
    rows = db.execute(select(Agent).order_by(Agent.name)).scalars().all()
    return [AgentOut(id=str(a.id), name=a.name, created_at=a.created_at) for a in rows]


@app.get("/api/trust-graph", response_model=list[TrustEdgeOut])
@app.get("/api/graph", response_model=list[TrustEdgeOut])
def trust_graph(db: DbSession = Depends(get_db)):
    rows = get_graph(db)
    return [
        TrustEdgeOut(
            id=str(e.id),
            source_id=str(e.source_id),
            source_name=e.source.name if e.source else "unknown",
            target_id=str(e.target_id),
            target_name=e.target.name if e.target else "unknown",
            score=e.score,
            interaction_count=e.interaction_count,
            last_interaction=e.last_interaction,
        )
        for e in rows
    ]


@app.get("/api/trust-graph/{agent_name}", response_model=list[TrustEdgeOut])
def agent_trust(agent_name: str, db: DbSession = Depends(get_db)):
    agent = db.execute(
        select(Agent).where(Agent.name == agent_name)
    ).scalar_one_or_none()
    if not agent:
        return []
    rows = get_agent_edges(db, agent.id)
    return [
        TrustEdgeOut(
            id=str(e.id),
            source_id=str(e.source_id),
            source_name=e.source.name if e.source else "unknown",
            target_id=str(e.target_id),
            target_name=e.target.name if e.target else "unknown",
            score=e.score,
            interaction_count=e.interaction_count,
            last_interaction=e.last_interaction,
        )
        for e in rows
    ]


@app.get("/api/dashboard/graph")
def dashboard_graph(db: DbSession = Depends(get_db)):
    agents = db.execute(select(Agent).order_by(Agent.name)).scalars().all()
    edges = get_graph(db)

    nodes = [
        {
            "id": str(a.id),
            "data": {"label": a.name},
            "position": {"x": i * 200, "y": (i % 3) * 150},
        }
        for i, a in enumerate(agents)
    ]

    rf_edges = []
    for e in edges:
        if e.score >= 0.5:
            color = "#3DDC97"
        elif e.score >= 0.3:
            color = "#E8A33D"
        else:
            color = "#E5484D"

        rf_edges.append({
            "id": str(e.id),
            "source": str(e.source_id),
            "target": str(e.target_id),
            "label": f"{e.score:.2f}",
            "animated": e.score < 0.3,
            "style": {"stroke": color, "strokeWidth": 2},
            "data": {
                "score": e.score,
                "interaction_count": e.interaction_count,
                "last_interaction": e.last_interaction.isoformat(),
                "source_name": e.source.name if e.source else "unknown",
                "target_name": e.target.name if e.target else "unknown",
            },
        })

    return {"nodes": nodes, "edges": rf_edges}


@app.get("/api/dashboard/stats")
def dashboard_stats(db: DbSession = Depends(get_db)):
    agent_count = db.execute(select(func.count(Agent.id))).scalar() or 0
    msg_count = db.execute(select(func.count(Message.id))).scalar() or 0
    flagged_count = db.execute(
        select(func.count(Message.id)).where(Message.flagged == True)
    ).scalar() or 0
    edge_count = db.execute(select(func.count(TrustEdge.id))).scalar() or 0

    return {
        "active_agents": agent_count,
        "messages_inspected": msg_count,
        "messages_flagged": flagged_count,
        "trust_edges": edge_count,
    }


@app.get("/api/dashboard/incidents")
def dashboard_incidents(limit: int = 20, db: DbSession = Depends(get_db)):
    rows = db.execute(
        select(Message)
        .where((Message.flagged == True) | (Message.anomaly_flags.is_not(None)))
        .order_by(Message.timestamp.desc())
        .limit(limit)
    ).scalars().all()

    out = []
    for m in rows:
        is_flagged = bool(m.flagged)
        flags = m.anomaly_flags or []
        if not is_flagged and not flags:
            continue
        s = db.get(Agent, m.sender_id)
        r = db.get(Agent, m.receiver_id)
        flag_name = flags[0] if len(flags) > 0 else None
        out.append({
            "id": str(m.id),
            "timestamp": m.timestamp.isoformat(),
            "sender": s.name if s else "unknown",
            "receiver": r.name if r else "unknown",
            "bert_score": m.bert_score,
            "threat_score": m.bert_score,
            "flagged": is_flagged,
            "anomaly_flags": flags,
            "flag_name": flag_name,
            "content_preview": m.content[:120],
        })
    return out
