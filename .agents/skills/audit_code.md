# Skill: Audit Code

## When to use
After generating or editing any non-trivial piece of code, before marking a
task as done, and before any commit.

## What to check, in order

**1. Correctness against the actual codebase**
- Does every imported function/class actually exist at that path? Open the
  file and confirm — do not assume from the name alone.
- Do Kafka topic names, PostgreSQL table/column names, and API route paths
  match what is already defined elsewhere in the repo?
- Does this change break an existing caller? Search the repo for other
  usages before renaming or changing a signature.

**2. Security hygiene (this project is a security tool — hold it to its own
standard)**
- No API keys, DB credentials, or secrets hardcoded anywhere. They must come
  from environment variables loaded via `.env`, and `.env` must stay in
  `.gitignore`.
- Any input coming from an agent message (Kafka payload) must be validated
  against the Pydantic schema before it touches business logic — never
  trust a field exists or has the expected type without validation.
- SQL queries go through SQLAlchemy's parameterized query interface, never
  raw string formatting.

**3. Scope discipline**
- Confirm nothing in this change references or scaffolds a Semester 8
  feature (Claude escalation, sandboxing, attack console, "Ask Why",
  benchmarking). If it does, remove it and flag this to the user.

**4. Style compliance**
- Re-check against `generate_code.md`: no comments, short variable names,
  no single-use helper functions, formatting consistent with the rest of
  the file.

## Output
State plainly what you checked and what, if anything, you changed as a
result. If you found nothing wrong, say so — do not invent a minor issue
just to appear thorough.
