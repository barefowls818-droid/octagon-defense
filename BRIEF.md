# Octagon Defense — build brief

Static HTML/CSS/JS site for Brennan Thomasson's contract protection business. Read
`ONPAGE-SEO.md` and `PREMIUM-POLISH.md` in the vintage-lash-studio repo (both lowest
priority; this brief and Noah's instructions win).

## Decisions (locked by Noah, 2026-11-12)

- **Brand direction:** "Corner Man" (direction 2 in `branding/index.html`), with one change:
  the mark is a **solid red octagon**, no "OD" letters and no mesh inside it.
- **Words:** the business doesn't call itself "security". Use "protection" in visible copy.
  "Security" is allowed sparingly for search: title tags, meta descriptions, and at most one
  natural FAQ question per page. Never in headings other than that FAQ question.
- **Licensing:** say nothing that implies a license, certification, insurance, armed status
  or "officers" until Brennan supplies his license details. Texas regulates guard and
  protection companies (DPS Private Security Bureau, Occupations Code ch. 1702); once he
  has a license number, it likely needs to appear on the site.
- **Pages:** Home, Need protection? (`/hire-bouncers-lubbock/`, targets "hire bouncers
  Lubbock", "bar/event bouncers Lubbock", "party security Lubbock"), Careers (`/careers/`), About
  (`/about/`), Contact (`/contact/`). That's the whole site.
- **Stack/hosting:** same as Vintage Lash Studio: stdlib `build.py`, `public/` committed,
  Cloudflare Worker static assets, `noindex` until the domain is live.

## Brand system

| Token | Hex | Use |
| --- | --- | --- |
| Canvas Black | `#0B0B0C` | Main ground |
| Fight Red | `#C8102E` | Mark, buttons (white on it 5.9:1) |
| Red text on black | `#F0484F` | Small red text on dark grounds |
| Mat White | `#F4F3EF` | Type on dark, light sections |
| Cage Grey | `#8A8A8A` | Mesh, captions |

Type: Anton (display, uppercase), Barlow (body), Barlow Condensed 600/700 (labels, buttons,
nav). Self-hosted latin woff2 in `src/static/fonts/`. Texture: diagonal cage mesh.
Red on black is for marks and large display only (3.3:1).

## Business facts (from the hiring flyer and business card, 2026-11-12)

- **Owner:** Brennan Thomasson, Owner and Operator. Texas Tech graduate; MMA and wrestling
  background (Noah).
- **Phone:** (936) 445-8822 · **Email:** brennanthomasson@gmail.com
- **Descriptors used so far:** "Contract Protection", "Protection Services".
- **Card text:** "Highly trained party facilitators specializing in de-escalation and venue
  safety/protection."
- **Areas:** Lubbock (most current work), Houston, Dallas–Fort Worth.
- **Hiring:** part-time, $15–20/hr based on experience.
- Source images: `assets/source/hiring-flyer.png`, `assets/source/business-card.png`.

## Copy Brennan should confirm

These are written from the facts above but put words in his mouth:
- The three "How we work" points (read the room early / talk first / hands-on last resort).
- "You deal directly with Brennan" and "your contact from the first call to the end of the event".
- Service examples: birthdays and private parties; door and floor coverage for venues;
  one-night or recurring contracts.
- Hero slogan "Trained to fight. Paid not to."
- `/hire-bouncers-lubbock/`: the bouncer duties list (incl. checking guest lists and IDs),
  the "who hires us" list (incl. student and Greek events, formals), the three booking steps
  (plan and quote; arriving before doors open and staying until the room is clear), and the
  staffing table (a common rule of thumb: 1 per 100 guests, 1 per 50 with alcohol).
- `/careers/`: "Who we're looking for", "Why work here" (incl. shifts around school or another
  job), the availability options on the application form, "Apply in two minutes".
- `/about/`: "Why the octagon" (eight sides + the MMA cage) is our reading of the name; the
  combat-sports paragraph and "Own the result" points.
- Photo of Brennan for `/about/` (the profile card uses a "BT" octagon until then).

## Open questions

- Formspree form for the three site forms (or another endpoint); goes in `site.json` → `formEndpoint`.
- Before launch: the bouncer page markets contract bouncers. Texas regulates contract guard
  services (Occupations Code ch. 1702), so the license question matters before this page
  is indexed.

- License number and status (see Licensing above).
- Domain name; Google Business Profile (service-area business, no public address).
- Photos of Brennan and the team (the site is typographic until then).
- Does he want texts at the cell number? Should the Gmail stay public, or move to a
  domain email once the domain exists?
- Social profiles to list in schema `sameAs`.
