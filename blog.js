/* ============================================================
   TNC BLOG — Shared JavaScript
   blog.js
   ============================================================ */

/* ── CONSTANTS ── */
const GHL_WEBHOOK     = 'https://hooks.leadconnectorhq.com/webhook/REPLACE_WITH_GHL_WEBHOOK_ID';
const GHL_COMMENTS    = 'https://hooks.leadconnectorhq.com/webhook/REPLACE_WITH_GHL_COMMENTS_WEBHOOK_ID';
const SUBSCRIBED_KEY  = 'tnc_blog_subscribed';
const POPUP_CLOSE_KEY = 'tnc_popup_closed_until';
const COOKIE_KEY      = 'tnc_cookie_consent';

const BUCKET_MAP = {
  'sdira':    'Self-Directed IRA Holder',
  '401k':     '401(k) / Solo 401(k) Holder',
  'private':  'Private Capital / Cash Investor',
  'learning': 'Just Learning About Note Investing'
};

/* ── GHL SUBMIT ── */
function submitToGHL(data, webhookUrl) {
  const url = webhookUrl || GHL_WEBHOOK;
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).catch(() => {});
}

/* ── SUBSCRIPTION STATE ── */
function markSubscribed() {
  localStorage.setItem(SUBSCRIBED_KEY, '1');
  const nextAllowed = Date.now() + (7 * 24 * 60 * 60 * 1000);
  localStorage.setItem(POPUP_CLOSE_KEY, String(nextAllowed));
}
function isSubscribed()  { return localStorage.getItem(SUBSCRIBED_KEY) === '1'; }
function popupBlocked()  {
  const raw = localStorage.getItem(POPUP_CLOSE_KEY);
  return raw && Number(raw) > Date.now();
}

/* ── POPUP ── */
let popupShown = false;

function showPopup() {
  if (popupShown || isSubscribed() || popupBlocked()) return;
  popupShown = true;
  const overlay = document.getElementById('exitPopup');
  if (overlay) overlay.classList.add('active');
}

function closePopup(skipBlock) {
  const overlay = document.getElementById('exitPopup');
  if (overlay) overlay.classList.remove('active');
  if (!skipBlock && !isSubscribed()) {
    const nextAllowed = Date.now() + (7 * 24 * 60 * 60 * 1000);
    localStorage.setItem(POPUP_CLOSE_KEY, String(nextAllowed));
  }
}

function submitPopup() {
  const firstName = document.getElementById('popupName')?.value.trim();
  const email     = document.getElementById('popupEmail')?.value.trim();
  const bucket    = document.getElementById('popupProfile')?.value || '';
  if (!firstName || !email) { alert('Please fill in your name and email.'); return; }

  submitToGHL({
    firstName,
    email,
    investorType: BUCKET_MAP[bucket] || bucket,
    tags: ['blog-lead', 'playbook-request']
  });

  markSubscribed();
  hideBanner();
  document.getElementById('popupForm').style.display = 'none';
  document.getElementById('popupSuccess').style.display = 'block';
}

/* ── EXIT INTENT TRIGGERS ── */
document.addEventListener('mouseleave', e => {
  if (window.innerWidth > 768 && e.clientY <= 10) showPopup();
});
setTimeout(() => { if (!isSubscribed()) showPopup(); }, 30000);

let lastY = 0;
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (window.innerWidth <= 768 && y < lastY && y > 300) showPopup();
  lastY = y;
}, { passive: true });

/* ── PLAYBOOK BANNER ── */
function showBanner() {
  if (isSubscribed()) return;
  const b = document.getElementById('playbookBanner');
  if (b) b.classList.add('visible');
}
function hideBanner() {
  const b = document.getElementById('playbookBanner');
  if (b) b.classList.remove('visible');
}

setTimeout(showBanner, 8000);

/* ── NEWSLETTER BAR ── */
function handleNewsletterBar(e) {
  e.preventDefault();
  const firstName = document.getElementById('barName')?.value.trim() || '';
  const email     = document.getElementById('barEmail')?.value.trim();
  const bucket    = document.getElementById('barProfile')?.value || '';
  if (!email) return;

  submitToGHL({
    firstName,
    email,
    investorType: BUCKET_MAP[bucket] || bucket,
    tags: ['blog-lead', 'newsletter-bar']
  });

  markSubscribed();
  hideBanner();
  const form = document.getElementById('newsletterBarForm');
  if (form) form.innerHTML = '<p class="subscribe-success">✓ You\'re in! Watch your inbox for the next brief. 📬</p>';
}

/* ── MINI CTA (quiz capture) ── */
function submitMiniCTA(e) {
  e.preventDefault();
  const firstName = document.getElementById('miniName')?.value.trim() || '';
  const email     = document.getElementById('miniEmail')?.value.trim();
  const bucket    = document.getElementById('miniProfile')?.value || '';
  if (!email) return;

  submitToGHL({
    firstName,
    email,
    investorType: BUCKET_MAP[bucket] || bucket,
    tags: ['blog-lead', 'quiz-capture']
  });

  markSubscribed();
  const form = e.target;
  form.innerHTML = '<p class="subscribe-success">✓ You\'re in! Check your inbox. 📬</p>';
}

