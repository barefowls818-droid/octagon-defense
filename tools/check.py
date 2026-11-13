"""Sanity checks on public/: titles, descriptions, one h1, heading order, links, images, JSON-LD."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PUB = Path(__file__).resolve().parent.parent / "public"
problems = []
# Pages linked from the nav that are planned but not built yet. Remove each as it ships.
PENDING = {"/protection/", "/careers/", "/about/", "/contact/"}
pending_hits = set()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h, self.links, self.imgs, self.ld, self._ld = [], [], [], [], None
        self.title = self.desc = None
        self._t = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if re.fullmatch(r"h[1-6]", tag):
            self.h.append(int(tag[1]))
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
        if tag == "title":
            self._t = True
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag == "script" and self._ld is not None:
            self.ld.append(self._ld)
            self._ld = None

    def handle_data(self, data):
        if self._t:
            self.title = (self.title or "") + data
        if self._ld is not None:
            self._ld += data


titles, descs = {}, {}
for f in sorted(PUB.rglob("*.html")):
    rel = "/" + f.relative_to(PUB).as_posix()
    p = Page()
    p.feed(f.read_text())
    if p.h.count(1) != 1:
        problems.append(f"{rel}: {p.h.count(1)} h1")
    for a, b in zip(p.h, p.h[1:]):
        if b > a + 1:
            problems.append(f"{rel}: heading jump h{a}->h{b}")
    t = (p.title or "").replace("&amp;", "&")
    if not 30 <= len(t) <= 70 and "404" not in rel:
        problems.append(f"{rel}: title length {len(t)}: {t}")
    if not 110 <= len(p.desc or "") <= 165 and "404" not in rel:
        problems.append(f"{rel}: description length {len(p.desc or '')}")
    titles.setdefault(t, []).append(rel)
    descs.setdefault(p.desc, []).append(rel)
    for href in p.links:
        if href.startswith("/"):
            path = href.split("#")[0].split("?")[0]
            target = PUB / path.lstrip("/")
            if path in PENDING:
                pending_hits.add(path)
            elif not (target.is_file() or (target / "index.html").is_file()):
                problems.append(f"{rel}: broken link {href}")
    for img in p.imgs:
        src = img.get("src", "").split("?")[0]
        if src.startswith("/") and not (PUB / src.lstrip("/")).is_file():
            problems.append(f"{rel}: missing image {src}")
        if "alt" not in img:
            problems.append(f"{rel}: img without alt {src}")
        if not img.get("width") or not img.get("height"):
            problems.append(f"{rel}: img without dimensions {src}")
        for part in img.get("srcset", "").split(","):
            u = part.strip().split(" ")[0].split("?")[0]
            if u.startswith("/") and not (PUB / u.lstrip("/")).is_file():
                problems.append(f"{rel}: missing srcset image {u}")
    for block in p.ld:
        try:
            json.loads(block)
        except ValueError as e:
            problems.append(f"{rel}: bad JSON-LD {e}")

for k, v in list(titles.items()) + list(descs.items()):
    if len(v) > 1:
        problems.append(f"duplicate title/description on {v}")

if pending_hits:
    print("links to planned pages (not built yet): " + ", ".join(sorted(pending_hits)))
print("\n".join(problems) or "all checks passed")
sys.exit(1 if problems else 0)
