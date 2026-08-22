#!/usr/bin/env python3
"""Move an approved, unlisted-preview blog post into the Friday cadence queue.

Usage:  python3 queue/queue_approved.py <slug> [--dry-run]

Stage-2 of the weekly loop. After AJ reviews an unlisted preview (a <slug>.html sitting
at the repo root, live at its URL but NOT in blog.html or sitemap.xml) and says "publish",
this moves the file into queue/ and appends a queue/manifest.json entry stamped
"approved": true. The Friday cadence (publish_next.py) then takes the head of the queue
live on the next Friday.

The manifest card fields (title, category, cat_class, blurb, read_time) are extracted from
the post's OWN HTML, so the only input needed is the slug. That is what lets a one-word
"publish" reply drive the whole thing. Deterministic + guarded: slug is allowlisted, paths
must stay inside the repo, and nothing overwrites an existing queue entry. This script only
moves the file + edits the manifest; the caller does the git commit + push.
"""
import json, os, re, sys, subprocess, html, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MANIFEST = "queue/manifest.json"
SLUG_RE = re.compile(r'[a-z0-9][a-z0-9-]{1,80}\Z')

# category display name -> the cat_class publish_next.py / the index card expect
CAT_CLASS = {
    "Note Investing":       "cat-note",
    "Note Strategies":      "cat-strategy",
    "Retirement Investing": "cat-retire",
    "Real Estate":          "cat-re",
    "Deal Breakdowns":      "cat-deal",
    "Deal Breakdown":       "cat-deal",
    "Education":            "cat-edu",
    "Other":                "cat-other",
}

def die(msg):
    print(f"ERROR: {msg}"); sys.exit(1)

args = [a for a in sys.argv[1:] if not a.startswith("-")]
dry = "--dry-run" in sys.argv
if len(args) != 1:
    die("usage: queue_approved.py <slug> [--dry-run]")

slug = args[0]
if slug.endswith(".html"):
    slug = slug[:-5]
if not SLUG_RE.match(slug):
    die(f"invalid slug (a-z 0-9 '-' only): {slug!r}")

src = slug + ".html"
if os.path.commonpath([os.path.realpath(src), ROOT]) != ROOT:
    die(f"refusing path outside repo: {src}")
if not os.path.exists(src):
    die(f"unlisted preview not found at repo root: {src} (nothing to queue)")
dst = os.path.join("queue", src)
if os.path.exists(dst):
    die(f"already in queue: {dst}")

page = open(src, encoding="utf-8").read()

def grab(pattern, what):
    m = re.search(pattern, page, re.S)
    if not m:
        die(f"could not extract {what} from {src}")
    return html.unescape(m.group(1)).strip()

title = grab(r'<title>(.*?)</title>', "title")
title = re.sub(r'\s*\|\s*Take Notes Capital.*$', '', title).strip()
category = grab(r'<span class="post-cat-tag"[^>]*>(.*?)</span>', "category")
category = re.sub(r'<[^>]+>', '', category).strip()
read_time = grab(r'<span class="meta-read">(.*?)</span>', "read time")
blurb = grab(r'<p class="post-excerpt">(.*?)</p>', "excerpt (post-excerpt)")
blurb = re.sub(r'<[^>]+>', '', blurb).strip()

cat_class = CAT_CLASS.get(category)
if not cat_class:
    die(f"unknown category {category!r}; add it to CAT_CLASS in queue_approved.py")

entry = {
    "approved":  True,
    "slug":      slug,
    "file":      src,
    "title":     title,
    "category":  category,
    "cat_class": cat_class,
    "blurb":     blurb,
    "read_time": read_time,
}

print("Manifest entry extracted from the post HTML:")
print(json.dumps(entry, indent=2, ensure_ascii=False))

if dry:
    print("\n[dry-run] nothing moved, manifest unchanged.")
    sys.exit(0)

# move the preview into queue/ (git mv keeps history; fall back to a plain move)
if subprocess.run(["git", "mv", src, dst], capture_output=True, text=True).returncode != 0:
    shutil.move(src, dst)

data = json.load(open(MANIFEST, encoding="utf-8")) if os.path.exists(MANIFEST) else {"queue": []}
data.setdefault("queue", []).append(entry)
json.dump(data, open(MANIFEST, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print(f"\nQueued {src} (position {len(data['queue'])} in the queue). "
      "Commit + push to arm it for the next Friday.")
