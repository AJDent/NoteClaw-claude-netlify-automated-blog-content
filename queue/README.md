# Friday Publish Queue 🐉

Pre-approved blog posts wait here and go live automatically **every Friday at 10:00 AM ET**
(GitHub Action: `.github/workflows/friday-publish.yml` → `queue/publish_next.py`).

## The rule
**Only fully-built, validated, AJ-APPROVED posts go in this queue.** The queue *is* the
approval gate — the Friday job is mechanical and publishes whatever is at the front of the
line, unattended. Never drop a draft here.

## How to add a post to the queue
1. Build the post per `BLOG-FRAMEWORK.md` (chunked) and get it to **36/36** on `validate-blog.sh`.
2. Get AJ's "lock it".
3. Put the finished HTML file in `queue/` (e.g. `queue/my-slug.html`). Leave its
   `<span class="meta-date">` as anything — the publisher stamps the real publish date.
4. Add an entry to `queue/manifest.json` (order = publish order, first = next Friday):

```json
{
  "queue": [
    {
      "slug": "my-slug",
      "file": "my-slug.html",
      "title": "The Exact Post Title (matches the H1)",
      "category": "Retirement Investing",
      "cat_class": "cat-retire",
      "blurb": "1–2 sentence card blurb for the blog index. No em-dashes.",
      "read_time": "8 min read"
    }
  ]
}
```

`cat_class` values (see `BLOG-FRAMEWORK.md` CATEGORIES):
`cat-note` · `cat-strategy` · `cat-retire` · `cat-re` · `cat-deal` · `cat-edu` · `cat-other`.

## What the Friday job does
- Moves `queue/<slug>.html` → `<slug>.html`, stamps today's ET date into the hero.
- Injects SEO/social/schema via `build_seo.py` — canonical, Open Graph, Twitter card, and
  JSON-LD (`BlogPosting` + `FAQPage` from the quiz), dated to the publish day.
- Inserts the index card at the `<!-- CADENCE:CARDS -->` marker in `blog.html` (newest first).
- Inserts the sitemap URL at the `<!-- CADENCE:URLS -->` marker in `sitemap.xml` (today's `lastmod`).
- Removes the entry from this manifest.
- Runs `validate-blog.sh` — if it fails, it does **not** push.
- Commits + pushes to `main` → Netlify deploys.

## Publish now instead of waiting for Friday
Actions tab → **Friday Publish (blog cadence)** → **Run workflow** (manual runs skip the time gate).

## Test locally without publishing
`python3 queue/publish_next.py` from the repo root, then `git checkout -- blog.html sitemap.xml`
and restore the manifest / moved file to undo.
