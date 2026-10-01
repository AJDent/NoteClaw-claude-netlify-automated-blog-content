// TEMP diagnostic — verifies GHL env vars are present AND that GHL accepts them.
// Read-only: lists 1 contact (no writes, no test contact created). Returns NO secret values.
// Safe to delete once wiring is confirmed.
exports.handler = async () => {
  const hasKey = !!process.env.GHL_API_KEY;
  const hasLoc = !!process.env.GHL_LOCATION_ID;
  let ghlStatus = null, ghlOk = false, note = '';
  if (hasKey && hasLoc) {
    try {
      const r = await fetch(
        `https://services.leadconnectorhq.com/contacts/?locationId=${encodeURIComponent(process.env.GHL_LOCATION_ID)}&limit=1`,
        { headers: { Authorization: `Bearer ${process.env.GHL_API_KEY}`, Version: '2021-07-28' } }
      );
      ghlStatus = r.status;
      ghlOk = r.ok;
      if (r.status === 401) note = 'GHL rejected the API key (invalid or wrong scope).';
      else if (r.status === 404) note = 'GHL could not find that location id.';
      else if (r.ok) note = 'GHL authenticated successfully — key + location are valid.';
    } catch (e) {
      ghlStatus = 'fetch-error';
      note = 'Could not reach GHL.';
    }
  } else {
    note = 'One or both env vars are missing in Netlify.';
  }
  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hasKey, hasLoc, ghlStatus, ghlOk, note })
  };
};
