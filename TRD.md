# Technical Requirements Document — Historical Events Map (MVP)

## 1. Architecture Overview

This is a **frontend-only application** with static data.

- No backend
- No database
- No authentication

## 2. Core Technology Stack

### 2.1 Frontend Framework (choose one)

Recommended:

- React (Vite setup recommended)

---

### 2.2 Build Tool

- Vite

### 2.3 Mapping Library (critical decision)

- Leaflet

### 2.4 Styling

- CSS Modules (simplest)

### 2.5 Data Storage (MVP)

- Static JSON file inside project:
  - `/data/events.json`

### 2.6 Deployment

- GitHub Pages via GitHub Actions (see `docs/adr/001-github-pages-hosting.md`)
- Free, git-based, minimal setup

---

## 3. Project Structure

Keep it minimal and predictable:

```
src/
  components/
    Map/
    EventPopup/
    Filters/
  data/
    events.json
  hooks/
  utils/
  App.jsx
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
  "description": "string"
}
```

(Updated per `docs/adr/002-flexible-date-schema.md`.)

Rules:

- Year is required; month and day are optional (day requires month)
- Coordinates must match selected city boundary
- Max 20 events for MVP

---

## 5. Tooling (Developer Experience)

### Required

- Node.js (latest LTS)
- npm or pnpm (pnpm recommended)

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
- No external APIs for data
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
- AI-generated historical datasets
- Agent-based content pipeline
- Timeline visualization mode
- Category filters (war, architecture, politics)

---

## 10. Key Technical Decision Summary

You are committing to:

- React + Vite
- Leaflet maps
- Static JSON data
- No backend
- GitHub Pages deployment
- npm as package manager
