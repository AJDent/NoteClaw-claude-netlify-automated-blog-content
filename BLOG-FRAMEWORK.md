# TNC Blog Post Build Framework 🐉

**Purpose:** Ensure every blog post is built correctly, in chunks, with full template structure and zero mistakes.

---

## ⚠️ GOLDEN RULES

1. **NEVER write a full blog in one shot.** Always chunk it (5-6 chunks minimum).
2. **NEVER start writing content until the planning chunk is approved.**
3. **ALWAYS verify each chunk compiled correctly before moving to the next.**
4. **ALWAYS run the SEO smoke test before pushing to Netlify.**
5. **Use `edit` tool for incremental additions — NOT one giant `write`.**

---

## 📋 CHUNK SEQUENCE

Every blog post follows this exact sequence. No skipping steps.

### CHUNK 0: PLANNING (Do not write any HTML yet)

Before ANY code is written, produce and confirm:

```
□ Post title (final, SEO-optimized)
□ Slug (URL-safe filename, e.g., "how-does-an-sdira-work.html")
□ Category + color (see CATEGORIES below)
□ Meta description (≤155 chars, includes primary keyword)
□ Keywords meta (10 long-tail search phrases)
□ Target word count (~1,500-2,500 words)
□ Read time estimate (words ÷ 250, rounded)
□ H2 outline (all section headers, in order)
□ Quiz questions (3 questions, 4 options each, correct answer + explanation)
□ Publish date
```

**STOP HERE.** Get AJ's approval on the outline before continuing.

---

### CHUNK 1: HTML SHELL (Head + Hero + Nav)

Write the file with:
- `<!DOCTYPE html>` + `<html lang="en">`
- Full `<head>` block (title, meta description, meta keywords, fonts, blog.css, inline `<style>`)
- `<body>` open
- `<nav>` (standard TNC nav)
- `<header class="post-hero">` (category tag, date, read time, discuss badge, h1, excerpt, author row)

**Verify:** File starts with `<!DOCTYPE html>` and hero renders all metadata.

---

### CHUNK 2: BODY CONTENT — FIRST HALF

Inside `<div class="post-layout"><div class="post-content">`:
- Opening paragraphs (hook/intro)
- First 2-3 H2 sections with full content

**Verify:** Content sits inside `.post-content` div. No unclosed tags.

---

### CHUNK 3: BODY CONTENT — SECOND HALF

Continue inside `.post-content`:
- Remaining H2/H3 sections
- Closing paragraphs
- Author bio block with `<hr class="post-divider">`
- Close `.post-content` div

**Verify:** All H2s from outline are present. `.post-content` div is closed.

---

### CHUNK 4: QUIZ + COMMENTS + CTA

After the `.post-content` div closes, still inside `.post-layout`:
- Quiz section (`#quizSection`) with header, container, results, email capture
- Comments section (`#comments`) with form
- Bottom CTA (Book a Call button)
- Close `.post-layout` div

**Verify:** Quiz section has 3 questions in the `quizData` array. All IDs present.

---

### CHUNK 5: FOOTER + SCRIPTS + CLOSING

After `.post-layout` closes:
- `<footer>` (logo, socials, links, legal, tagline, copyright)
- Floating "Book a Free Call" button
- Playbook banner
- Exit popup
- Cookie banner + cookie panel
- `<script>` block with quiz data array
- `<script src="blog.js"></script>`
- Close `</body></html>`

**Verify:** File ends with `</body></html>`. Run integrity check.

---

### CHUNK 6: VALIDATION & DEPLOY

Run ALL of these before pushing:

