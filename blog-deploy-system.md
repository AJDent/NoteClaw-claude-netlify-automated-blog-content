# Blog Deploy System — 5-Step Manual Process

## How It Works
You write the blog in Claude using the prompt below, then follow the 5 steps to review, confirm, and push to Netlify.

---

## Claude Prompt (Copy & Paste This)

```
I need you to build a blog post for takenotescapital.com.

**Blog Topic:** [PASTE YOUR TOPIC HERE]

**Source Content:** [PASTE YOUR DRAFT MARKDOWN OR OUTLINE HERE]

**Instructions:**
1. Use the exact HTML structure from this template file (I'll paste it below)
2. Write the full article in AJ Dent's voice — direct, no-BS, real numbers, real math
3. Include internal links to other TNC blog posts where relevant
4. End with AJ's bio line and Book a Call CTA (https://calendly.com/ajdent-tnc/30min)
5. Write 3 quiz questions that test what the reader just learned
6. Give me the complete, production-ready HTML file

**SEO Requirements:**
- Title tag: Use a "How to" or "What is" format that matches how people search
- Meta description: 155 chars max, include the primary keyword
- Add 10 long-tail keywords in the meta description focused on HOW people search (not industry jargon)
- Use H2s and H3s with keyword-rich headings
- Pull relevant keywords from the Master Keyword Bank below AND generate 3-5 fresh ones specific to this topic

**Master Keyword Bank (use what's relevant per post):**
1. "How to invest in real estate without buying property"
2. "What is a non-performing mortgage note"
3. "How to get higher returns on my 401k"
4. "Can I use my IRA to invest in real estate"
5. "How to invest my retirement account in real estate"
6. "What to do with my IRA to get higher returns"
7. "Can I roll over 401k to buy mortgage notes"
8. "How to make passive income from real estate"
9. "What is the safest real estate investment"
10. "How do I start investing in mortgage notes"
11. "Is note investing better than rental properties"
12. "How to earn cash flow without being a landlord"
13. "What are the best alternatives to stock market investing"
14. "How to build generational wealth with real estate"
15. "What is a self-directed IRA and how does it work"

**Category (pick one):**
- 🏠 Real Estate — market trends, updates, housing market insights
- 📓 Note Investing — educational content (what it is, how it works)
- 💰 Retirement Investing — SDIRA, 401k, IRA strategies
- 🎯 Note Strategies — how to negotiate, structure deals, exit strategies, tactics
- 📊 Deal Breakdown — real deal examples, returns analysis, lessons learned
- 🔗 Other — related to real estate but outside core note investing

**Category colors for the post-cat-tag (use the one matching your category):**
- Note Investing: background:rgba(74,158,222,.15);color:#4a9ede
- Note Strategies: background:rgba(0,201,167,.15);color:#00c9a7
- Retirement Investing: background:rgba(240,165,0,.15);color:#f0a500
- Real Estate: background:rgba(78,203,113,.15);color:#4ecb71
- Deal Breakdown: background:rgba(167,139,250,.15);color:#a78bfa
- Other: background:rgba(156,168,184,.15);color:#9ca8b8

**Template:** [PASTE post-template-lean.html CONTENTS HERE]
```

---

## The 5 Steps (Manual Checklist)

### Step 1: Content Review ✏️
- [ ] Grammar, flow, tone, accuracy
- [ ] Matches AJ's voice (direct, no fluff, real numbers)
- [ ] Internal links to other TNC blogs included
- [ ] Bio + Book a Call CTA at the bottom

### Step 2: SEO Audit 🔍
- [ ] Title tag uses "How to" or "What is" search format
- [ ] Meta description under 155 chars with primary keyword
- [ ] 10 long-tail "how people search" keywords added
- [ ] H2/H3 headings are keyword-rich
- [ ] URL slug matches the topic

### Step 3: HTML Build 🔧
- [ ] Full HTML file built from post-template-lean.html
- [ ] Correct category tag color applied
- [ ] Correct category name displayed
- [ ] Quiz section has 3 relevant questions
- [ ] Comment section included
- [ ] Footer, nav, cookie banner, playbook popup all present

### Step 4: Site Integration 📋
- [ ] Blog listing page (blog.html) updated with new post card
- [ ] "Coming Soon" badge removed from that post's card
- [ ] Card links to correct HTML filename
- [ ] sitemap.xml updated with new URL

### Step 5: Deploy 🚀
- [ ] Save HTML file to NoteClaw-claude-netlify-automated-blog-content/
- [ ] git add, commit, push to main
- [ ] Netlify auto-deploys
- [ ] Verify live URL loads correctly
- [ ] Verify category tag matches inside AND outside

---

## Blog Status

| # | Title | Category | Status |
|---|-------|----------|--------|
| 01 | What Is Non-Performing Note Investing | 📓 Note Investing | ✅ Published |
| 02 | 5 Exit Strategies With Math | 🎯 Note Strategies | ✅ Published |
| 03 | Invest IRA in Mortgage Notes | 💰 Retirement Investing | 📝 Coming Soon |
| 04 | Rentals vs Note Investing | 🔗 Other | 📝 Draft |
| 05 | How Banks Sell Non-Performing Loans | 🏠 Real Estate | 📝 Draft |
| 06 | Deal Breakdown: 34% Return | 📊 Deal Breakdown | 📝 Draft |

---

## Category Reference

| Category | Color | Use For |
|----------|-------|---------|
| 🏠 Real Estate | Green (#4ecb71) | Market trends, updates, housing insights |
| 📓 Note Investing | Blue (#4a9ede) | Educational — what it is, how it works |
| 💰 Retirement Investing | Gold (#f0a500) | SDIRA, 401k, IRA strategies |
| 🎯 Note Strategies | Teal (#00c9a7) | Negotiation, deal structure, exit tactics |
| 📊 Deal Breakdown | Purple (#a78bfa) | Real deals, returns analysis, lessons |
| 🔗 Other | Slate (#9ca8b8) | Related but outside core note investing |
