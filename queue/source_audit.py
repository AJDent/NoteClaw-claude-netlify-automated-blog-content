#!/usr/bin/env python3
"""TNC blog SOURCE AUDIT — read-only. Flags which live posts assert facts without backbone.

Implements the Backbone Rule (BLOG-FRAMEWORK.md, 2026-08-30) as a triage: for every live
post it scans the ARTICLE body (the .post-content div, so nav/footer boilerplate is ignored),
counts factual-claim candidates (percentages, dollar/large numbers, stat phrases, legal/tax
refs, named agencies), counts authoritative citations actually present (links to .gov / MBA /
ATTOM / Fed / etc. + a Sources block), and scores each post's sourcing risk.

Deal Breakdown posts: their anonymized $/return figures are EXEMPT (illustrative, per AJ
2026-08-30) — those are NOT counted as claims. But external facts inside them (legal timelines,
statutes, market stats, named agencies) ARE counted.

This NEVER edits anything. It writes a markdown report and prints a ranked summary.

  python3 queue/source_audit.py            # audit + write report + print summary
  python3 queue/source_audit.py --print    # also print the full report to stdout
"""
import os, re, sys, html, datetime, glob

REPO   = os.path.expanduser("~/tnc-blog")
REPORT = os.path.expanduser(
    "~/noteclaw-backup/business/blog-posts/blog-source-audit-{}.md".format(
        datetime.date.today().isoformat()))
os.chdir(REPO)

# pages that are not blog posts
NON_POST = {"index", "blog", "post-template", "post-template-lean", "cookie-policy",
            "privacy-policy", "terms-and-conditions", "terms", "buybox", "unsubscribed",
            "404", "thank-you", "thanks"}

# --- claim signals (a factual assertion that should have backbone) ---
PCT      = re.compile(r'\b\d+(?:\.\d+)?\s?%')
DOLLAR   = re.compile(r'\$\s?\d[\d,]*(?:\.\d+)?')
BIGNUM   = re.compile(r'\b\d{1,3}(?:,\d{3})+\b')
STAT_PHRASE = re.compile(r'\b(according to|studies show|study (found|shows)|research (shows|found)|'
                         r'survey|data (show|shows|from)|on average|the average|median|statistics?|'
                         r'reported|report(s)?|per the|rate of|as many as|roughly \d|nearly \d)\b', re.I)
LEGAL    = re.compile(r'\b(IRC|CFR|U\.?S\.?C|Notice \d|Section \d|Dodd[- ]?Frank|RESPA|TILA|FDCPA|'
                      r'Reg(ulation)? [A-Z]|§|SAFE Act|Garn[- ]?St)\b')
AGENCY   = re.compile(r'\b(IRS|MBA|ATTOM|Federal Reserve|the Fed|Freddie Mac|Fannie Mae|HUD|FHA|'
                      r'FHFA|CFPB|FDIC|Census|BLS|FRED)\b')

# --- authoritative citations actually present ---
AUTH_LINK = re.compile(r'href="https?://[^"]*?(irs\.gov|[a-z0-9.-]*\.gov|mba\.org|attom|'
                       r'federalreserve|freddiemac|fanniemae|hud\.gov|consumerfinance|fdic|'
                       r'census\.gov|bls\.gov|stlouisfed|fred\.)[^"]*"', re.I)
SOURCES_BLOCK = re.compile(r'(id=["\']sources["\']|>\s*sources\s*<|<h[23][^>]*>\s*sources)', re.I)

def article(page):
    """Return just the .post-content article HTML (fallback: whole page)."""
    m = re.search(r'<div class="post-content">(.*?)<div id="quizSection"', page, re.S)
    if not m:
        m = re.search(r'<div class="post-content">(.*?)</div>\s*<!--', page, re.S)
    return m.group(1) if m else page

