# Workflow: Start Cycle

## Purpose
Run this at the beginning of every work session on SentinelMesh, before
touching any code.

## Steps

1. **Load persona and ground rules**
   Apply `ask_sentinelmesh_persona.md`. Confirm the active scope is
   Semester 7 only.

2. **Read project state**
   - Read `PROGRESS_LOG.md` in the repo root. If it does not exist, create
     it with a single entry: "Project bootstrap."
   - Read `tech_stack.md` and `Technical_Specification.md` if present. If
     either is missing, create it from the confirmed stack and feature list
     in `agents.md` before proceeding.

3. **Pick the next task**
   - From the Semester 7 feature list in `agents.md`, identify the first
     feature not yet marked complete in `PROGRESS_LOG.md`.
   - Features build in order: Centralized Interception Layer → Rule-Based +
     BERT Detection Engine → Trust-Graph Anomaly Detection → Live Agent
     Trust Graph Dashboard. Do not start a later feature before the one
     before it is functional, even partially — each one depends on the
     plumbing the previous one establishes.
   - If the next task depends on infrastructure that isn't set up yet,
     apply `setup_infra.md` first.

4. **Do the work**
   - Apply `generate_code.md` while writing code.
   - Apply `design_frontend.md` (Taste Skill setup) for any UI work.
   - Apply `build_dashboard.md` specifically when working on Feature 4.

5. **Before ending the session**
   - Apply `audit_code.md` on everything written this session.
   - Update `PROGRESS_LOG.md`: what was built, what was verified working,
     what is left incomplete and why, and the exact next step for the
     following session. Be specific — "detection engine partially done"
     is not useful; "BERT classifier trained and serving at /classify,
     not yet wired into the Kafka consumer" is.
   - Do not mark a feature complete unless it was actually run and
     verified, not just written.
