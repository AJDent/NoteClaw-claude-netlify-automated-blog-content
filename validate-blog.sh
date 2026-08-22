#!/bin/bash
# TNC Blog Post Validator
# Usage: ./validate-blog.sh <filename.html>

FILE="$1"
if [ -z "$FILE" ]; then echo "Usage: ./validate-blog.sh <filename.html>"; exit 1; fi
if [ ! -f "$FILE" ]; then echo "❌ File not found: $FILE"; exit 1; fi

PASS=0
FAIL=0

check() {
  if [ "$1" -eq 0 ]; then
    echo "  ✅ $2"
    PASS=$((PASS+1))
  else
    echo "  ❌ $2"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════"
echo "  TNC Blog Validator — $FILE"
echo "═══════════════════════════════════════"
echo ""

echo "📋 STRUCTURE"
grep -q '<!DOCTYPE html>' "$FILE"; check $? "DOCTYPE present"
grep -q '<html lang="en">' "$FILE"; check $? '<html lang="en"> present'
grep -q '<title>' "$FILE"; check $? "<title> tag present"
grep -q '<meta name="description"' "$FILE"; check $? "Meta description present"
grep -q '<meta name="keywords"' "$FILE"; check $? "Meta keywords present"
grep -q 'blog.css' "$FILE"; check $? "blog.css linked"
grep -q 'blog.js' "$FILE"; check $? "blog.js linked"
grep -q '</html>' "$FILE"; check $? "Closing </html> present"
echo ""

echo "🎨 HERO & NAV"
grep -q 'class="nav-logo"' "$FILE"; check $? "Nav present"
grep -q 'post-hero' "$FILE"; check $? "Post hero section present"
grep -q 'post-cat-tag' "$FILE"; check $? "Category tag present"
grep -q 'meta-date' "$FILE"; check $? "Date present"
grep -q 'meta-read' "$FILE"; check $? "Read time present"
grep -q 'author-avatar' "$FILE"; check $? "Author avatar present"
# Hero background gradient MUST match the post's category color (not the generic var(--navy)).
# Cloning the lean template leaves a generic navy hero; this catches it so the category color is never missed.
CAT=$(grep -oE 'class="post-cat-tag"[^>]*>[^<]+</span>' "$FILE" | head -1 | sed -E 's/.*>([^<]+)<\/span>/\1/')
case "$CAT" in
  "Note Investing")               WANT="#1a3a6b" ;;
  "Note Strategies")              WANT="#3d0a0a" ;;
  "Retirement Investing")         WANT="#3d2e0a" ;;
  "Real Estate")                  WANT="#0f3d1e" ;;
  "Deal Breakdown"|"Deal Breakdowns") WANT="#2d1f5e" ;;
  "Education")                    WANT="#0d2a4a" ;;
  "Other")                        WANT="#2a2f38" ;;
  *)                              WANT="" ;;
esac
if [ -n "$WANT" ]; then
  # format-agnostic: the invariant is the gradient END color = the category color
  # (older posts use 135deg/#0d1428, newer use 180deg/#0a0a1a; both are fine).
  HEROBG=$(grep -A3 '\.post-hero {' "$FILE" | grep 'background:' | head -1)
  echo "$HEROBG" | grep -q "$WANT"; check $? "Hero gradient matches category ($CAT -> $WANT)"
else
  false; check $? "Hero category recognized for gradient check (got '$CAT')"
fi
echo ""

echo "📝 CONTENT"
grep -q 'post-content' "$FILE"; check $? "Post content div present"
grep -q 'post-layout' "$FILE"; check $? "Post layout wrapper present"
H2COUNT=$(grep -c '<h2>' "$FILE")
[ "$H2COUNT" -ge 2 ]; check $? "At least 2 H2 sections ($H2COUNT found)"
grep -q 'post-divider' "$FILE"; check $? "Post divider present"
grep -q 'calendly.com/ajdent-tnc' "$FILE"; check $? "Calendly CTA link present"
echo ""

echo "🧠 QUIZ"
grep -q 'quizSection\|quizContainer' "$FILE"; check $? "Quiz section present"
grep -q 'quizData' "$FILE"; check $? "Quiz data array present"
QCOUNT=$(grep -c 'question:' "$FILE")
[ "$QCOUNT" -ge 3 ]; check $? "At least 3 quiz questions ($QCOUNT found)"
grep -q 'quizCapture\|quizCaptureForm' "$FILE"; check $? "Quiz email capture present"
echo ""

echo "💬 COMMENTS & CTA"
grep -q 'id="comments"' "$FILE"; check $? "Comments section present"
grep -q 'commentForm' "$FILE"; check $? "Comment form present"
grep -q 'Book a Free' "$FILE"; check $? "Bottom CTA present"
echo ""

echo "🦶 FOOTER & BANNERS"
grep -q '<footer>' "$FILE"; check $? "Footer present"
grep -q 'footer-socials' "$FILE"; check $? "Social links present"
grep -q 'footer-legal' "$FILE"; check $? "Legal links present"
grep -q 'playbookBanner' "$FILE"; check $? "Playbook banner present"
grep -q 'exitPopup' "$FILE"; check $? "Exit popup present"
grep -q 'cookieBanner' "$FILE"; check $? "Cookie banner present"
grep -q 'cookiePanel' "$FILE"; check $? "Cookie settings panel present"
grep -q 'book-call-float' "$FILE"; check $? "Floating call button present"
echo ""

echo "🚨 PLACEHOLDER CHECK"
PLACEHOLDERS=$(grep -cE '\[POST TITLE\]|\[META|\[PLACEHOLDER|\[CATEGORY|\[DATE\]|\[QUIZ|\[X\] min|\[HERO_GRADIENT_END\]' "$FILE")
[ "$PLACEHOLDERS" -eq 0 ]; check $? "No placeholder text remaining ($PLACEHOLDERS found)"
echo ""

echo "📐 DIV BALANCE"
OPENS=$(grep -o "<div" "$FILE" | wc -l)
CLOSES=$(grep -o "</div>" "$FILE" | wc -l)
[ "$OPENS" -eq "$CLOSES" ]; check $? "Div tags balanced (open=$OPENS close=$CLOSES)"
echo ""

echo "═══════════════════════════════════════"
echo "  RESULTS: $PASS passed / $FAIL failed"
if [ "$FAIL" -eq 0 ]; then
  echo "  🎉 ALL CHECKS PASSED — Ready to deploy!"
else
  echo "  🚫 FIX $FAIL ISSUES BEFORE DEPLOYING"
fi
echo "═══════════════════════════════════════"
exit $FAIL
