#!/usr/bin/env python3
"""TNC blog monthly review — audits every post + the site against the framework.
Run from the repo root: `python3 audit.py`. Exit 0 = clean, 1 = issues found.

Deterministic checks (the judgment layer — copy quality, number realism — is added by
the scheduled NoteClaw routine that runs this and reads the report). Covers:
 structure (validator), voice (em-dashes/banned words), SEO/schema, hero category pill,
 internal links, deal-breakdown disclaimers, sitemap freshness, GA, and the pop-up + ebook.
"""
import os, re, glob, subprocess, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'index.html','blog.html','post-template.html','post-template-lean.html','cookie-policy.html',
        'privacy-policy.html','terms-and-conditions.html','buybox.html','unsubscribed.html'}
BANNED = ['crucial','robust','leverage','delve','nuanced','multifaceted']
GA_ID = 'G-GQ77SEVNY7'
EBOOK = "The Note Investor's Playbook"     # canonical ebook name — must be consistent
CATS = {"cat-note","cat-strategy","cat-retire","cat-re","cat-deal","cat-edu","cat-other"}
ALL = set(glob.glob("*.html"))
posts = sorted(f for f in ALL if f not in SKIP)
issues = []
def flag(f, msg): issues.append((f, msg))

for f in posts:
    h = open(f, encoding="utf-8").read()
    low = h.lower()
    # structure
    if subprocess.run(["bash","validate-blog.sh",f],capture_output=True).returncode != 0:
        flag(f, "validator FAIL (run ./validate-blog.sh)")
    # voice
    if "—" in h or "&mdash;" in h: flag(f, f"em-dashes present ({h.count(chr(8212))})")
    for b in BANNED:
        if re.search(r'\b'+b+r'\b', low): flag(f, f"banned word: {b}")
    # SEO / schema
    if 'rel="canonical"' not in h: flag(f, "missing canonical")
    if 'property="og:title"' not in h: flag(f, "missing Open Graph")
    if 'application/ld+json' not in h: flag(f, "missing JSON-LD schema")
    # hero category pill must use inline style (class-only renders no pill)
    m = re.search(r'<span class="post-cat-tag([^"]*)"([^>]*)>', h)
    if m and 'style=' not in m.group(2):
        flag(f, "hero category pill has no inline style (renders as plain text)")
    # internal links resolve
    for tgt in set(re.findall(r'href="([a-z0-9-]+\.html)"', h)):
        if tgt not in ALL: flag(f, f"broken internal link -> {tgt}")
    # pop-up form + ebook
    if 'exitPopup' not in h or 'playbook-banner' not in h: flag(f, "missing pop-up / playbook banner")
    if EBOOK not in h: flag(f, f'ebook name mismatch (expected "{EBOOK}")')
    # deal-breakdown compliance
    if f.startswith("deal-breakdown"):
        if 'not investment, tax, or legal advice' not in h:
            flag(f, "DEAL BREAKDOWN missing compliance disclaimer")

# site-level
sm = open("sitemap.xml", encoding="utf-8").read() if os.path.exists("sitemap.xml") else ""
locs = sm.count("<loc>")
if locs != len(posts) + 2:
    flag("sitemap.xml", f"loc count {locs} != posts+2 ({len(posts)+2})")
bj = open("blog.js", encoding="utf-8").read() if os.path.exists("blog.js") else ""
if GA_ID not in bj: flag("blog.js", f"GA id {GA_ID} not found (tracking may be broken)")

print("═══════════════════════════════════════")
print(f"  TNC BLOG MONTHLY REVIEW — {len(posts)} posts")
print("═══════════════════════════════════════")
if not issues:
    print("  ✅ ALL CLEAN — no issues found.")
else:
    from collections import defaultdict
    byf = defaultdict(list)
    for f, m in issues: byf[f].append(m)
    for f in sorted(byf):
        print(f"\n  ⚠ {f}")
        for m in byf[f]: print(f"      - {m}")
    print(f"\n  {len(issues)} issue(s) across {len(byf)} file(s).")
print("═══════════════════════════════════════")
sys.exit(1 if issues else 0)
