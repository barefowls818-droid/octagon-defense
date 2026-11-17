#!/usr/bin/env python3
"""Render src/ into public/ (standard library only).

    python3 build.py                                          # preview build: every page noindex
    SITE_URL=https://example.com INDEXABLE=1 python3 build.py # launch build

Pages live in src/pages/*.html. Each starts with a front-matter block:

    ---
    title: Page title for <title>
    description: Meta description
    crumb: Short breadcrumb name (omit on the home page)
    schema: home | faq | person | contact      (comma-separate to combine, e.g. home,faq)
    ---

Inside a page, {{tokens}} are replaced; see TOKENS below.
"""
import hashlib
import html
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

# ---- CONFIG: change these when the custom domain is live ------------------
SITE_URL = os.environ.get("SITE_URL", "https://octagon-defense.workers.dev").rstrip("/")
INDEXABLE = os.environ.get("INDEXABLE", "0") == "1"
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "public"
SITE = json.loads((SRC / "data" / "site.json").read_text())
ORG_ID = f"{SITE_URL}/#business"
OWNER_ID = f"{SITE_URL}/about/#brennan"
TODAY = date.today().isoformat()

NAV = [
    ("Need protection?", "/hire-bouncers-lubbock/"),
    ("Careers", "/careers/"),
    ("About", "/about/"),
    ("Contact", "/contact/"),
]

esc = html.escape

# The brand mark: a solid red octagon (flat top). Decorative wherever the name sits beside it.
MARK = ('<svg class="mark" viewBox="0 0 200 200" aria-hidden="true" focusable="false">'
        '<polygon points="58.58,0 141.42,0 200,58.58 200,141.42 141.42,200 58.58,200 0,141.42 0,58.58"/></svg>')


