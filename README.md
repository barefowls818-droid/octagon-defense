# Octagon Defense website

Static site for Octagon Defense (contract protection, Lubbock / Houston / DFW). Plain
HTML/CSS/JS rendered by a small Python script, served by a Cloudflare Worker (static assets).
Business facts and decisions live in `BRIEF.md`.

## Layout

| Path | What it is |
| --- | --- |
| `src/pages/` | One `.html` file per page with a front-matter block (title, description, crumb, schema) |
| `src/data/site.json` | Business facts: owner, phone, email, areas, hiring pay |
| `src/static/` | CSS, JS, fonts, images, favicons, `_headers` (copied as is) |
| `build.py` | Renders `src/` into `public/` (stdlib only) |
| `public/` | The built site. Committed, so Cloudflare needs no build step |
| `tools/check.py` | Checks titles, descriptions, headings, links, images, JSON-LD |
| `tools/make_images.js` | Renders the share card, schema logo and touch icon (Playwright) |
| `tools/make_favicon.py` | Builds `favicon.ico` (Pillow) |
| `branding/index.html` | The five brand directions (Corner Man was chosen) |

## Everyday edits

```sh
python3 build.py && python3 tools/check.py
```

`check.py` lists links to planned pages that aren't built yet. Remove a page from
`PENDING` in `tools/check.py` once it ships.

**Request form:** set `formEndpoint` in `src/data/site.json` to the Formspree URL
(e.g. `https://formspree.io/f/xxxxxxx`) and rebuild. Until then, submitting opens a pre-filled
email to Brennan. Send one real test after setting it; Formspree only starts delivering after
the first submission is confirmed.

Page tokens: `{{phone}}`, `{{tel}}`, `{{email}}`, `{{mailto}}`, `{{owner}}`, `{{pay}}`,
`{{areas}}`, `{{mark}}`. Change a fact in `site.json` and it updates everywhere.

## Status

| Page | URL | Status |
| --- | --- | --- |
| Home | `/` | Built |
| Need protection? | `/hire-bouncers-lubbock/` | Built |
| Careers | `/careers/` | Built (JobPosting schema) |
| About | `/about/` | Built |
| Contact | `/contact/` | Built |

All three forms (event request, job application, contact) share `formEndpoint`.

**The job posting:** `/careers/` carries JobPosting markup for Google's job listings, built
from `site.json` → `hiring`. When the role changes, update `pay`/`payMin`/`payMax` and set
`posted` to the new date. When Brennan stops hiring, set `hiring.open` to `false` (removes the
markup; also edit the page copy). Google penalises job markup for positions that are closed.

## Deploy and launch

Same as Vintage Lash Studio: `npx wrangler deploy` for a workers.dev preview (every page
`noindex`), then for launch:

```sh
SITE_URL=https://thedomain.com INDEXABLE=1 python3 build.py
```

Then verify the domain in Search Console and submit `/sitemap.xml`.
