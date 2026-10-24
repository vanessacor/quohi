# Technical Requirements Document — Historical Events Map (MVP)

## 1. Architecture Overview

This is a **frontend-only application** with static data.

- No backend
- No database
- No authentication
- No external APIs at runtime; data is prepared offline (see `docs/adr/007-build-time-data-pipeline.md`)

## 2. Core Technology Stack

### 2.1 Frontend Framework (choose one)

Recommended:

- React + TypeScript (Vite setup; see `docs/adr/004-typescript.md`)

---

### 2.2 Build Tool

- Vite

### 2.3 Mapping Library (critical decision)

- Leaflet via react-leaflet, isolated behind an adapter (see `docs/adr/005-map-adapter-boundary.md`)

### 2.4 Styling

- CSS Modules (simplest)

### 2.5 Data Storage (MVP)

- Static JSON file inside project:
  - `src/data/events.json`

### 2.6 Data Preparation (build time only)

- Python scripts in `scripts/` (dependencies in `requirements.txt`): Wikidata SPARQL, Wikipedia API, normalize, validate, export `src/data/events.json` (max 20 events)
- AI summaries generated locally with Ollama + Qwen3 (see `docs/adr/008-local-ai-summaries.md`), stored in the JSON; the site never calls a model
- Scripts are developer tools; they are not deployed and not called by the frontend

### 2.7 Deployment

- GitHub Pages via GitHub Actions (see `docs/adr/001-github-pages-hosting.md`)
- Free, git-based, minimal setup

---

## 3. Project Structure

Keep it minimal and predictable:

```
src/
  components/
    Map/
      leaflet/    # only place importing leaflet / react-leaflet
    EventDetails/
    Sidebar/
    Filters/
  config/
  data/
    events.json
  hooks/
  types/
  utils/
  App.tsx
scripts/            # Python data-prep tools (build time only)
requirements.txt
```

No overengineering.

---

## 4. Data Schema (contract for AI + app)

This is critical for your agentic workflow.

```json id="t7xk91"
{
  "id": "string",
  "title": "string",
  "year": "integer (negative = BCE)",
  "month": "integer 1-12, optional",
  "day": "integer 1-31, optional",
  "endYear": "integer, optional",
  "lat": "number",
  "lng": "number",
  "description": "string",
  "locationName": "string, optional",
  "summary": "string, optional",
  "image": { "url": "string", "license": "optional", "attribution": "optional" },
  "sources": { "wikipedia": "optional", "wikidata": "optional" }
}
```

(Updated per `docs/adr/002-flexible-date-schema.md` and `docs/adr/009-event-schema-extension.md`.)

Rules:

- Year is required; month and day are optional (day requires month)
- Coordinates must match selected city boundary
- Max 20 events for MVP
- All new fields are optional; the UI must tolerate any of them missing

---

## 5. Tooling (Developer Experience)

### Required

- Node.js (latest LTS)
- npm (see ADR-003)
- Python 3 (data-prep scripts only)
- Ollama with a Qwen3 model for summaries (optional; the site builds without it)

### Recommended

- VS Code
- oxlint (basic, Vite 8 template default; see step 2 of milestone-1 plan)
- Prettier (optional but helpful)

### AI Tools (important for your goal)

You will use AI for:

- generating dataset
- refactoring code
- debugging
- converting natural language → JSON

But:

> AI never decides architecture

You do.

---

## 6. Constraints (hard rules)

These are non-negotiable for MVP discipline:

- No backend
- No database
- No authentication
- No multi-city support
- No external APIs at runtime (offline data-prep scripts excepted, ADR-007)
- No complex state management (Redux etc. not needed)

---

## 7. Non-Goals (explicit exclusions)

- Real-time data updates
- User-generated content
- Social features
- Advanced analytics
- Map clustering (optional later)
- Timeline visualization (future iteration)

---

## 8. Performance Expectations

Not a priority, but:

- Initial load < 2 seconds on normal connection
- Smooth map interaction
- < 20 markers rendered

---

## 9. Future Extensions (not now, but important for direction)

- Multi-city support
- Agent-based content pipeline
- Timeline visualization mode
- Category filters (war, architecture, politics)

---

## 10. Key Technical Decision Summary

You are committing to:

- React + Vite
- Leaflet maps
- Static JSON data, prepared offline by Python scripts (ADR-007)
- Local AI summaries, generated at build time (ADR-008)
- No backend
- GitHub Pages deployment
- npm as package manager