```bash
# 1. SEO smoke test — no placeholders
grep -E "\[POST TITLE\]|\[META|\[PLACEHOLDER|\[CATEGORY|\[DATE\]|\[QUIZ" FILE.html && echo "❌ STOP" || echo "✅ clean"

# 2. Structure check — has required elements
grep -c "<!DOCTYPE html>" FILE.html   # must be 1
grep -c "<html lang=\"en\">" FILE.html # must be 1
grep -c "post-hero" FILE.html          # must be ≥1
grep -c "quizSection" FILE.html        # must be ≥1
grep -c "blog.js" FILE.html            # must be ≥1
grep -c "</html>" FILE.html            # must be 1

# 3. Tag balance check
grep -o "<div" FILE.html | wc -l       # count opens
grep -o "</div>" FILE.html | wc -l     # count closes (should match)

# 4. HTML validation (quick)
python3 -c "
from html.parser import HTMLParser
import sys
class V(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
    def handle_starttag(self, tag, attrs): pass
    def handle_endtag(self, tag): pass
p = V()
with open(sys.argv[1]) as f:
    try:
        p.feed(f.read())
        print('✅ Parses OK')
    except Exception as e:
        print(f'❌ Parse error: {e}')
" FILE.html
```

**🚨 CRITICAL NEW STEP — VISUAL VERIFICATION:**

**Before any push to Netlify, you MUST manually verify the post renders correctly.**

**Checklist (verify all before deploying):**
```
□ Hero section displays (category badge, h1, excerpt, date, author)
□ Post content flows properly (no layout breaks, proper spacing)
□ Tables render correctly (if any)
□ Quiz section displays with all 3 questions visible
□ Footer renders properly
□ Responsive on mobile (at minimum, check 375px width)
□ No CSS errors in browser console
□ Links work (internal nav, Calendly CTAs, external links)
```

**Why this is MANDATORY:**
- HTML can parse correctly but still render visually broken
- CSS loading issues won't show up in text validation
- This catches layout problems before they go live
- Broken blogs on live site = bad user experience

**How to verify:**
1. Deploy to Netlify (test/staging first if possible)
2. Open the live URL in a real browser
3. Visually scan: hero → content sections → quiz → footer
4. If ANYTHING looks broken/misaligned → STOP, rebuild, DO NOT PUSH
5. Only after visual sign-off: push to production
6. Re-verify on production URL (confirm it still renders correctly)

Then:
- Update `blog.html` (add card to index)
- Update `sitemap.xml` (add `<url>` entry — **MANDATORY, see Sitemap Update section below**)
- Git commit + push to main repo
- Deploy to production Netlify URL
- **Final visual check on production** — confirm rendering is correct

---

## 🗺️ SITEMAP UPDATE (MANDATORY — EVERY POST)

**Every new blog post MUST be added to `sitemap.xml` immediately.** No exceptions.

Google can only index what it knows about. If a post isn't in the sitemap, it's invisible to search engines.

### How to add a new entry:

Add this block inside `<urlset>`, ordered by date (newest first, after the homepage and blog.html entries):

```xml
  <url>
    <loc>https://takenotescapital.com/YOUR-SLUG.html</loc>
    <lastmod>YYYY-MM-DD</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
```

### Sitemap structure (always maintain this order):
1. Homepage (`/`) — priority 1.0, changefreq weekly
2. Blog index (`/blog.html`) — priority 0.9, changefreq daily
3. All blog posts — priority 0.8, changefreq monthly, ordered newest → oldest

### Verification after adding:
```bash
# Count blog HTML files (excluding non-blog pages)
ls *.html | grep -v -E '(index|blog|post-template|cookie-policy|privacy-policy|terms-and-conditions|buybox)' | wc -l

# Count sitemap blog entries (subtract 2 for homepage + blog.html)
grep -c '<loc>' sitemap.xml

# These numbers should match: blog files + 2 = sitemap entries
```

### Why this was added:
On 2026-06-16, we discovered only 4 of 19 blog posts were in the sitemap. Google only knew about 4 pages. This rule ensures it never happens again.

---

## 🏷️ CATEGORIES

⚠️ **THESE ARE THE ONLY ALLOWED CATEGORIES. DO NOT invent new ones unless AJ explicitly asks.**

