# Skill: Build Dashboard (Feature 4 — Live Agent Trust Graph Dashboard)

## When to use
Implementing the Semester 7 dashboard feature specifically. Before starting,
confirm the Taste Skill setup in `design_frontend.md` has been installed and
that the project style guide has been pasted into the generated `SKILL.md`
— do not proceed on default/generic styling if that step was skipped.

## Scope for this phase
Only the baseline live trust graph, stats, and incident feed. Do not add the
attack injection console or the "Ask Why" chat panel — both are Semester 8.

## Implementation steps

1. **Backend endpoint (FastAPI)**
   - Add a route that reads the current trust-graph state from PostgreSQL
     (sender, receiver, message_count, last_seen, anomalous flag) and returns
     it as `{ nodes: [...], edges: [...] }`.
   - Add a second route returning recent entries from the message/incident
     log for the incident feed.
   - Add a third route returning aggregate counts (active agents, messages
     inspected, flagged count) for the stats panel.
   - Confirm actual column names in the SQLAlchemy models before writing
     these queries — do not assume a schema.

2. **Frontend data fetching (Next.js)**
   - Poll the graph-state endpoint on an interval (start with 3–5 seconds;
     do not implement WebSockets for this phase unless explicitly asked —
     polling is sufficient for Semester 7 scope).
   - Keep fetching logic in a small hook, not scattered across components.

3. **Graph rendering (React Flow)**
   - Map each agent to a node, each communicating pair to an edge.
   - Edge color follows the state palette from `design_frontend.md`: green
     for normal, amber for anomalous, red for blocked — never use React
     Flow's default edge styling unmodified.
   - Verify the installed `reactflow` version's node/edge type props before
     using them; do not assume prop names from memory.

4. **Incident feed and stats panel**
   - Render as compact, monospace-forward list items per
     `design_frontend.md` — timestamp, sender→receiver, decision, in that
     order.
   - Keep these as secondary panels around the graph, not competing with it
     for visual weight.

5. **Verify before marking done**
   - Confirm the dashboard reflects a real state change: manually insert a
     new trust_graph row or trigger a flagged message and confirm the UI
     updates within one polling interval.
   - Run `audit_code.md` on all new files.
