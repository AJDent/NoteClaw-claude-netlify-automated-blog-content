#!/usr/bin/env python3
"""TNC weekly blog AUTO-DRAFT — stage 1 of the weekly loop.

Picks the next topic from queue/autodraft-nextup.json, drafts a full blog post with a
headless Claude session (the locked prompt in queue/AUTODRAFT-PROMPT.md), re-validates it
to 37/37 as the authoritative gate, pushes it as an UNLISTED preview (the <slug>.html sits
live at its URL but is NOT in blog.html or sitemap.xml), and pings #tnc-blog-reviews with a
NEEDS REVIEW message carrying the preview URL.

AJ then replies "publish" in Discord -> tnc_blogreview_relay.py -> queue_approved.py moves it
into queue/ -> the Friday cadence (publish_next.py) takes it live. This script only handles
the DRAFT+PREVIEW half; it never publishes and never touches blog.html/sitemap.xml.

Run:
  python3 queue/autodraft_next.py            # normal: draft, validate, push, ping, pop
  python3 queue/autodraft_next.py --dry-run  # draft + validate only; no push/ping/pop
  python3 queue/autodraft_next.py --slug X    # force a specific nextup slug (testing)

Safety: never pushes a draft that fails validate-blog.sh; a failed draft file is removed and
a failure is posted to Discord; the nextup list is left unchanged on failure.
"""
import json, os, re, sys, subprocess, datetime, urllib.request, fcntl

REPO       = os.path.expanduser("~/tnc-blog")
VAULT      = os.path.expanduser("~/noteclaw-backup")
NEXTUP     = os.path.join(REPO, "queue", "autodraft-nextup.json")
PROMPT     = os.path.join(REPO, "queue", "AUTODRAFT-PROMPT.md")
MANIFEST   = os.path.join(REPO, "queue", "manifest.json")
TOKEN_PATH = os.path.expanduser("~/.secrets/discord_bot_token_techwizard")
CHANNEL_ID = "1490078388302381126"                     # #tnc-blog-reviews
API        = "https://discord.com/api/v10"
SITE       = "https://takenotescapital.com"
CLAUDE     = os.path.expanduser("~/.local/bin/claude")
LOCK_FILE  = os.path.expanduser("~/.local/state/tnc-blog-autodraft.lock")
SLUG_RE    = re.compile(r'[a-z0-9][a-z0-9-]{1,80}\Z')
DRAFT_TIMEOUT = 1200                                    # 20 min hard cap on the headless build

os.chdir(REPO)

def log(m): print(f"[autodraft] {m}", flush=True)

def discord_post(content):
    """Post to #tnc-blog-reviews with the tech-wizard bot, matching the relay's method."""
    try:
        token = open(TOKEN_PATH).read().strip()
        data = json.dumps({"content": content[:1900]}).encode()
        req = urllib.request.Request(f"{API}/channels/{CHANNEL_ID}/messages", data=data, method="POST")
        req.add_header("Authorization", f"Bot {token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "tnc-blog-autodraft/1.0")   # Discord/Cloudflare needs a UA
        urllib.request.urlopen(req, timeout=30)
        log("posted to #tnc-blog-reviews")
    except Exception as e:
        log(f"WARN: Discord post failed: {e}")

def manifest_slugs():
    try:
        data = json.load(open(MANIFEST, encoding="utf-8"))
        return {e.get("slug") for e in data.get("queue", [])}
    except FileNotFoundError:
        return set()

def is_taken(slug):
    """A slug is taken if it is already published (root <slug>.html), already an unlisted
    preview (also root), already sitting in queue/, or already a manifest entry."""
    return (os.path.exists(os.path.join(REPO, f"{slug}.html"))
            or os.path.exists(os.path.join(REPO, "queue", f"{slug}.html"))
            or slug in manifest_slugs())

def load_nextup():
    return json.load(open(NEXTUP, encoding="utf-8"))

def pick_next(force_slug=None):
    data = load_nextup()
    for entry in data.get("nextup", []):
        slug = entry.get("slug", "")
        if not SLUG_RE.match(slug):
            log(f"skip invalid slug in nextup: {slug!r}"); continue
        if force_slug and slug != force_slug:
            continue
        if is_taken(slug):
            log(f"skip {slug} (already published/queued/previewed)"); continue
        return entry
    return None

def build_prompt(entry):
    tpl = open(PROMPT, encoding="utf-8").read()
    return (tpl.replace("{SLUG}", entry["slug"])
               .replace("{CATEGORY}", entry["category"])
               .replace("{TOPIC}", entry["topic"])
               .replace("{ANGLE}", entry.get("angle", "")))

def run_draft(entry):
    """Invoke the headless Claude build. Returns True if the file now exists."""
    prompt = build_prompt(entry)
    slug = entry["slug"]
    cmd = [CLAUDE, "-p", prompt,
           "--permission-mode", "bypassPermissions",
           "--model", "opus",
           "--add-dir", VAULT]
    log(f"drafting {slug}.html via headless claude (timeout {DRAFT_TIMEOUT}s)...")
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=DRAFT_TIMEOUT)
    except subprocess.TimeoutExpired:
        log("ERROR: draft timed out"); return False
    tail = (r.stdout or "")[-500:]
    log(f"claude exit={r.returncode}; tail: {tail!r}")
    return os.path.exists(os.path.join(REPO, f"{slug}.html"))