/* ── QUIZ ENGINE ── */
function initQuiz(quizData) {
  const container = document.getElementById('quizContainer');
  if (!container || !quizData || !quizData.length) return;

  let answers = new Array(quizData.length).fill(null);
  let completed = false;

  function render() {
    container.innerHTML = '';

    quizData.forEach((q, qi) => {
      const qBlock = document.createElement('div');
      qBlock.className = 'quiz-question';

      const qText = document.createElement('p');
      qText.className = 'quiz-q-text';
      qText.textContent = `${qi + 1}. ${q.question}`;
      qBlock.appendChild(qText);

      const opts = document.createElement('div');
      opts.className = 'quiz-options';

      q.options.forEach((opt, oi) => {
        const btn = document.createElement('button');
        btn.className = 'quiz-opt-btn';
        btn.textContent = opt;
        btn.type = 'button';

        if (answers[qi] !== null) {
          btn.disabled = true;
          if (oi === q.correct) btn.classList.add('correct');
          else if (oi === answers[qi]) btn.classList.add('wrong');
        }

        btn.addEventListener('click', () => {
          if (answers[qi] !== null) return;
          answers[qi] = oi;
          render();
          checkComplete();
        });

        opts.appendChild(btn);
      });

      qBlock.appendChild(opts);

      if (answers[qi] !== null) {
        const expl = document.createElement('p');
        expl.className = `quiz-explanation ${answers[qi] === q.correct ? 'expl-correct' : 'expl-wrong'}`;
        expl.textContent = answers[qi] === q.correct
          ? `✓ ${q.explanation}`
          : `✗ ${q.explanation}`;
        qBlock.appendChild(expl);
      }

      container.appendChild(qBlock);
    });
  }

  function checkComplete() {
    if (completed) return;
    const allAnswered = answers.every(a => a !== null);
    if (!allAnswered) return;
    completed = true;

    const correct = answers.filter((a, i) => a === quizData[i].correct).length;
    const total   = quizData.length;
    const perfect = correct === total;

    const results = document.getElementById('quizResults');
    if (results) {
      results.style.display = 'block';
      results.innerHTML = `
        <div class="quiz-score">${perfect ? '🔥' : '📚'} You got <strong>${correct} of ${total}</strong> correct!</div>
        <p class="quiz-verdict">${perfect
          ? "You're ready to become the bank."
          : 'Not bad — review the article and try again, or book a call and we\'ll walk through it together.'
        }</p>
        ${!perfect ? '<a class="primary-btn quiz-cta-btn" href="https://calendly.com/ajdent-tnc/30min" target="_blank" rel="noopener">Book a Free Call →</a>' : ''}
      `;
      const capture = document.getElementById('quizCapture');
      if (capture) capture.style.display = 'block';
    }
  }

  render();
}

/* ── COMMENT FORM ── */
function submitComment(e) {
  e.preventDefault();
  const name    = document.getElementById('commentName')?.value.trim() || 'Anonymous';
  const comment = document.getElementById('commentText')?.value.trim();
  const postUrl = window.location.href;
  if (!comment) return;

  submitToGHL({ name, comment, postUrl, tags: ['blog-comment'] }, GHL_COMMENTS);

  const form = document.getElementById('commentForm');
  const success = document.getElementById('commentSuccess');
  if (form) form.style.display = 'none';
  if (success) success.style.display = 'block';
}

/* ── COOKIE CONSENT ── */
function initCookies() {
  const consent = localStorage.getItem(COOKIE_KEY);
  if (!consent) {
    setTimeout(() => {
      const b = document.getElementById('cookieBanner');
      if (b) b.classList.add('visible');
    }, 700);
  } else if (consent === 'accepted') {
    loadTrackingScripts();
  }
}

function cookieAction(action) {
  localStorage.setItem(COOKIE_KEY, action === 'accept' ? 'accepted' : 'rejected');
  document.cookie = 'cookie_consent=' + (action === 'accept' ? 'accepted' : 'rejected') + '; max-age=31536000; path=/';
  const banner = document.getElementById('cookieBanner');
  const panel  = document.getElementById('cookiePanel');
  if (banner) banner.classList.remove('visible');
  if (panel)  panel.classList.remove('open');
  if (action === 'accept') loadTrackingScripts();
}

function openCookiePanel()  { const p = document.getElementById('cookiePanel'); if (p) p.classList.add('open'); }
function closeCookiePanel() { const p = document.getElementById('cookiePanel'); if (p) p.classList.remove('open'); }

function saveCookiePrefs() {
  const prefs = {
    analytics:     document.getElementById('toggleAnalytics')?.checked,
    marketing:     document.getElementById('toggleMarketing')?.checked,
    functionality: document.getElementById('toggleFunctionality')?.checked
  };
  localStorage.setItem(COOKIE_KEY, 'custom');
  localStorage.setItem('tnc_cookie_prefs', JSON.stringify(prefs));
  document.cookie = 'cookie_consent=custom; max-age=31536000; path=/';
  closeCookiePanel();
  const banner = document.getElementById('cookieBanner');
  if (banner) banner.classList.remove('visible');
  if (prefs.analytics || prefs.marketing) loadTrackingScripts(prefs);
}

function loadTrackingScripts(prefs) {
  if (!prefs || prefs.analytics) {
    if (window.__tncAnalyticsLoaded) return;
    window.__tncAnalyticsLoaded = true;
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX';
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag(){ window.dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  }
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
  initCookies();
});
