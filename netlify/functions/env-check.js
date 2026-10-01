// TEMP, GUARDED diagnostic — re-verify GHL key after env-var change.
// Requires ?k=<guard>; returns 404 otherwise (not a public oracle). No secret values. Read-only. Deleted after use.
exports.handler = async (event) => {
  const GUARD = 'tncv-64c33df9d81ddd9706c971df';
  const k = (event.queryStringParameters || {}).k || '';
  if (k !== GUARD) return { statusCode: 404, body: 'Not found' };
  const hasKey = !!process.env.GHL_API_KEY;
  const hasLoc = !!process.env.GHL_LOCATION_ID;
  let ghlStatus = null, ghlOk = false, note = '';
  if (hasKey && hasLoc) {
    try {
      const r = await fetch(
        `https://services.leadconnectorhq.com/contacts/?locationId=${encodeURIComponent(process.env.GHL_LOCATION_ID)}&limit=1`,
        { headers: { Authorization: `Bearer ${process.env.GHL_API_KEY}`, Version: '2021-07-28' } }
      );
      ghlStatus = r.status; ghlOk = r.ok;
      note = r.ok ? 'GHL authenticated — key + location valid.'
           : r.status === 401 ? 'GHL rejected the key (invalid or wrong scope).'
           : r.status === 404 ? 'GHL could not find that location id.'
           : 'GHL returned ' + r.status;
    } catch (e) { ghlStatus = 'fetch-error'; note = 'Could not reach GHL.'; }
  } else { note = 'env var missing in Netlify.'; }
  return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ hasKey, hasLoc, ghlStatus, ghlOk, note }) };
};
