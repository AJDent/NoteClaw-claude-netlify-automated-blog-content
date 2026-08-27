// Relay: GHL workflow Webhook ("Fire a webhook containing the contact's details")
// -> reformat into Discord's payload shape -> POST to the #new-lead channel webhook.
// GHL's webhook body is fixed (contact fields), which Discord rejects; this bridges the format.
// Wire in GHL WF5: trigger tag `lead-magnet-download` -> Webhook (POST this function URL) -> END.
// Secret lives ONLY in the Netlify env var DISCORD_WEBHOOK_NEW_LEAD (never hardcoded).

const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_NEW_LEAD;
const NOTIFY_SECRET   = process.env.NOTIFY_SECRET; // optional shared secret (see header check below)

const TNC_BLUE = 0x5ba4e6; // brand accent

// which lead magnet the contact grabbed, read off the tags GHL sends
const MAGNET_MAP = {
  'lead-magnet-ira':        'IRA / SDIRA + 401(k) Guide',
  'lead-magnet-7ways':      '7 Ways to Earn Passive Income',
  'lead-magnet-compare':    'Note Investing vs Rentals',
  'lead-magnet-tapefilter': '60-Second Tape Filter'
};

// which funnel / avatar they came through
const FUNNEL_MAP = {
  'landing-sdira':   'SDIRA landing page',
  'landing-401k':    '401(k) landing page',
  'landing-private': 'Private-investor landing page',
  'avatar-sdira':    'SDIRA avatar',
  'avatar-401k':     '401(k) avatar',
  'avatar-private':  'Private-capital avatar',
  'avatar-learning': 'Just-learning avatar',
  'buybox-submission': 'Note-buyer buy box'
};

function toTagList(tags) {
  if (Array.isArray(tags)) return tags.map(t => String(t).trim()).filter(Boolean);
  if (typeof tags === 'string') return tags.split(',').map(t => t.trim()).filter(Boolean);
  return [];
}

function firstMatch(tags, map) {
  for (const t of tags) if (map[t]) return map[t];
  return '';
}

function buildDiscordPayload(data) {
  const tags = toTagList(data.tags);
  const name = (data.full_name || `${data.first_name || ''} ${data.last_name || ''}`).trim() || 'Unknown';
  const email = data.email || '—';
  const phone = data.phone || '—';
  const magnet = firstMatch(tags, MAGNET_MAP) || 'Lead magnet';
  const funnel = firstMatch(tags, FUNNEL_MAP) || '—';
  const tagStr = tags.length ? tags.join(', ') : '—';

  return {
    username: 'TNC New Lead',
    embeds: [{
      title: `🎯 New lead — ${magnet}`,
      color: TNC_BLUE,
      fields: [
        { name: 'Name',   value: name,   inline: true },
        { name: 'Email',  value: email,  inline: true },
        { name: 'Phone',  value: phone,  inline: true },
        { name: 'Funnel', value: funnel, inline: false },
        { name: 'Tags',   value: tagStr.slice(0, 1000), inline: false }
      ],
      footer: { text: 'Take Notes Capital' },
      timestamp: new Date().toISOString()
    }]
  };
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  if (!DISCORD_WEBHOOK) return { statusCode: 500, body: JSON.stringify({ error: 'DISCORD_WEBHOOK_NEW_LEAD not set' }) };

  // Optional hardening: if NOTIFY_SECRET is set, require GHL to send a matching x-tnc-secret header.
  if (NOTIFY_SECRET) {
    const got = event.headers['x-tnc-secret'] || event.headers['X-Tnc-Secret'];
    if (got !== NOTIFY_SECRET) return { statusCode: 401, body: JSON.stringify({ error: 'unauthorized' }) };
  }

  let data;
  try { data = JSON.parse(event.body || '{}'); }
  catch { return { statusCode: 400, body: JSON.stringify({ error: 'bad json' }) }; }

  try {
    const res = await fetch(DISCORD_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildDiscordPayload(data))
    });
    if (res.ok || res.status === 204) return { statusCode: 200, body: JSON.stringify({ success: true }) };
    const txt = await res.text();
    return { statusCode: 502, body: JSON.stringify({ error: 'discord rejected', detail: txt.slice(0, 300) }) };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: 'relay failed' }) };
  }
};
