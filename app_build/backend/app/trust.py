from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.orm import Session as DbSession
from app.models import TrustEdge

INITIAL_SCORE = 0.5
NORMAL_BOOST = 0.02
THREAT_PENALTY = 0.15
DECAY_FLOOR = 0.05
FIRST_TIME_THRESHOLD = 0
RARE_PAIR_THRESHOLD = 3


def get_edge(db: DbSession, src_id, tgt_id) -> TrustEdge | None:
    return db.execute(
        select(TrustEdge).where(
            and_(TrustEdge.source_id == src_id, TrustEdge.target_id == tgt_id)
        )
    ).scalar_one_or_none()


def update_trust(db: DbSession, src_id, tgt_id, threat_score: float, flagged: bool) -> dict:
    edge = get_edge(db, src_id, tgt_id)
    first_time = edge is None

    if first_time:
        edge = TrustEdge(
            source_id=src_id,
            target_id=tgt_id,
            score=INITIAL_SCORE,
            interaction_count=0,
        )
        db.add(edge)

    edge.interaction_count += 1
    edge.last_interaction = datetime.now(timezone.utc)

    if flagged:
        edge.score = max(edge.score - THREAT_PENALTY * (1 + threat_score), DECAY_FLOOR)
    else:
        edge.score = min(edge.score + NORMAL_BOOST, 1.0)

    rare = edge.interaction_count <= RARE_PAIR_THRESHOLD
    anomaly = first_time or rare or edge.score < 0.3

    return {
        "first_time": first_time,
        "rare_pair": rare,
        "anomaly": anomaly,
        "trust_score": round(edge.score, 4),
        "interaction_count": edge.interaction_count,
    }


def get_graph(db: DbSession) -> list[TrustEdge]:
    return list(db.execute(
        select(TrustEdge).order_by(TrustEdge.last_interaction.desc())
    ).scalars().all())


def get_agent_edges(db: DbSession, agent_id) -> list[TrustEdge]:
    return list(db.execute(
        select(TrustEdge).where(
            (TrustEdge.source_id == agent_id) | (TrustEdge.target_id == agent_id)
        ).order_by(TrustEdge.last_interaction.desc())
    ).scalars().all())
