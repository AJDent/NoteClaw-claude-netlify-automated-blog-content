#!/usr/bin/env python3
"""Report which live TNC blog pages Google has NOT indexed yet.

Uses the Search Console URL Inspection API (read-only). It CANNOT press "Request Indexing"
(Google exposes no API for that), but it tells you exactly which URLs still need a manual
request, so you never waste a click on a page that's already indexed. Optionally posts the
list to Discord (#tnc-blog-reviews).

One-time setup (service account + install): see queue/GSC-MONITOR-SETUP.md.

  python3 queue/gsc_index_monitor.py            # print a report
  python3 queue/gsc_index_monitor.py --discord  # also post the not-indexed list to Discord
"""
import os, sys, json, glob, time, urllib.request, urllib.error

SITE  = "sc-domain:takenotescapital.com"
HOST  = "takenotescapital.com"
ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA_PATH = os.environ.get("GSC_SA_JSON", os.path.expanduser("~/.secrets/gsc-service-account.json"))
SCOPES  = ["https://www.googleapis.com/auth/webmasters.readonly"]
INSPECT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
SKIP = {"index.html", "blog.html", "post-template.html", "post-template-lean.html",
        "cookie-policy.html", "privacy-policy.html", "terms-and-conditions.html",
        "buybox.html", "unsubscribed.html"}
DISCORD_CHANNEL = "1490078388302381126"   # #tnc-blog-reviews
DISCORD_TOKEN_PATH = os.path.expanduser("~/.secrets/discord_bot_token_techwizard")


def get_token():
    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
    except ImportError:
        sys.exit("google-auth not installed. Run:  pip install --user google-auth\n"
                 "(and complete queue/GSC-MONITOR-SETUP.md first)")
    if not os.path.exists(SA_PATH):
        sys.exit(f"service-account JSON not found at {SA_PATH}. See queue/GSC-MONITOR-SETUP.md")
    creds = service_account.Credentials.from_service_account_file(SA_PATH, scopes=SCOPES)
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def inspect(url, tok):
    body = json.dumps({"inspectionUrl": url, "siteUrl": SITE}).encode()
    req = urllib.request.Request(INSPECT, data=body, method="POST",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    return res.get("inspectionResult", {}).get("indexStatusResult", {})


def live_urls():
    os.chdir(ROOT)
    posts = sorted(f for f in glob.glob("*.html") if f not in SKIP)
    return [f"https://{HOST}/{p}" for p in posts]


def post_discord(text):
    try:
        tok = open(DISCORD_TOKEN_PATH).read().strip()
        data = json.dumps({"content": text[:1900]}).encode()
        req = urllib.request.Request(
            f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL}/messages",
            data=data, method="POST",
            headers={"Authorization": f"Bot {tok}", "Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=20)
    except Exception as e:
        print(f"(discord post failed: {e})")


def main():
    tok = get_token()
    urls = live_urls()
    not_indexed = []
    print(f"Inspecting {len(urls)} live pages against Google's index...\n")
    for url in urls:
        try:
            r = inspect(url, tok)
        except urllib.error.HTTPError as e:
            print(f"  !  HTTP {e.code}  {url}\n     {e.read().decode()[:160]}")
            continue
        indexed = r.get("verdict") == "PASS"           # PASS = on Google
        state = r.get("coverageState", "unknown")
        print(f"  {'OK ' if indexed else 'NO '} {state:<42} {url}")
        if not indexed:
            not_indexed.append(url)
        time.sleep(1)                                   # gentle on the API

    print(f"\n{len(urls) - len(not_indexed)}/{len(urls)} indexed. "
          f"{len(not_indexed)} still need a manual Request-Indexing.")
    if not_indexed:
        lines = "\n".join(not_indexed)
        print("\nNOT INDEXED:\n" + lines)
        if "--discord" in sys.argv:
            post_discord(f"🔎 **GSC index check** — {len(not_indexed)} live page(s) NOT indexed by "
                         f"Google yet. Request-Index these in Search Console (URL Inspection → "
                         f"Request Indexing):\n" + lines)
    elif "--discord" in sys.argv:
        post_discord("🔎 **GSC index check** — all live pages are indexed by Google. Nothing to do. ✅")


if __name__ == "__main__":
    main()
