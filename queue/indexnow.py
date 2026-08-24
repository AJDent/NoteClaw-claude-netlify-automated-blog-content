#!/usr/bin/env python3
"""Submit URLs to IndexNow so Bing + Yandex pick up new/changed pages fast.

Google does NOT use IndexNow, but Bing and Yandex do, and it's free + near-instant. The key
is public by design (hosted at https://takenotescapital.com/<key>.txt), so nothing secret
lives here. The Friday cadence calls this after publishing a post; also runnable by hand:

  python3 queue/indexnow.py https://takenotescapital.com/foo.html [more urls...]
  python3 queue/indexnow.py --all        # submit every live blog page + home + blog index
"""
import sys, os, json, glob, urllib.request, urllib.error

HOST = "takenotescapital.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = open(os.path.join(ROOT, ".indexnow-key")).read().strip()
ENDPOINT = "https://api.indexnow.org/indexnow"   # shared endpoint; forwards to Bing/Yandex

SKIP = {"index.html", "blog.html", "post-template.html", "post-template-lean.html",
        "cookie-policy.html", "privacy-policy.html", "terms-and-conditions.html",
        "buybox.html", "unsubscribed.html"}

def all_urls():
    os.chdir(ROOT)
    posts = sorted(f for f in glob.glob("*.html") if f not in SKIP)
    urls = [f"https://{HOST}/", f"https://{HOST}/blog.html"]
    urls += [f"https://{HOST}/{p}" for p in posts]
    return urls

def submit(urls):
    if not urls:
        print("IndexNow: no urls to submit"); return True
    payload = {"host": HOST, "key": KEY,
               "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            print(f"IndexNow: submitted {len(urls)} url(s) -> HTTP {r.status}")
            return True
    except urllib.error.HTTPError as e:
        # 200/202 = accepted; IndexNow often returns 202. Anything else is logged, not fatal.
        body = e.read().decode()[:200]
        print(f"IndexNow HTTP {e.code}: {body}")
        return e.code in (200, 202)
    except Exception as e:
        print(f"IndexNow error: {e}")
        return False

if __name__ == "__main__":
    args = sys.argv[1:]
    urls = all_urls() if (args and args[0] == "--all") else args
    ok = submit(urls)
    sys.exit(0 if ok else 1)
