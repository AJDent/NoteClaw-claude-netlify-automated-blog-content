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
- Update `sitemap.xml` (add `<url>` entry)
- Git commit + push to main repo
- Deploy to production Netlify URL
- **Final visual check on production** — confirm rendering is correct

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
□ Git committed and pushed
```

---

_This framework lives in the repo. Follow it every time. No exceptions. 🐉_