| # | Category | CSS Class | Emoji | Card Gradient | Hero Gradient |
|---|----------|-----------|-------|---------------|---------------|
| 1 | Note Investing | `cat-note` | 📓 | `#0d1428 → #1a3a6b` | same |
| 2 | Note Strategies | `cat-strategy` | 🎯 | `#0d1428 → #3d0a0a` | same |
| 3 | Retirement Investing | `cat-retire` | 💰 | `#0d1428 → #3d2e0a` | same |
| 4 | Real Estate | `cat-re` | 🏠 | `#0d1428 → #0f3d1e` | same |
| 5 | Deal Breakdowns | `cat-deal` | 📊 | `#0d1428 → #2d1f5e` | same |
| 6 | Education | `cat-edu` | 📚 | `#0d1428 → #0d2a4a` | same |
| 7 | Other | `cat-other` | 🔗 | `#0d1428 → #2a2f38` | same |

**How to pick a category:**
- RMDs, SDIRAs, 401k, IRA investing → **💰 Retirement Investing** (`cat-retire`)
- General note concepts, what is a note, NPNs → **📓 Note Investing** (`cat-note`)
- Exit strategies, pricing, underwriting tactics → **🎯 Note Strategies** (`cat-strategy`)
- Real deal walkthroughs with numbers → **📊 Deal Breakdowns** (`cat-deal`)
- Broader RE concepts, landlord comparisons, market stuff → **🏠 Real Estate** (`cat-re`)
- Educational/explainer content that doesn't fit above → **📚 Education** (`cat-edu`)
- Anything else → **🔗 Other** (`cat-other`)

### 🎨 Hero category PILL — use the INLINE style, not just the class (added 2026-08-20)
The hero category tag gets its pill color from an **inline `style`**, NOT from the `cat-*` class (the class
only colors the blog-index *card*, so a class-only hero tag renders as plain text with no pill). Copy the
exact inline style from an existing post of the same category. Locked map:

| Category | Hero pill inline style | Hero gradient end |
|---|---|---|
| 📓 Note Investing | `background:rgba(74,158,222,0.15);color:#4a9ede;` | `#1a3a6b` |
| 🎯 Note Strategies | `background:rgba(232,93,93,0.15);color:#e85d5d;` | `#3d0a0a` |
| 💰 Retirement Investing | `background:rgba(240,165,0,0.16);color:#f0a500;` | `#3d2e0a` |
| 🏠 Real Estate | `background:rgba(78,203,113,0.15);color:#4ecb71;` | `#0f3d1e` |
| 📊 Deal Breakdowns | `background:rgba(167,139,250,0.15);color:#a78bfa;` | `#2d1f5e` |
| 🔗 Other | `background:rgba(156,168,184,0.15);color:#9ca8b8;` | `#2a2f38` |

Hero background = `linear-gradient(180deg, #0a0a1a 0%, <end> 100%)`. Blog category colors (incl. amber) are
**EXEMPT** from the no-gold brand rule — they are this framework's own system (vault CLAUDE.md, 2026-08-20).

⚠️ **DO NOT leave the hero background as the template default (`var(--navy)` / `[HERO_GRADIENT_END]`).** Cloning
`post-template-lean.html` ships a generic navy hero that does NOT match the category (it looks flat/"transparent").
Set the gradient END color to the category value in the table above. **The validator now enforces this** (HERO & NAV
→ "Hero gradient matches category"), so a mismatch fails `validate-blog.sh` and the monthly audit. Both the older
`linear-gradient(135deg, #0d1428, <end>)` and newer `linear-gradient(180deg, #0a0a1a 0%, <end> 100%)` formats pass;
the invariant the validator checks is the END color = the category color. (Root cause of the 2026-08-21 fix: the lean
template hardcoded `var(--navy)`, and 3 live posts had shipped mismatched heroes before the check existed.)

---

## 🔎 SEO + SCHEMA (added 2026-08-20 — every post)
Every post ships with canonical + Open Graph + Twitter card + JSON-LD (`BlogPosting` + `FAQPage` from the
quiz). Do NOT hand-write these — run **`build_seo.py <file>`** (repo root; idempotent). The Friday cadence
auto-injects them at publish, so **queued posts should NOT be pre-run through `build_seo.py`** (let the
cadence stamp the real publish date into the schema).

