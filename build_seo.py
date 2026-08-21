#!/usr/bin/env python3
"""Add missing SEO/social/schema tags to a TNC blog post, idempotently.
Adds only what's absent: canonical, Open Graph, Twitter card, JSON-LD BlogPosting,
and JSON-LD FAQPage (built from the post's quizData). Inserts before </head>.

Usage: build_seo.py <file.html>            # apply in place
       build_seo.py --dry <file.html>      # print what would be added, don't write
"""
import sys, os, re, json, datetime

DOMAIN = "https://takenotescapital.com"
IMG = f"{DOMAIN}/og-image.jpg"

def load(path): return open(path, encoding="utf-8").read()

def first(pat, s, default=""):
    m = re.search(pat, s, re.S)
    return m.group(1).strip() if m else default

def build_block(path, html):
    fname = os.path.basename(path)
    url = f"{DOMAIN}/{fname}"
    title = first(r'<title>(.*?)</title>', html)
    desc = first(r'<meta name="description" content="(.*?)">', html)
    cat = first(r'class="post-cat-tag[^"]*"[^>]*>(.*?)</span>', html) or "Note Investing"
    headline = re.sub(r'\s*\|\s*Take Notes Capital.*$', '', title).strip()
    # publish date -> ISO
    human = first(r'<span class="meta-date">(.*?)</span>', html)
    iso = ""
    try:
        iso = datetime.datetime.strptime(human, "%B %d, %Y").strftime("%Y-%m-%d")
    except Exception:
        iso = datetime.date.today().strftime("%Y-%m-%d")
    # FAQ from quizData
    qs = re.findall(r'question:\s*"((?:[^"\\]|\\.)*)"', html)
    ex = re.findall(r'explanation:\s*"((?:[^"\\]|\\.)*)"', html)
    faqs = list(zip(qs, ex))

    parts, added = [], []
    def esc(s): return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

    if 'rel="canonical"' not in html:
        parts.append(f'  <link rel="canonical" href="{url}">'); added.append("canonical")
    if 'property="og:title"' not in html:
        parts += [
            f'  <meta property="og:type" content="article">',
            f'  <meta property="og:site_name" content="Take Notes Capital">',
            f'  <meta property="og:title" content="{esc(title)}">',
            f'  <meta property="og:description" content="{esc(desc)}">',
            f'  <meta property="og:url" content="{url}">',
            f'  <meta property="og:image" content="{IMG}">',
        ]; added.append("open-graph")
    if 'name="twitter:card"' not in html:
        parts += [
            f'  <meta name="twitter:card" content="summary_large_image">',
            f'  <meta name="twitter:title" content="{esc(title)}">',
            f'  <meta name="twitter:description" content="{esc(desc)}">',
            f'  <meta name="twitter:image" content="{IMG}">',
        ]; added.append("twitter")
    if 'BlogPosting' not in html:
        blog_ld = {
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": headline, "description": desc, "image": IMG,
            "author": {"@type": "Person", "name": "AJ Dent", "url": DOMAIN},
            "publisher": {"@type": "Organization", "name": "Take Notes Capital",
                          "logo": {"@type": "ImageObject", "url": f"{DOMAIN}/logo.png"}},
            "datePublished": iso, "dateModified": iso,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "articleSection": cat,
        }
        parts.append('  <script type="application/ld+json">\n' +
                     json.dumps(blog_ld, indent=2, ensure_ascii=False) + '\n  </script>')
        added.append("schema:BlogPosting")
    if faqs and 'FAQPage' not in html:
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": q,
                                  "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
        parts.append('  <script type="application/ld+json">\n' +
                     json.dumps(faq_ld, indent=2, ensure_ascii=False) + '\n  </script>')
        added.append(f"schema:FAQPage({len(faqs)})")
    return ("\n".join(parts), added, {"title": title, "iso": iso, "cat": cat, "faqs": len(faqs)})

def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry"]
    path = args[0]
    html = load(path)
    block, added, meta = build_block(path, html)
    if not added:
        print(f"{os.path.basename(path)}: already complete — nothing to add"); return
    if "</head>" not in html:
        print(f"::error::{path}: no </head>"); sys.exit(1)
    new = html.replace("</head>", block + "\n</head>", 1)
    if dry:
        print(f"--- {os.path.basename(path)} would add: {', '.join(added)} ---")
        print(block)
    else:
        open(path, "w", encoding="utf-8").write(new)
        print(f"{os.path.basename(path)}: added {', '.join(added)}  (date={meta['iso']}, cat={meta['cat']}, faqs={meta['faqs']})")

if __name__ == "__main__":
    main()
