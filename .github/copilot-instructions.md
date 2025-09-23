# Copilot Instructions for pigeon.pictures

## Project Overview

- **Framework:** [Astro](https://astro.build/) with React integration (`@astrojs/react`)
- **Purpose:** Fetches and displays random pigeon images from Pixabay, with a timer for periodic updates.
- **Key Features:**
  - Dynamic image fetching via API routes
  - Periodic refresh logic (every 60 minutes)
  - Progress bar UI for next refresh
  - Facebook Like integration and Google Analytics

## Key Files & Structure

- `src/pages/pigeons/pigeon-[id].jpg.ts`: API route for serving pigeon images (uses randomized IDs and fetches from Pixabay)
- `src/shared.ts`: Shared constants and logic (e.g., pigeon count, refresh period, ID generation)
- `src/pages/timing.js.ts`: API route exposing next refresh time and period as JS globals
- `src/components/ProgressBar.tsx`: React component showing time remaining until next refresh
- `src/layouts/Layout.astro`: Main layout, includes Facebook/Google Analytics scripts and loads `/timing.js`
- `astro.config.mjs`: Astro config, enables React integration

## Developer Workflows

- **Install:** `npm install`
- **Dev server:** `npm run dev` (localhost:4321)
- **Build:** `npm run build`
- **Preview:** `npm run preview`
- **Astro CLI:** `npm run astro -- <command>`

## Patterns & Conventions

- **API Routes:** Use `.ts` files in `src/pages/` (e.g., `[param].ts`) to define endpoints. Return `Response` objects.
- **Image Fetching:** Uses `astro:env/server` for secrets (e.g., `PIXABAY_API_KEY`).
- **Randomization:** Pigeon IDs and image pages are randomized per request.
- **Globals:** `/timing.js` sets `window.nextPigeons` and `window.pigeonPeriod` for client-side use.
- **React Components:** Place in `src/components/`, import in `.astro` files as needed.
- **Styling:** Inline styles in components; global styles can be added in layouts.

## External Integrations

- **Pixabay API:** Requires `PIXABAY_API_KEY` secret (set in environment)
- **Facebook SDK:** Loaded in layout for Like button
- **Google Analytics:** Included in layout

## Tips for AI Agents

- Reference `src/shared.ts` for shared logic/constants
- Use Astro's file-based routing for new pages or API endpoints
- When adding new integrations, update `astro.config.mjs` if needed
- For new React components, add to `src/components/` and import in `.astro` files
- Use environment secrets for API keys (see `astro:env/server`)

---

_If any conventions or workflows are unclear, please ask for clarification or examples from the maintainers._
