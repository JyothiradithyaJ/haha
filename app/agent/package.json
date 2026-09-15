# ARCHIVE — BMSIT Academic Resource Hub (Frontend Prototype)

This is the Phase 1 frontend/UI for ARCHIVE, an academic resource platform
for BMS Institute of Technology and Management (BMSIT). It is built with
React, TypeScript, Tailwind CSS and React Router, using mock data only —
no backend, auth, or file storage yet.

## Run it locally

```bash
npm install
npm run dev
```

Then open the printed local URL (usually http://localhost:5173).

## Build for production

```bash
npm run build
npm run preview
```

## Pages

- `/` — Home / Archive (hero, greyed course-name search, 4 colorful category cards, course carousel, bookshelf preview, contribute CTA)
- `/course/:id` — Course resource page with category tabs, upvotes, and an upload modal
- `/bookshelf` — Textbooks (the References category) shown as a real shelf of book spines with hover reveal
- `/honor-roll` — Contributor leaderboard with an upvotes column, department filter, points rules and a points calculator
- `/contribute` — Contribution form (course name, resource type, department, academic year; References accepts a link instead of a file)
- `/resource/:id` — Resource detail / mock PDF view page with an upvote button
- `/terms` — Terms & rules
- `/releases` — Releases & updates changelog

Course codes have been removed from the UI everywhere; browsing and search
are by course name only. Resource categories are Notes, Past Papers,
Extras and References, each with its own accent color (green / orange /
coral / purple).

## Structure

- `src/components/` — shared UI: Header, Footer, SearchOverlay, Carousel, ShelfBook, cards, form fields, tabs, modal, upload dropzone
- `src/pages/` — one file per route
- `src/lib/categoryTheme.ts` — color/label/icon theme for the four resource categories
- `src/data/mockData.ts` — mock BMSIT departments, courses, resources (including reference books) and contributors, structured so it can be swapped for a real API/database later
- `src/data/types.ts` — shared TypeScript types for the data model

## Design system

Editorial "card catalog" aesthetic: warm paper background, oxblood accent,
a serif display face (Source Serif 4) paired with Inter for UI text, and
monospace "call numbers" for department tags — tokens live in
`tailwind.config.js` and `src/index.css`. Each resource category (Notes,
Past Papers, Extras, References) carries its own accent color used across
category cards, badges and icon chips.

## Not included yet (Phase 2)

Firebase/Supabase, real auth, real file storage/upload, admin approval
workflow, real leaderboard persistence, notifications, email, and deployment
config. Forms currently simulate submission with mock local state.
