// TEMP, GUARDED QA verifier — reads a contact's tags by email so wiring can be confirmed. Read-only. Deleted after use.
exports.handler = async (event) => {
  const GUARD = 'qa-6dcea5df5e123f323e31f8a1';
  const q = event.queryStringParameters || {};
  if (q.k !== GUARD) return { statusCode: 404, body: 'Not found' };
  const email = (q.email || '').trim().toLowerCase();
  try {
    const r = await fetch(
      `https://services.leadconnectorhq.com/contacts/?locationId=${encodeURIComponent(process.env.GHL_LOCATION_ID)}&query=${encodeURIComponent(email)}&limit=10`,
      { headers: { Authorization: `Bearer ${process.env.GHL_API_KEY}`, Version: '2021-07-28' } }
    );
    const data = await r.json();
    const list = data.contacts || [];
    const c = list.find(x => (x.email || '').toLowerCase() === email) || null;
    return { statusCode: 200, headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ found: !!c, count: list.length, id: c && c.id, email: c && c.email, tags: c ? (c.tags || []) : [] }) };
  } catch (e) {
    return { statusCode: 200, body: JSON.stringify({ error: String(e) }) };
  }
};
