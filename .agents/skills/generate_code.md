# Skill: Generate Code

## When to use
Any time you are writing or editing backend (Python) or frontend
(TypeScript/Next.js) code in this repo.

## Style rules — apply to every file, no exceptions

- No comments anywhere in the code. Not docstrings, not inline explanations,
  not TODOs. If the code needs a comment to be understood, rewrite it to be
  clearer instead.
- Use short, obvious variable names (`msg`, `sender`, `score`, `conn`) over
  long descriptive ones. Avoid Hungarian-notation-style or over-qualified
  names.
- Do not extract a helper function for logic that is only used once. Inline
  it at the call site instead. Only factor out a function when it is
  genuinely called from more than one place.
- Write code that reads like it was written directly by a human engineer
  under normal time pressure — not like a generated tutorial. Avoid
  excessive defensive checks, avoid wrapping every block in try/except
  unless the failure mode is real and specific, avoid restating the obvious.
- Match the formatting conventions already present in the file you are
  editing before introducing your own.

## Stack-specific rules

**Python (FastAPI, kafka-python, SQLAlchemy, Hugging Face Transformers)**
- Use type hints on function signatures, not inline comments, to convey intent.
- Do not wrap every Kafka/DB call in a broad `except Exception` — catch the
  specific exception type the library actually raises.
- Verify SQLAlchemy model field names and Pydantic schema fields against the
  actual models before writing queries that reference them.

**TypeScript / Next.js / React Flow**
- Co-locate a component's types with the component unless they are shared
  across more than one file.
- Do not invent React Flow node/edge prop names — check the installed
  `reactflow` version's type definitions if unsure.
- Prefer server components by default; only mark a component `"use client"`
  when it genuinely needs interactivity or browser APIs.

## Before finishing any task
Run the `audit_code.md` skill on what you just wrote before marking the task
complete.