def asset_hash(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()[:10]


# ---- partials --------------------------------------------------------------

def tel_link(label=None, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="tel:{SITE["phoneE164"]}">{esc(label or SITE["phone"])}</a>'


def mail_link(label=None, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="mailto:{SITE["email"]}">{esc(label or SITE["email"])}</a>'


def areas_inline():
    return " · ".join(a.get("short", a["name"]) for a in SITE["areas"])


EVENT_TYPES = ["Bar or nightclub", "Event venue", "House or private party", "Student or Greek event",
               "Birthday or celebration", "Other"]
CITIES = ["Lubbock", "Houston", "Dallas–Fort Worth", "Somewhere else in Texas"]


def _opts(xs):
    return "".join(f'<option>{esc(x)}</option>' for x in xs)


def form_shell(form_id, subject, mail_subject, ok_msg, inner, submit_label):
    """Every site form. Posts to SITE["formEndpoint"] (Formspree) when set; until then site.js opens
    a pre-filled email to Brennan instead, so a form is never a dead end."""
    endpoint = SITE.get("formEndpoint", "")
    p = form_id.split("-")[0]
    return f"""<form class="rq" id="{form_id}" method="post" action="{esc(endpoint) or 'mailto:' + SITE['email']}" data-endpoint="{esc(endpoint)}" data-email="{SITE['email']}" data-mail-subject="{esc(mail_subject)}" data-ok="{esc(ok_msg)}" novalidate>
  <input type="hidden" name="_subject" value="{esc(subject)}">
  <p class="rq__hp" aria-hidden="true"><label for="{p}-company">Leave this empty</label><input id="{p}-company" name="_gotcha" tabindex="-1" autocomplete="off"></p>
  {inner}
  <div class="rq__foot">
    <button class="btn" type="submit">{esc(submit_label)}</button>
    <p class="rq__alt">Rather talk? Call <a href="tel:{SITE['phoneE164']}">{SITE['phone']}</a>.</p>
  </div>
  <p class="rq__status" role="status" aria-live="polite"></p>
</form>"""


def you_fields(p, email_required=False):
    req = " required" if email_required else ""
    opt = "" if email_required else ' <span class="opt">(optional)</span>'
    return f"""<div class="rq__row">
      <p class="field"><label for="{p}-name">Your name</label><input id="{p}-name" name="name" autocomplete="name" required></p>
      <p class="field"><label for="{p}-phone">Phone</label><input id="{p}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></p>
    </div>
    <p class="field"><label for="{p}-email">Email{opt}</label><input id="{p}-email" name="email" type="email" autocomplete="email"{req}></p>"""


def request_form():
    inner = f"""<fieldset>
    <legend>About you</legend>
    {you_fields("rq")}
  </fieldset>
  <fieldset>
    <legend>About the event</legend>
    <div class="rq__row">
      <p class="field"><label for="rq-type">Type of event</label><select id="rq-type" name="event_type" required><option value="">Choose one</option>{_opts(EVENT_TYPES)}</select></p>
      <p class="field"><label for="rq-city">City</label><select id="rq-city" name="city" required>{_opts(CITIES)}</select></p>
    </div>
    <div class="rq__row">
      <p class="field"><label for="rq-date">Date</label><input id="rq-date" name="date" type="date" required></p>
      <p class="field"><label for="rq-hours">Start and end time</label><input id="rq-hours" name="hours" placeholder="e.g. 9 pm to 2 am"></p>
    </div>
    <div class="rq__row">
      <p class="field"><label for="rq-guests">Expected guests</label><input id="rq-guests" name="guests" inputmode="numeric" placeholder="e.g. 150"></p>
      <p class="field"><label for="rq-alcohol">Alcohol served?</label><select id="rq-alcohol" name="alcohol"><option>Yes</option><option>No</option><option>Not sure yet</option></select></p>
    </div>
    <p class="field"><label for="rq-venue">Venue or address</label><input id="rq-venue" name="venue" autocomplete="street-address"></p>
    <p class="field"><label for="rq-notes">Anything else we should know? <span class="opt">(optional)</span></label><textarea id="rq-notes" name="notes" rows="4" placeholder="Recurring nights, problems you've had before, where you want people posted"></textarea></p>
  </fieldset>"""
    return form_shell("request-form", "Protection request from the website", "Protection request",
                      "Request sent. Brennan will get back to you soon.", inner, "Send request")


def apply_form():
    inner = f"""<fieldset>
    <legend>About you</legend>
    {you_fields("ap")}
  </fieldset>
  <fieldset>
    <legend>Your experience</legend>
    <p class="field"><label for="ap-exp">Door, event or protection experience</label><select id="ap-exp" name="experience" required><option value="">Choose one</option><option>None yet</option><option>Less than a year</option><option>One to three years</option><option>More than three years</option></select></p>
    <p class="field"><label for="ap-background">Combat sports, wrestling or martial arts background <span class="opt">(optional)</span></label><input id="ap-background" name="background" placeholder="e.g. 4 years high school wrestling, amateur MMA"></p>
    <div class="field"><p class="field__label" id="ap-avail-l">When can you work?</p>
      <div class="checks" role="group" aria-labelledby="ap-avail-l">
        <label><input type="checkbox" name="availability" value="Weeknights"> Weeknights</label>
        <label><input type="checkbox" name="availability" value="Friday and Saturday nights"> Friday and Saturday nights</label>
        <label><input type="checkbox" name="availability" value="Daytime weekends"> Daytime weekends</label>
      </div>
    </div>
    <p class="field"><label for="ap-about">Tell us about yourself <span class="opt">(optional)</span></label><textarea id="ap-about" name="about" rows="4" placeholder="Jobs you've worked, why you want this one, anything we should know"></textarea></p>
  </fieldset>"""
    return form_shell("apply-form", "Job application from the website", "Job application",
                      "Application sent. Brennan will reach out if it's a fit.", inner, "Send application")


def contact_form():
    inner = f"""<fieldset>
    <legend>Send a message</legend>
    {you_fields("ct")}
    <p class="field"><label for="ct-topic">What's this about?</label><select id="ct-topic" name="topic" required><option value="">Choose one</option><option>Hiring bouncers or protection</option><option>Applying for a job</option><option>Something else</option></select></p>
    <p class="field"><label for="ct-msg">Message</label><textarea id="ct-msg" name="message" rows="5" required></textarea></p>
  </fieldset>"""
    return form_shell("contact-form", "Message from the website", "Website message",
                      "Message sent. Brennan will get back to you soon.", inner, "Send message")


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


TOKENS = {
    "phone": lambda: SITE["phone"],
    "tel": lambda: f'tel:{SITE["phoneE164"]}',
    "email": lambda: SITE["email"],
    "mailto": lambda: f'mailto:{SITE["email"]}',
    "owner": lambda: SITE["owner"],
    "pay": lambda: SITE["hiring"]["pay"],
    "mark": lambda: MARK,
    "areas": areas_inline,
    "request-form": request_form,
    "apply-form": apply_form,
    "contact-form": contact_form,
    "posted": lambda: fmt_date(SITE["hiring"]["posted"]),
    "posted-iso": lambda: SITE["hiring"]["posted"],
}


def render_tokens(body):
    return re.sub(r"\{\{([a-z\-]+)\}\}", lambda m: TOKENS[m.group(1)](), body)


# ---- schema ----------------------------------------------------------------

def business_node(description):
    return {
        "@type": "ProfessionalService",
        "@id": ORG_ID,
        "name": SITE["name"],
        "slogan": SITE["descriptor"],
        "description": description,
        "url": f"{SITE_URL}/",
        "logo": f"{SITE_URL}/img/octagon-defense-logo.png",
        "image": f"{SITE_URL}/img/og-octagon-defense.jpg",
        "telephone": SITE["phoneE164"],
        "email": SITE["email"],
        "areaServed": [{"@type": "Place", "name": a["schema"]} for a in SITE["areas"]],
        "founder": {"@id": OWNER_ID},
        "contactPoint": {"@type": "ContactPoint", "telephone": SITE["phoneE164"], "email": SITE["email"],
                         "contactType": "customer service", "areaServed": "US-TX", "availableLanguage": "English"},
    }


def person_node():
    return {
        "@type": "Person",
        "@id": OWNER_ID,
        "name": SITE["owner"],
        "jobTitle": SITE["ownerTitle"],
        "worksFor": {"@id": ORG_ID},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": SITE["ownerSchool"]},
        "url": f"{SITE_URL}/about/",
    }


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def faq_node(body, url):
    qa = re.findall(r'<details class="faq"[^>]*>\s*<summary><h3>(.*?)</h3></summary>(.*?)</details>', body, re.S)
    return {
        "@type": "FAQPage",
        "@id": f"{url}#faq",
        "mainEntity": [
            {"@type": "Question", "name": strip_tags(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in qa
        ],
    }


def service_node(meta, url):
    """Service page: name/type/area come from front matter (service_name, service_type, service_area)."""
    areas = [a.strip() for a in meta.get("service_area", "").split("|") if a.strip()]
    return {
        "@type": "Service",
        "@id": f"{url}#service",
        "name": meta["service_name"],
        "serviceType": meta["service_type"],
        "description": meta["description"],
        "provider": {"@id": ORG_ID},
        "areaServed": [{"@type": "City", "name": a} for a in areas],
        "url": url,
        "potentialAction": {"@type": "CommunicateAction", "name": "Request protection", "target": f"{url}#request"},
    }


def job_node(body, url):
    """JobPosting for Google's job listings. The description is the visible job section, marked
    in the page with <!--job--> ... <!--/job-->. Only emitted while site.json hiring.open is true."""
    h = SITE["hiring"]
    m = re.search(r"<!--job-->(.*?)<!--/job-->", body, re.S)
    desc = re.sub(r'\s(?:class|id|aria-[\w-]+|data-[\w-]+)="[^"]*"', "", m.group(1))
    desc = re.sub(r"</?(?:div|section|article|span)[^>]*>", "", desc)
    desc = re.sub(r"\s+", " ", desc).strip()
    return {
        "@type": "JobPosting",
        "@id": f"{url}#job",
        "title": h["title"],
        "description": desc,
        "datePosted": h["posted"],
        "employmentType": "PART_TIME",
        "hiringOrganization": {"@type": "Organization", "@id": ORG_ID, "name": SITE["name"],
                               "sameAs": f"{SITE_URL}/", "logo": f"{SITE_URL}/img/octagon-defense-logo.png"},
        "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "addressLocality": "Lubbock",
                                                      "addressRegion": "TX", "addressCountry": "US"}},
        "baseSalary": {"@type": "MonetaryAmount", "currency": "USD",
                       "value": {"@type": "QuantitativeValue", "minValue": h["payMin"], "maxValue": h["payMax"],
                                 "unitText": "HOUR"}},
        "url": url,
    }


def breadcrumb_node(crumbs):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, **({"item": SITE_URL + href} if href else {})}
            for i, (name, href) in enumerate(crumbs)
        ],
    }


