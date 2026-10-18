## 1. Product Overview

The Historical Events Map is a web application that allows users to explore historical events tied to a specific geographic location. Events are displayed as markers on a map and can be filtered by date or date range.

The MVP focuses on a single city and a limited dataset to provide a simple, interactive way to discover historical context spatially.

---

## 2. Target Users (Personas)

### Primary User: Curious Explorer

- Interested in history and geography
- Wants to explore historical events spatially
- Prefers simple, visual interaction

## 3. User Experience

### Entry Point

- User opens the web app
- Map is centered on the selected city

### Core Interaction Flow

1. User sees markers on the map representing historical events
2. User clicks on a marker
3. A side panel displays:
   - Event title
   - Date
   - Description
   - AI-generated summary, image with attribution, and a link to the source article, when available

### Filtering Flow

1. User selects a date or date range
2. Map updates to show only relevant events

### UX Principles

- Minimal UI
- Fast interaction
- No onboarding or instructions required
- Focus on exploration

---

## 4. User Stories

### Core Stories

- As a user, I want to see historical events on a map so I can explore them geographically
- As a user, I want to click on a marker to view event details
- As a user, I want to filter events by date range so I can focus on a specific time period

---

## 5. Functional Requirements

### Map

- Display map centered on a predefined city
- Render markers for each event

### Event Interaction

- Clicking a marker displays event details
- Only one event detail view visible at a time

### Filtering

- Provide date range input (start and end)
- Filter events dynamically based on selected range
- Provide a reset control and an empty state when nothing matches

### Data Handling

- Load events from a static JSON file
- Prepare the JSON offline from Wikidata/Wikipedia with local scripts and local AI summaries; the app itself makes no external data calls
- Ensure all events follow a consistent schema

---

## 6. Milestones

### Milestone 1: Setup & Map

- Initialize project
- Render map centered on chosen city

### Milestone 2: Data Integration

- Create initial dataset (10–20 events)
- Load and display markers

### Milestone 3: Interaction

- Implement marker click behavior
- Display event details

### Milestone 4: Filtering

- Add date range filter
- Update visible markers based on filter

### Milestone 5: Data Pipeline

- Generate the Xi'an dataset (max 20 events) from Wikidata and Wikipedia with Python scripts
- Manual review of the output

### Milestone 6: Summaries & Images

- Generate AI summaries locally (Ollama + Qwen3)
- Show summary, image with attribution and source links in the side panel

### Milestone 7: Finalization

- Basic UI cleanup
- Deploy application

---

## 7. Technical Requirements

(See separate Technical Specification document)

Summary:

- Frontend-only application
- Static data source (JSON)
- Map rendering library required
- Must be deployable on a free hosting platform

---

## 8. Constraints

- Time: ~12 hours total development time
- Scope limited to MVP features only
- No backend or database
- Limited dataset (max 20 events)
- Must prioritize simplicity over completeness

---

## 9. Out of Scope (MVP)

- Multiple cities
- User accounts or personalization
- Fetching data from APIs at runtime
- Category filtering
- Advanced filtering (categories, tags, etc.)
- Timeline visualization
- Mobile optimization beyond basic responsiveness

---

## 10. Success Criteria

- Map renders correctly with event markers
- At least 10 events displayed
- Marker interaction works reliably
- Date filtering functions as expected
- Events show source links; summaries and images appear when available and missing ones do not break the panel
- Application is deployed and accessible

---

## 11. Risks

- Overcomplicating the implementation
- Spending excessive time on data accuracy
- Delays due to unfamiliar map libraries
- AI summaries containing factual errors
- Image licensing and attribution
- Local hardware too weak for the summary model

Mitigation:

- Keep dataset small
- Timebox all tasks
- Summaries restricted to the source text, sampled for review, always shown with a source link
- Show only images with attribution; check model hardware requirements before installing
- Prioritize working functionality over polish
