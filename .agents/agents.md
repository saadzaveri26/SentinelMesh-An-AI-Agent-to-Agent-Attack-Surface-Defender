# SentinelMesh — Agent Manifest

## Project
SentinelMesh is an AI agent-to-agent attack surface defender. It intercepts
communication between autonomous AI agents, detects manipulation attempts,
and models trust between agents over time.

## Active scope: Semester 7 ONLY

Do not implement, scaffold, or reference any Semester 8 feature under any
circumstance unless the user explicitly says the words "Semester 8" or "Sem 8"
in the current instruction. If a task seems to require a Sem 8 capability,
stop and ask instead of building a placeholder for it.

**Semester 7 features (build these, in this order):**
1. Centralized Interception Layer — Kafka-based message routing between agents
2. Rule-Based + BERT Detection Engine — cheap rule checks, then a fine-tuned
   BERT classifier for pattern-level detection
3. Trust-Graph Anomaly Detection — PostgreSQL-backed record of which agents
   normally talk to which, flagging first-time/rare pairs
4. Live Agent Trust Graph Dashboard — Next.js + React Flow, polling a FastAPI
   endpoint for live graph state

**Explicitly excluded from this phase (Semester 8 — do not build yet):**
- Claude API escalation for ambiguous detections
- Docker sandboxed execution of suspicious actions
- Human-in-the-loop escalation UI
- Live Attack Injection Console
- "Ask Why" conversational incident explanation
- Attack benchmark and evaluation reporting

## Tech stack (confirmed — do not substitute without asking)
- Messaging: Apache Kafka (Docker)
- Backend: FastAPI (Python)
- Detection: fine-tuned BERT (Hugging Face Transformers)
- Database: PostgreSQL + SQLAlchemy
- Frontend: Next.js + React Flow
- Infra: Docker Compose (local)

## Skills available (`.agents/skills/`)
| Skill | Use when |
|---|---|
| `ask_sentinelmesh_persona.md` | Start of any session — establishes context and ground rules |
| `setup_infra.md` | Setting up Kafka, PostgreSQL, FastAPI, Docker Compose |
| `generate_code.md` | Writing any backend or frontend code |
| `audit_code.md` | After generating a non-trivial chunk of code, before marking a task done |
| `design_frontend.md` | Before or during any dashboard UI work (now built around Taste Skill) |
| `build_dashboard.md` | Implementing Feature 4 specifically |

## Workflow (`.agents/workflows/`)
| Workflow | Use when |
|---|---|
| `startcycle.md` | Beginning of every work session |

## Ground rules
- Never invent an API, library method, or config option you have not verified
  exists. If unsure, say so and check documentation or ask the user.
- Never silently swap a tech-stack choice listed above for an alternative.
- Read `PROGRESS_LOG.md` before starting work; update it before ending a session.
- If `tech_stack.md` or `Technical_Specification.md` do not yet exist in the
  repo root, create them from the confirmed details in this file before
  writing any feature code.