# ---- page assembly ---------------------------------------------------------

def parse(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def url_for(rel):
    rel = rel.with_suffix("")
    if rel.name == "index":
        rel = rel.parent
    return "/" if str(rel) == "." else f"/{rel.as_posix()}/"


def header(current):
    here = ' aria-current="page"'
    links = "".join(
        f'<li><a href="{href}"{here if current.startswith(href) else ""}>{esc(label)}</a></li>'
        for label, href in NAV
    )
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="masthead__inner">
    <a class="brand" href="/"{here if current == "/" else ""}>{MARK}<span class="brand__name">Octagon Defense</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="nav" id="site-nav" aria-label="Main"><ul>{links}</ul></nav>
    {tel_link(f"Call {SITE['phone']}", "btn btn--sm masthead__call")}
  </div>
</header>"""


def footer():
    year = date.today().year
    pages = "".join(f'<li><a href="{h}">{esc(l)}</a></li>' for l, h in NAV)
    areas = "".join(f'<li>{esc(a["name"])}, TX</li>' for a in SITE["areas"])
    return f"""<footer class="footer t-ink">
  <div class="wrap footer__inner">
    <div class="footer__brand">
      <a class="brand" href="/">{MARK}<span class="brand__name">Octagon Defense</span></a>
      <p class="footer__tag">{esc(SITE["descriptor"])}. De-escalation first.</p>
    </div>
    <div>
      <h2 class="footer__h">Contact</h2>
      <ul class="footer__list">
        <li>{esc(SITE["owner"])}, {esc(SITE["ownerTitle"].lower())}</li>
        <li>{tel_link()}</li>
        <li>{mail_link()}</li>
      </ul>
    </div>
    <div>
      <h2 class="footer__h">Where we work</h2>
      <ul class="footer__list">{areas}</ul>
    </div>
    <div>
      <h2 class="footer__h">Pages</h2>
      <ul class="footer__list">{pages}</ul>
    </div>
  </div>
  <div class="wrap"><p class="footer__legal">© {year} Octagon Defense · Lubbock, Texas</p></div>
</footer>
<div class="callbar">{tel_link("Call", "btn btn--ghost")}<a class="btn" href="/hire-bouncers-lubbock/#request">Request protection</a></div>"""


def breadcrumbs_html(crumbs):
    items = []
    for name, href in crumbs:
        items.append(f'<li><a href="{href}">{esc(name)}</a></li>' if href else f'<li aria-current="page">{esc(name)}</li>')
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def page(meta, body, url, css, js, is_404=False):
    canonical = SITE_URL + url
    crumbs = []
    if meta.get("crumb"):
        crumbs = [("Home", "/"), (meta["crumb"], None)]
        if "{{crumbs}}" in body:  # a page can place its breadcrumb inside its hero
            body = body.replace("{{crumbs}}", breadcrumbs_html(crumbs).replace('class="crumbs wrap"', 'class="crumbs"'))
        else:
            body = breadcrumbs_html(crumbs) + body
    body = render_tokens(body)

    schema = [s.strip() for s in meta.get("schema", "").split(",") if s.strip()]
    graph = [business_node(meta["description"] if "home" in schema else SITE["descriptor"])]
    if "home" in schema:
        graph += [person_node(),
                  {"@type": "WebSite", "@id": f"{SITE_URL}/#website", "url": f"{SITE_URL}/",
                   "name": SITE["name"], "publisher": {"@id": ORG_ID}}]
    if "person" in schema and "home" not in schema:
        graph.append(person_node())
    if "service" in schema:
        graph.append(service_node(meta, canonical))
    if "job" in schema and SITE["hiring"].get("open"):
        graph.append(job_node(body, canonical))
    if "about" in schema:
        graph += [person_node(), {"@type": "AboutPage", "@id": f"{canonical}#page", "url": canonical,
                                  "name": meta["title"], "about": {"@id": ORG_ID}, "mainEntity": {"@id": OWNER_ID}}]
    if "contact" in schema:
        graph.append({"@type": "ContactPage", "@id": f"{canonical}#page", "url": canonical,
                      "name": meta["title"], "about": {"@id": ORG_ID}})
    if "faq" in schema:
        graph.append(faq_node(body, canonical))
    if crumbs:
        graph.append(breadcrumb_node([(n, h or url) for n, h in crumbs]))
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))

    robots = "index, follow" if INDEXABLE and not is_404 else "noindex, follow"
    og_image = f"{SITE_URL}/img/og-octagon-defense.jpg"
    title, desc = esc(meta["title"]), esc(meta["description"])
    canon = "" if is_404 else f'<link rel="canonical" href="{canonical}">\n'
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add("js")</script>
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
{canon}<meta name="theme-color" content="#0B0B0C">
<link rel="preload" href="/fonts/anton-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/barlow-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css?v={css}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Octagon Defense">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Octagon Defense: a red octagon beside the words Trained to fight. Paid not to.">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
<script src="/js/site.js?v={js}" defer></script>
</head>
<body class="{meta.get("bodyclass", "")}">
{header(url)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""


def version_assets(doc):
    """Add ?v=<content hash> to local image URLs so browsers refetch an image when it changes."""
    hashes = {}

    def sub(m):
        path = m.group(2)
        if path not in hashes:
            f = OUT / path.lstrip("/")
            hashes[path] = asset_hash(f) if f.is_file() else None
        return m.group(0) if hashes[path] is None else f"{m.group(0)}?v={hashes[path]}"

    return re.sub(r"(https?://[^\s\"'/]+)?(/img/[\w\-/]+\.(?:webp|png|jpg|svg))(?![?\w])", sub, doc)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "static", OUT)
    css = asset_hash(OUT / "css" / "site.css")
    js = asset_hash(OUT / "js" / "site.js")

    urls = []
    for path in sorted((SRC / "pages").rglob("*.html")):
        rel = path.relative_to(SRC / "pages")
        meta, body = parse(path)
        if rel.name == "404.html":
            (OUT / "404.html").write_text(version_assets(page(meta, body, "/404", css, js, is_404=True)))
            continue
        url = url_for(rel)
        dest = OUT / url.strip("/") / "index.html" if url != "/" else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(version_assets(page(meta, body, url, css, js)))
        urls.append(url)

    sitemap = "".join(f"<url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n'
    )
    robots = "User-agent: *\nAllow: /\n"
    if INDEXABLE:
        robots += f"\nSitemap: {SITE_URL}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots)

    headers = (OUT / "_headers").read_text()
    if not INDEXABLE:
        headers = headers.replace("/*\n", "/*\n  X-Robots-Tag: noindex\n", 1)
    (OUT / "_headers").write_text(headers)
    print(f"built {len(urls)} pages -> {OUT.relative_to(ROOT)}  (SITE_URL={SITE_URL}, indexable={INDEXABLE})")


if __name__ == "__main__":
    build()
