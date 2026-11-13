"""Single-file preview of a built page (CSS, JS and fonts inlined) for sharing as one HTML file.
    python3 tools/make_preview.py public/index.html OUT.html
"""
import base64, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
src, out = Path(sys.argv[1]), Path(sys.argv[2])
doc = src.read_text()
css = (PUB / "css" / "site.css").read_text()
css = re.sub(r'url\("/fonts/([\w\-]+\.woff2)"\)', lambda m: 'url("data:font/woff2;base64,' + base64.b64encode((PUB / "fonts" / m.group(1)).read_bytes()).decode() + '")', css)
js = (PUB / "js" / "site.js").read_text()
title = re.search(r"<title>(.*?)</title>", doc).group(1)
body = re.search(r"<body[^>]*>(.*)</body>", doc, re.S).group(1)
body = re.sub(r'href="/(?=[a-z])', 'href="#', body)  # internal pages don't exist in the preview
out.write_text(f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
               f'<script>document.documentElement.classList.add("js")</script>\n<style>{css}</style>\n'
               f'<div class="body-preview">{body}</div>\n<script>{js}</script>\n')
print(out, out.stat().st_size)
