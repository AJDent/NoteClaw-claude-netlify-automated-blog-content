#!/usr/bin/env python3
"""TNC blog Friday cadence — publish the next pre-approved queued post.

Run from the repo root (the Friday GitHub Action does this). Reads queue/manifest.json,
takes the head entry, moves its HTML into place, stamps today's date, inserts the index
card + sitemap URL at the CADENCE markers, pops the entry, and validates the result.

SAFETY: only publishes what is already in queue/ — posts you built, validated, and approved.
The queue is the approval gate; this script is purely mechanical. Manifest fields are still
validated and HTML-escaped defensively (slug/file allowlisted, card text escaped, no raw
values written to GITHUB_OUTPUT) so a malformed entry can't traverse paths or inject markup.
"""
import json, os, re, sys, shutil, subprocess, datetime, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MANIFEST = "queue/manifest.json"

SLUG_RE = re.compile(r'[a-z0-9][a-z0-9-]{1,80}\Z')      # url-safe, no dots/slashes
FILE_RE = re.compile(r'[A-Za-z0-9._-]+\Z')             # plain basename only
CATS = {"cat-note", "cat-strategy", "cat-retire", "cat-re", "cat-deal", "cat-edu", "cat-other"}

def die(msg):
    print(f"::error::{msg}"); sys.exit(1)

data = json.load(open(MANIFEST, encoding="utf-8"))
queue = data.get("queue", [])
if not queue:
    print("::notice::Queue empty — nothing to publish today.")
    sys.exit(0)

e = queue[0]
for k in ("slug", "title", "category", "cat_class", "blurb", "read_time"):
    if not isinstance(e.get(k), str) or not e.get(k).strip():
        die(f"Manifest entry missing/invalid '{k}': {e!r}")

# --- validate identifiers before they touch the filesystem or markup ---
slug = e["slug"]
if not SLUG_RE.match(slug):
    die(f"Invalid slug (allowed: a-z 0-9 '-'): {slug!r}")
fname = e.get("file", slug + ".html")
if not FILE_RE.match(fname) or os.path.basename(fname) != fname:
    die(f"Invalid file name (plain basename only): {fname!r}")
if e["cat_class"] not in CATS:
    die(f"Invalid cat_class {e['cat_class']!r}; must be one of {sorted(CATS)}")

src = os.path.join("queue", fname)
dst = slug + ".html"
# defense in depth: both paths must resolve inside the repo root
for p in (src, dst):
    if os.path.commonpath([os.path.realpath(p), ROOT]) != ROOT:
        die(f"Refusing path outside repo: {p}")
if not os.path.exists(src): die(f"Queued file not found: {src}")
if os.path.exists(dst):     die(f"'{dst}' already exists in repo root — already published?")

# publish date in Eastern Time
try:
    from zoneinfo import ZoneInfo
    now = datetime.datetime.now(ZoneInfo("America/New_York"))
except Exception:
    now = datetime.datetime.utcnow()
human = now.strftime("%B %-d, %Y")     # e.g. August 28, 2026
iso = now.strftime("%Y-%m-%d")

# 1) move the post into place + stamp the visible date
shutil.move(src, dst)
page = open(dst, encoding="utf-8").read()
page, nsub = re.subn(r'(<span class="meta-date">)(.*?)(</span>)',
                     lambda m: m.group(1) + human + m.group(3), page, count=1)
if nsub == 0: die(f'No <span class="meta-date"> found in {dst}')
open(dst, "w", encoding="utf-8").write(page)

# 2) index card at the CADENCE:CARDS marker (newest first) — text HTML-escaped
cat_class = e["cat_class"]                                  # allowlisted above
cat_bg = "cat-bg-" + cat_class.split("cat-", 1)[1]          # cat-bg-retire
esc = lambda s: html.escape(s, quote=False)                # neutralize tags, keep quotes readable
blog = open("blog.html", encoding="utf-8").read()
if "<!-- CADENCE:CARDS -->" not in blog: die("blog.html missing <!-- CADENCE:CARDS --> marker")
nums = [int(x) for x in re.findall(r'<!-- Post (\d+) -->', blog)]
n = (max(nums) + 1) if nums else 1
card = (
    f'\n    <!-- Post {n} -->\n'
    f'    <a href="{dst}" style="text-decoration:none;color:inherit;">\n'
    f'    <article class="preview-card">\n'
    f'      <div class="preview-card-img {cat_bg}"></div>\n'
    f'      <div class="preview-card-body">\n'
    f'        <span class="preview-cat-tag {cat_class}">{esc(e["category"])}</span>\n'
    f'        <h3>{esc(e["title"])}</h3>\n'
    f'        <p>{esc(e["blurb"])}</p>\n'
    f'        <div class="preview-read">{esc(e["read_time"])}</div>\n'
    f'      </div>\n'
    f'    </article>\n'
    f'    </a>\n'
)
blog = blog.replace("<!-- CADENCE:CARDS -->", "<!-- CADENCE:CARDS -->" + card, 1)
open("blog.html", "w", encoding="utf-8").write(blog)

# 3) sitemap URL at the CADENCE:URLS marker (slug is allowlisted)
sm = open("sitemap.xml", encoding="utf-8").read()
if "<!-- CADENCE:URLS -->" not in sm: die("sitemap.xml missing <!-- CADENCE:URLS --> marker")
url_block = (
    f'\n  <url>\n'
    f'    <loc>https://takenotescapital.com/{dst}</loc>\n'
    f'    <lastmod>{iso}</lastmod>\n'
    f'    <changefreq>monthly</changefreq>\n'
    f'    <priority>0.8</priority>\n'
    f'  </url>'
)
sm = sm.replace("<!-- CADENCE:URLS -->", "<!-- CADENCE:URLS -->" + url_block, 1)
open("sitemap.xml", "w", encoding="utf-8").write(sm)

# 4) pop the entry
data["queue"] = queue[1:]
json.dump(data, open(MANIFEST, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# 5) validate the published post — fail loudly so the Action does NOT push a broken post
res = subprocess.run(["bash", "validate-blog.sh", dst], capture_output=True, text=True)
print(res.stdout[-600:])
if res.returncode != 0: die(f"Validator failed on {dst} — aborting before push")

print(f"::notice::Published {dst} as Post {n} ({human}). {len(data['queue'])} post(s) left in queue.")
# only emit sanitized, structural values (slug is allowlisted; remaining is an int)
out = os.environ.get("GITHUB_OUTPUT")
if out:
    with open(out, "a") as f:
        f.write(f"published={dst}\n")
        f.write(f"remaining={len(data['queue'])}\n")
