# SentinelMesh — Technical Specification

## Overview
SentinelMesh intercepts communication between autonomous AI agents, detects
manipulation attempts (prompt injection, social engineering, authority
spoofing), and models trust between agents over time.

## Active scope: Semester 7

### Feature 1: Centralized Interception Layer
Kafka-based message routing. All agent-to-agent messages pass through
SentinelMesh before delivery. Two Kafka topics:
- `agent.outbound` — messages from a sending agent
- `agent.inbound` — messages delivered to a receiving agent

The FastAPI service acts as both Kafka consumer (reading from `agent.outbound`)
and producer (writing to `agent.inbound` after processing). This gives us a
single point to inspect, log, and optionally block any message.

### Feature 2: Rule-Based + BERT Detection Engine
Two-stage detection on every intercepted message:
1. Cheap rule-based checks (regex patterns for known injection templates,
   authority-claim keywords, suspicious formatting)
2. A fine-tuned BERT classifier for pattern-level detection of manipulation
   that rules alone miss

Messages are scored. High-confidence threats are flagged or blocked; ambiguous
ones are logged for review.

### Feature 3: Trust-Graph Anomaly Detection
PostgreSQL-backed record of which agents normally communicate with which.
Each agent pair has a trust score based on historical interaction frequency
and outcomes. First-time or rare communication pairs are flagged as anomalous.

### Feature 4: Live Agent Trust Graph Dashboard
Next.js + React Flow frontend. Polls a FastAPI endpoint for current graph
state — nodes are agents, edges are trust relationships with scores.
Highlights anomalous or flagged connections in real time.

## Explicitly out of scope (Semester 8)
- Claude API escalation for ambiguous detections
- Docker sandboxed execution of suspicious actions
- Human-in-the-loop escalation UI
- Live Attack Injection Console
- "Ask Why" conversational incident explanation
- Attack benchmark and evaluation reporting

## Architecture

```
Agent A ──► Kafka (agent.outbound)
                │
                ▼
          FastAPI Service
          ├─ Rule checks
          ├─ BERT classifier
          ├─ Trust graph lookup (PostgreSQL)
          └─ Log / flag / block decision
                │
                ▼
          Kafka (agent.inbound) ──► Agent B

          Next.js Dashboard ◄── polls /api/graph ── FastAPI
```

## Data model (PostgreSQL)

### agents
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR | Unique agent identifier |
| created_at | TIMESTAMP | |

### messages
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| sender_id | UUID | FK → agents.id |
| receiver_id | UUID | FK → agents.id |
| content | TEXT | Raw message body |
| timestamp | TIMESTAMP | |
| threat_score | FLOAT | Combined detection score |
| flagged | BOOLEAN | Whether message was blocked/flagged |

### trust_edges
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| source_id | UUID | FK → agents.id |
| target_id | UUID | FK → agents.id |
| score | FLOAT | Current trust score |
| interaction_count | INTEGER | |
| last_interaction | TIMESTAMP | |

## API endpoints (FastAPI)

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Service health check |
| POST | /api/messages | Submit a message for interception |
| GET | /api/messages | List recent messages with scores |
| GET | /api/graph | Current trust graph state for dashboard |
| GET | /api/agents | List registered agents |
