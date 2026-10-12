# SentinelMesh — Progress Log

## 2026-10-10 — Project Bootstrap, Infrastructure Setup, and Feature 1 Complete

**Status:** Infrastructure verified and Feature 1 (Centralized Interception Layer) functional and tested end-to-end.

**What was built & verified working:**
1. **Infrastructure (`setup_infra.md`):**
   - Single-node Apache Kafka (KRaft mode, official `apache/kafka:latest`) running via Docker Compose with topics `agent.outbound` and `agent.inbound` initialized.
   - PostgreSQL 16 container running with persistent volume `pgdata`.
   - Alembic migration environment initialized.
   - Secrets managed via [.env](file:///c:/MajorProject/SentinelMesh/.env), which is ignored in [.gitignore](file:///c:/MajorProject/SentinelMesh/.gitignore).
   - FastAPI service running in Docker on port 8000, connected to both Kafka and PostgreSQL. `/health` returning 200 OK.
2. **Feature 1: Centralized Interception Layer:**
   - Database models in [models.py](file:///c:/MajorProject/SentinelMesh/backend/app/models.py) for `agents`, `messages`, and `trust_edges`.
   - Pydantic validation schemas in [schemas.py](file:///c:/MajorProject/SentinelMesh/backend/app/schemas.py) (`MessageIn`, `MessageOut`, `AgentOut`).
   - Kafka client in [kafka_client.py](file:///c:/MajorProject/SentinelMesh/backend/app/kafka_client.py) using `kafka-python` 3.0.11 with resilient background consumer daemon and producer.
   - Core interception loop in [main.py](file:///c:/MajorProject/SentinelMesh/backend/app/main.py): consumes messages from `agent.outbound`, persists entities/messages to PostgreSQL, and re-publishes intercepted messages to `agent.inbound`.
   - Verified end-to-end routing via `POST /api/messages` and direct Kafka console producer on `agent.outbound`; observed messages arriving on `agent.inbound` and recorded in PostgreSQL (`GET /api/messages` and `GET /api/agents`).

## 2026-10-11 — Feature 2: Rule-Based + BERT Detection Engine Complete

**Status:** Feature 2 fully implemented, trained, containerized, and verified end-to-end.

**What was built & verified working:**
1. **Dataset Generation:**
   - Synthetic dataset generator in [generate_dataset.py](file:///c:/MajorProject/SentinelMesh/scripts/generate_dataset.py) producing 1,000 labeled agent messages across 5 classes (`normal`, `injection`, `impersonation`, `exfiltration`, `cascade`) with a 70/15/15 train/val/test split saved to `backend/data/dataset.csv`.
2. **Stage 1: Rule-Based Detection Engine:**
   - Pattern scanner in [rules.py](file:///c:/MajorProject/SentinelMesh/backend/app/rules.py) with regex patterns covering prompt injection, impersonation claims, exfiltration keywords, cascade worms, and suspicious commands.
   - Returns normalized score (0.0 to 1.0), top matching attack category, hit counts, and flagged threshold.
3. **Stage 2: Fine-Tuned BERT Sequence Classifier:**
   - Training pipeline in [train_bert.py](file:///c:/MajorProject/SentinelMesh/backend/app/train_bert.py) fine-tuning `bert-base-uncased` across 4 epochs with AdamW optimizer and linear warmup schedule.
   - Reached **99.0% test accuracy** (F1: 1.00 normal, 1.00 injection, 1.00 impersonation, 0.97 exfiltration, 0.93 cascade). Saved checkpoint and tokenizer artifacts to [backend/model/](file:///c:/MajorProject/SentinelMesh/backend/model).
   - Inference module in [bert_classifier.py](file:///c:/MajorProject/SentinelMesh/backend/app/bert_classifier.py) with lazy-loading and softmax confidence score outputs.
4. **Combined Detection Engine:**
   - Two-stage detector in [detector.py](file:///c:/MajorProject/SentinelMesh/backend/app/detector.py) weighting rule signals and neural confidence, falling back safely if model artifacts or dependencies are absent.
5. **FastAPI & Interception Integration:**
   - Interception handler in [main.py](file:///c:/MajorProject/SentinelMesh/backend/app/main.py) updated: every intercepted outbound message is scored by `analyze()` before persisting to PostgreSQL and publishing to Kafka `agent.inbound` with enriched `threat_score`, `flagged`, and `category`.
   - Added `POST /classify` endpoint for direct text evaluation.
6. **Containerization & End-to-End Verification:**
   - Updated [requirements.txt](file:///c:/MajorProject/SentinelMesh/backend/requirements.txt) with CPU PyTorch and Hugging Face Transformers.
   - Rebuilt and launched `backend` Docker container. Verified `GET /health` (200 OK) and `POST /classify`.
   - Verified live Kafka interception via `POST /api/messages`: confirmed malicious messages correctly flagged (`threat_score` 0.9902, `flagged` true, `category` injection) and benign messages allowed (`threat_score` 0.0085, `flagged` false) in PostgreSQL.
   - Unit and integration tests passed in [test_feature2.py](file:///c:/MajorProject/SentinelMesh/tests/test_feature2.py).

**Audit Results (`audit_code.md`):**
- Zero code comments / docstrings across all modified files (`generate_code.md` compliance).
- Specific exception handling for database and model inference.
- Short variable names throughout.
- Zero Semester 8 references or placeholders.

**Next step:**
- Completed Feature 3. Await confirmation before starting Feature 4: Live Agent Trust Graph Dashboard.

## 2026-10-12 — Feature 3: Trust-Graph Anomaly Detection Complete

**Status:** Feature 3 fully implemented, tested, and verified.

**What was built & verified working:**
1. **Trust Graph Dynamic Engine:**
   - Graph maintenance engine in [trust.py](file:///c:/MajorProject/SentinelMesh/backend/app/trust.py): tracks sender-receiver pairs in `trust_edges`, initializes first-contact edges at `0.5`, applies score boosts (+0.02) for benign messages, applies decay penalties (-0.15 * (1 + threat_score)) for threats, and clamps between floor `0.05` and max `1.0`.
   - Anomaly detection flags first-time interactions (`first_time`), rare communication pairs (`interaction_count <= 3`), and degraded trust edges (`score < 0.3`).
2. **Schema & API Endpoints:**
   - Added `TrustEdgeOut` Pydantic model in [schemas.py](file:///c:/MajorProject/SentinelMesh/backend/app/schemas.py).
   - Added `GET /api/graph` and `GET /api/trust-graph` returning all trust edges with source/target agent names and scores.
   - Added `GET /api/trust-graph/{agent_name}` returning all incoming and outgoing trust edges for a specific agent.
3. **Interception Pipeline Integration:**
   - Updated `handle_outbound` in [main.py](file:///c:/MajorProject/SentinelMesh/backend/app/main.py): every intercepted message updates the trust graph in the same transaction, sets message `flagged = result["flagged"] or trust["anomaly"]`, and includes the enriched `trust` anomaly metadata in the re-published payload on `agent.inbound`.
4. **Verification & Testing:**
   - Comprehensive unit and integration test suite in [test_feature3.py](file:///c:/MajorProject/SentinelMesh/tests/test_feature3.py) passed all checks:
     - `test_first_time_interaction` (PASS)
     - `test_trust_progression_and_rare_threshold` (PASS)
     - `test_threat_penalty_and_floor` (PASS)
     - `test_graph_queries` (PASS)
     - `test_api_endpoints` (PASS)
     - `test_handle_outbound_integration` (PASS)

**Audit Results (`audit_code.md`):**
- Zero code comments / docstrings across all files (`generate_code.md` compliance verified).
- Short variable names and direct typing throughout.
- Specific exception handling for database operations.
- Zero Semester 8 references or placeholders.

**Next step:**
- Completed Feature 3. Proceed to Feature 4: Live Agent Trust Graph Dashboard.

## 2026-10-12 — Feature 4: Live Agent Trust Graph Dashboard Complete

**Status:** Feature 4 fully implemented, built, visually verified, and covered by end-to-end integration tests. All four confirmed Semester 7 features are now complete.

**What was built & verified working:**
1. **Backend Dashboard Endpoints (`backend/app/main.py`):**
   - Added CORS middleware (`http://localhost:3000`).
   - `GET /api/dashboard/graph`: returns React Flow graph payload with `nodes` (agents) and `edges` (trust edges with dynamic stroke colors: `#3DDC97` normal >=0.5, `#E8A33D` anomalous 0.3-0.5, `#E5484D` critical <0.3 with animation).
   - `GET /api/dashboard/stats`: aggregate metrics (`active_agents`, `messages_inspected`, `messages_flagged`, `trust_edges`).
   - `GET /api/dashboard/incidents`: recent flagged messages with timestamp, sender/receiver, threat score, and content snippet.
2. **Next.js + React Flow Frontend (`frontend/`):**
   - Implemented with Next.js (App Router) and `@xyflow/react` v12.
   - Enforced project design style guide from `design_frontend.md`: charcoal background `#0A0E14`, flat surfaces `#12161F`, strict state palette (green `#3DDC97`, amber `#E8A33D`, red `#E5484D`), Inter and JetBrains Mono typography, dense grid layout with sharp borders.
   - Custom hook [useDashboard.js](file:///c:/MajorProject/SentinelMesh/frontend/src/app/hooks/useDashboard.js) polling all 3 endpoints every 4 seconds.
   - Centerpiece [TrustGraph.js](file:///c:/MajorProject/SentinelMesh/frontend/src/app/components/TrustGraph.js) with circular agent node layout, interactive pan/zoom, and color-coded trust edges.
   - [StatsPanel.js](file:///c:/MajorProject/SentinelMesh/frontend/src/app/components/StatsPanel.js) right sidebar and [IncidentFeed.js](file:///c:/MajorProject/SentinelMesh/frontend/src/app/components/IncidentFeed.js) bottom panel with monospace timestamps and score coloring.
   - Production Dockerfile created for `frontend` and added as service in [docker-compose.yml](file:///c:/MajorProject/SentinelMesh/docker-compose.yml).
3. **Verification & Testing:**
   - Production build verified: `next build` compiled cleanly in Turbopack.
   - Live dev server verified at `http://localhost:3000` (HTTP 200 OK) and visual verification captured via browser screenshot.
   - Integration test suite in [test_feature4.py](file:///c:/MajorProject/SentinelMesh/tests/test_feature4.py) passed all 4 test cases (`test_dashboard_stats_empty`, `test_dashboard_stats_populated`, `test_dashboard_graph`, `test_dashboard_incidents`).
   - All 12 test cases across Features 2, 3, and 4 passing.

**Audit Results (`audit_code.md`):**
- Strict compliance with `generate_code.md`: zero comments or docstrings in all new/modified files.
- Short variable names and direct implementation.
- Zero Semester 8 references or placeholders.

**Next step:**
- Full Semester 7 scope is complete. Await user instructions for review or next milestone.

