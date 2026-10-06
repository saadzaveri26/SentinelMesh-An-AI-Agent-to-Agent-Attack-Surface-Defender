# Skill: Design Frontend

## When to use
Before writing any UI code, and before generating any prompt for an external
design tool (e.g. Stitch) for this project.

## Setup — run once, before any dashboard work begins

This project uses Taste Skill (https://www.tasteskill.dev) as the enforced
anti-slop frontend framework, instead of relying on ad-hoc instructions
inside this file. Install these three skills in the project root:

```
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
npx skills add https://github.com/Leonxlnx/taste-skill --skill "stitch-skill"
npx skills add https://github.com/Leonxlnx/taste-skill --skill "output-skill"
```

- `design-taste-frontend` — the core anti-slop ruleset (brief inference,
  color/shape/theme locks, hero discipline, the full ban list on things like
  AI-purple gradients, fake div-based dashboards, three-equal-card rows,
  decorative status dots, em-dashes).
- `stitch-skill` — bridges this project's design rules into a Stitch-ready
  prompt and an optional `DESIGN.md` export, so prompts generated for Stitch
  and code generated in Antigravity stay in sync instead of drifting apart.
- `output-skill` — blocks placeholder sections, skipped work, and
  half-finished output. Keep this on for the whole project, not just UI work.

Each command adds a `SKILL.md` to the project root. Antigravity reads it
automatically — no further configuration needed.

## Project-specific style guide — paste this at the top of the generated `SKILL.md`

Taste Skill explicitly supports this: a pasted project style guide becomes
the dominant source of truth over its own defaults. Paste the block below
verbatim at the top of the installed `SKILL.md` file before any dashboard
work starts.

```
PROJECT STYLE GUIDE — SentinelMesh (dominant source of truth)

This is a security operations console, not a marketing site or SaaS
dashboard. The user is a security engineer monitoring live AI agent traffic.
Favor information density and technical credibility over decoration.

Color:
- Background: near-black charcoal #0A0E14 (not pure black, not navy)
- Panel surfaces: #12161F, flat, no gradient
- Normal/allowed state: desaturated signal green #3DDC97
- Anomalous/flagged state: amber #E8A33D
- Blocked/critical state: hard red #E5484D
- Primary text: off-white #E6E8EC — secondary text: muted grey #8A94A6
- No purple, no indigo, no gradient fills anywhere

Typography:
- UI labels and headings: humanist sans-serif, Inter or IBM Plex Sans,
  normal weight by default
- All technical data (agent IDs, timestamps, payloads, confidence scores,
  topic names): monospace, JetBrains Mono or IBM Plex Mono

Layout:
- Sharp corners, 0-4px radius maximum, thin 1px borders — no shadows, no glow
- Dense multi-panel grid, not a single centered card
- The live trust graph is the visual centerpiece; stats and incident feed
  are secondary, smaller, text-forward panels around it

Scope note: this is a real functional product, not a marketing mockup — the
"no fake div-based dashboards" ban refers to decorative fake UI on landing
pages, not this actual application.
```

## Relationship to other skills
`build_dashboard.md` applies this skill (and the installed Taste Skill
rules) for all Feature 4 UI decisions. If a future Semester 8 feature
touches the UI, it must follow the same installed skills and style guide —
do not introduce a second, divergent design direction.
