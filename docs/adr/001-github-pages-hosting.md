# ADR-001: Deploy to GitHub Pages

- Status: Accepted
- Date: 2026-10-11
- Supersedes: TRD.md section 2.6 (Vercel recommended)

## Context
The app is a static frontend and must deploy on a free platform. The TRD recommended Vercel or Netlify.

## Decision
Deploy to GitHub Pages via a GitHub Actions workflow, with Vite `base` set to the repo path.

## Consequences
- Free and tied to the repo; no extra account
- No preview deploys per branch
- Requires `base` configuration and a deploy workflow (Milestone 5)