def text_of(htmlfrag):
    t = re.sub(r'<style.*?</style>', '', htmlfrag, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return html.unescape(t)

def samples(rx, text, n=3):
    out, seen = [], set()
    for m in rx.finditer(text):
        s = m.group(0).strip()
        key = s.lower()
        if key in seen:
            continue
        seen.add(key); out.append(s)
        if len(out) >= n:
            break
    return out

def audit_post(slug, page):
    is_deal = slug.startswith("deal-breakdown")
    art = article(page)
    txt = text_of(art)

    # claim signals
    pct    = PCT.findall(txt)
    dollar = DOLLAR.findall(txt)
    bignum = BIGNUM.findall(txt)
    statp  = STAT_PHRASE.findall(txt)
    legal  = LEGAL.findall(txt)
    agency = AGENCY.findall(txt)

    # For deal breakdowns, the $/% and big numbers are exempt (anonymized illustrative math).
    if is_deal:
        numeric_claims = 0
        numeric_note = "(deal $/return figures exempt — anonymized illustrative)"
    else:
        numeric_claims = len(pct) + len(dollar) + len(bignum)
        numeric_note = ""

    # external_facts = the TRUE backbone gap: stats, statutes, named agencies. These are citable
    # in every post type. Illustrative numeric math is tracked but does NOT drive risk (a post
    # can be all hypothetical examples and need no external citation).
    external_facts = len(statp) + len(legal) + len(agency)
    claims = numeric_claims + external_facts

    # citations present
    auth_links = len(AUTH_LINK.findall(art))
    has_sources = bool(SOURCES_BLOCK.search(art))
    cited = auth_links + (2 if has_sources else 0)

    # risk is driven by uncited EXTERNAL FACTS, not by illustrative numbers
    ef = external_facts
    if ef == 0:
        risk = "NONE"
    elif cited >= max(1, ef // 3):
        risk = "LOW"
    elif ef >= 5:
        risk = "HIGH"
    elif ef >= 2:
        risk = "MED"
    else:
        risk = "LOW"

    return {
        "slug": slug, "is_deal": is_deal, "claims": claims,
        "numeric_claims": numeric_claims, "external_facts": external_facts,
        "auth_links": auth_links, "has_sources": has_sources, "cited": cited, "risk": risk,
        "ex_pct": samples(PCT, txt), "ex_dollar": ([] if is_deal else samples(DOLLAR, txt)),
        "ex_stat": samples(STAT_PHRASE, txt), "ex_legal": samples(LEGAL, txt),
        "ex_agency": samples(AGENCY, txt), "numeric_note": numeric_note,
    }

def main():
    show = "--print" in sys.argv
    posts = []
    for f in sorted(glob.glob("*.html")):
        slug = f[:-5]
        if slug in NON_POST:
            continue
        posts.append(audit_post(slug, open(f, encoding="utf-8").read()))

    order = {"HIGH": 0, "MED": 1, "LOW": 2, "NONE": 3}
    posts.sort(key=lambda p: (order[p["risk"]], -p["external_facts"], -p["claims"]))

    counts = {r: sum(1 for p in posts if p["risk"] == r) for r in ("HIGH", "MED", "LOW", "NONE")}

    lines = []
    lines.append(f"# TNC Blog Source Audit — {datetime.date.today().isoformat()}")
    lines.append("")
    lines.append("Read-only triage against the Backbone Rule (BLOG-FRAMEWORK.md). Flags posts that assert "
                 "facts/numbers/stats with no authoritative citation. Deal-breakdown $/return figures are "
                 "exempt (anonymized illustrative); external facts inside them are still counted.")
    lines.append("")
    lines.append(f"**{len(posts)} live posts** — HIGH: {counts['HIGH']} · MED: {counts['MED']} · "
                 f"LOW: {counts['LOW']} · NONE: {counts['NONE']}")
    lines.append("")
    lines.append("Ranked by **external-fact signals** (uncited stats / statutes / named agencies) — the real "
                 "backbone gap. `illus#` = illustrative numeric figures (exempt from external citation).")
    lines.append("")
    lines.append("| Risk | Post | Ext-facts | illus# | Cites | Sources block |")
    lines.append("|------|------|----------:|-------:|------:|:-------------:|")
    for p in posts:
        lines.append(f"| {p['risk']} | {p['slug']} | {p['external_facts']} | {p['numeric_claims']} | "
                     f"{p['auth_links']} | {'yes' if p['has_sources'] else 'no'} |")
    lines.append("")
    lines.append("## Per-post detail (HIGH + MED)")
    for p in posts:
        if p["risk"] in ("LOW", "NONE"):
            continue
        lines.append("")
        lines.append(f"### {p['slug']}  — **{p['risk']}**")
        lines.append(f"- claims: {p['claims']} (numeric {p['numeric_claims']} {p['numeric_note']}, "
                     f"external-fact signals {p['external_facts']}); authoritative links: {p['auth_links']}; "
                     f"sources block: {'yes' if p['has_sources'] else 'no'}")
        if p["ex_pct"]:    lines.append(f"- % examples: {', '.join(p['ex_pct'])}")
        if p["ex_dollar"]: lines.append(f"- $ examples: {', '.join(p['ex_dollar'])}")
        if p["ex_stat"]:   lines.append(f"- stat phrases: {', '.join(p['ex_stat'])}")
        if p["ex_legal"]:  lines.append(f"- legal/tax refs: {', '.join(p['ex_legal'])}")
        if p["ex_agency"]: lines.append(f"- agencies named: {', '.join(p['ex_agency'])}")
    report = "\n".join(lines) + "\n"

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w", encoding="utf-8").write(report)

    # concise stdout summary
    print(f"[audit] {len(posts)} posts  HIGH:{counts['HIGH']} MED:{counts['MED']} "
          f"LOW:{counts['LOW']} NONE:{counts['NONE']}")
    print(f"[audit] report -> {REPORT}")
    print("RISK  EXT-FACTS illus# CITES SRC  POST")
    for p in posts:
        print(f"{p['risk']:<5} {p['external_facts']:>9} {p['numeric_claims']:>6} {p['auth_links']:>5} "
              f"{'Y' if p['has_sources'] else '-':>3}  {p['slug']}")
    if show:
        print("\n" + report)

if __name__ == "__main__":
    main()