def validate(slug):
    r = subprocess.run(["bash", "validate-blog.sh", f"{slug}.html"],
                       cwd=REPO, capture_output=True, text=True)
    ok = r.returncode == 0
    m = re.search(r'RESULTS:\s*(\d+ passed / \d+ failed)', r.stdout or "")
    return ok, (m.group(1) if m else "no results line"), r.stdout

def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)

def push_preview(slug):
    git("add", f"{slug}.html")
    c = git("commit", "-m", f"Auto-draft unlisted preview: {slug} (weekly cadence, NEEDS REVIEW)")
    if c.returncode != 0:
        return False, c.stderr.strip()[:300]
    p = git("push", "origin", "main")
    if p.returncode != 0:
        return False, p.stderr.strip()[:300]
    return True, ""

def pop_nextup(slug):
    data = load_nextup()
    data["nextup"] = [e for e in data.get("nextup", []) if e.get("slug") != slug]
    json.dump(data, open(NEXTUP, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(NEXTUP, "a").write("\n")
    git("add", NEXTUP)
    git("commit", "-m", f"Auto-draft: pop {slug} from nextup (drafted + previewed)")
    git("push", "origin", "main")

def main():
    dry = "--dry-run" in sys.argv
    force = None
    if "--slug" in sys.argv:
        force = sys.argv[sys.argv.index("--slug") + 1]

    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    lock = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("another autodraft run holds the lock; exiting."); sys.exit(0)

    # Sync first: the Friday cadence + the blog-review relay push to origin from elsewhere, so
    # the local clone can be behind. Draft/push on a stale tree would fail the push (non-ff) and
    # mis-read which slugs are already taken. Fast-forward only; never merge/rebase unattended.
    pull = git("pull", "--ff-only", "origin", "main")
    if pull.returncode != 0:
        log(f"WARN: git pull --ff-only failed (local may have diverged): {pull.stderr.strip()[:300]}")
        if not dry:
            discord_post("⚠️ Auto-draft could not fast-forward the blog repo (local diverged from "
                         "origin/main). Skipped this week to avoid a bad push. A session should reconcile it.")
            sys.exit(1)

    entry = pick_next(force)
    if not entry:
        log("nothing to draft (nextup empty or all taken).")
        if not dry:
            discord_post("🐉 Auto-draft: the `autodraft-nextup.json` list is empty or every "
                         "topic is already published/queued. Add topics to keep the Friday cadence fed.")
        sys.exit(0)

    slug = entry["slug"]
    log(f"next topic -> {slug}  [{entry['category']}]")

    if not run_draft(entry):
        log(f"ERROR: draft did not produce {slug}.html")
        # remove any partial so the slug isn't falsely 'taken' next week
        p = os.path.join(REPO, f"{slug}.html")
        if os.path.exists(p): os.remove(p)
        if not dry:
            discord_post(f"⚠️ Auto-draft FAILED to build **{slug}** (no file produced). "
                         "Left the topic in the queue to retry next week; a session can build it by hand.")
        sys.exit(1)

    ok, result, out = validate(slug)
    log(f"validator: {result}")
    if not ok:
        log("validator failed — NOT pushing.")
        os.remove(os.path.join(REPO, f"{slug}.html"))
        if not dry:
            discord_post(f"⚠️ Auto-draft built **{slug}** but it failed the validator "
                         f"({result}). Not pushed. Left in the queue to retry.")
        sys.exit(1)

    if dry:
        log(f"[dry-run] {slug}.html validated {result}. Not pushing/pinging/popping.")
        log(f"[dry-run] preview file left at {slug}.html for inspection.")
        sys.exit(0)

    pushed, err = push_preview(slug)
    if not pushed:
        log(f"ERROR: push failed: {err}")
        discord_post(f"⚠️ Auto-draft built + validated **{slug}** but the push failed. "
                     f"Run `git push` from a session.\n```\n{err}\n```")
        sys.exit(1)

    url = f"{SITE}/{slug}.html"
    discord_post(
        f"🐉 **REVIEW NEW BLOG — NEEDS REVIEW**\n"
        f"**{entry.get('topic', slug)}**\n"
        f"Category: {entry['category']}\n"
        f"Preview (unlisted, live): {url}\n\n"
        f"Reply **publish** to queue it for the next Friday, or reply with edits."
    )
    pop_nextup(slug)
    log(f"done: {slug} previewed + pinged for review.")

if __name__ == "__main__":
    main()