## 🗣️ VOICE (the validator does NOT catch these — check by eye)
- **NO em-dashes (—) in published copy.** Ever. Use periods or commas. (Site-wide cleanup pending 2026-08-20.)
- Never use: crucial, robust, leverage, delve, nuanced, multifaceted.
- Customer-facing copy runs through the **`tnc-copywriting-persuasion`** skill first (business standing rule).

## 📊 DEAL-BREAKDOWN NUMBER INTEGRITY (added 2026-08-20 — HARD RULE)
Deal breakdowns make performance claims, so the numbers are a compliance surface, not decoration:
- The **headline number MUST match the body.** (2026-08-20: `deal-breakdown-atlanta` shipped a "$13,460 profit /
  156% return" headline while its own body table showed **−$6,835** net at 6 months — false and self-contradicting.)
- **Every table must foot** (line items sum to the stated total) and figures must reconcile across sections.
- **Never invent numbers.** Use the real (anonymized) deal figures: no names, city+state only, round figures.
- If the numbers do not reconcile, do NOT publish — flag AJ for the real figures.

## ⏰ FRIDAY PUBLISH CADENCE (added 2026-08-20)
Approved posts go in **`queue/`** + a `queue/manifest.json` entry; a GitHub Action publishes the next one
every Friday 10 AM ET (`.github/workflows/friday-publish.yml` → `queue/publish_next.py`). The queue IS the
approval gate. Full how-to: `queue/README.md`.

---

## 📐 TEMPLATE REFERENCE

The canonical template is: `post-template-lean.html`

Every post must match this structure exactly. Sections in order:
1. DOCTYPE + head (meta + styles)
2. Nav
3. Post Hero header
4. Post Layout > Post Content (article body)
5. Quiz Section
6. Comments Section
7. Bottom CTA
8. Footer
9. Floating Book a Call
10. Playbook Banner
11. Exit Popup
12. Cookie Banner + Panel
13. Quiz Data script
14. blog.js script tag

---

## 🚨 COMMON MISTAKES TO AVOID

- ❌ Writing content without the HTML shell first
- ❌ Forgetting `<html lang="en">`
- ❌ Leaving `[PLACEHOLDER]` text in the final file
- ❌ Missing the `<meta name="keywords">` tag
- ❌ Skipping the quiz section
- ❌ Not closing `.post-layout` or `.post-content` divs
- ❌ Forgetting to update `blog.html` index and `sitemap.xml`
- ❌ Starting body content at line 1 without doctype/head (← what broke the SDIRA post)
- ❌ Publishing without running the validation checks

---

## 🔄 FIXING AN EXISTING BROKEN POST

If a post exists but is malformed (like missing the shell):

1. **Extract** the body content from the broken file
2. **Start fresh** — write CHUNK 1 (shell) as a new file
3. **Inject** the existing body content as CHUNK 2-3
4. **Add** quiz/comments/footer as CHUNK 4-5
5. **Validate** with CHUNK 6 checks
6. **Replace** the broken file with the fixed version

---

## ✅ PRE-PUSH CHECKLIST

Before EVERY blog deploy:

```
□ File starts with <!DOCTYPE html>
□ <html lang="en"> present
□ <title> has real title (no placeholders)
□ <meta name="description"> filled (≤155 chars)
□ <meta name="keywords"> has 10 long-tail phrases
□ Hero section has: category tag, date, read time, h1, excerpt, author
□ Body content has all H2 sections from outline
□ Quiz has 3 complete questions with correct answers
□ Comments section present
□ Footer present with all links
□ Cookie/popup/playbook banners present
□ blog.js script tag present
□ File ends with </body></html>
□ Div open/close count matches
□ No placeholder text remaining
□ blog.html updated with new card
□ sitemap.xml updated with new URL
□ Sitemap entry count verified (blog files + 2 = total <loc> entries)
□ Git committed and pushed
```

---

_This framework lives in the repo. Follow it every time. No exceptions. 🐉_
