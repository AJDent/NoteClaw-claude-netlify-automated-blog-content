const GHL_API_KEY = process.env.GHL_API_KEY;
const GHL_LOCATION_ID = process.env.GHL_LOCATION_ID;
const GHL_BASE = 'https://services.leadconnectorhq.com';
const GHL_HEADERS = { 'Authorization': `Bearer ${GHL_API_KEY}`, 'Version': '2021-07-28', 'Content-Type': 'application/json' };
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

const FIELD_IDS = {
  contact_type:       'jB52kzxVk10zf09kUyX9',
  lead_temperature:   'xszwORAnf61TW0jGglcn',
  contact_source:     'wYiZOaLTxrerDcdlMmwJ',
  deal_notes:         'DA2MGqSCIFWzl83Dzpxq',
  buy_box_details:    '2aEsqFqKcO9mCcReYnXb',
  investing_with:     'XTxJdQMa4TmqBO4bngvv',
  investment_range:   'MZFeCmH9CESDS1NqJZX3',
  note_type_interest: 'BReVlQeBPBGyIemAYyD8',
  lien_position:      'WmIwBeFqDCtgVVIk49Qb',
  target_state:       '5AtOBCG5D48tPMPVqDAV',
  decision_speed:     'lGuYsUdaLx1gSV4Rsxwl',
  max_ltv:            'loRbnFa67biv3fxegt4i'
};

const INVESTING_WITH_MAP = {
  'sdira':           'Self-Directed IRA (SDIRA)',
  'traditional_ira': 'Traditional IRA',
  'roth_ira':        'Roth IRA',
  '401k':            '401(k) / Solo 401(k)',
  'cash':            'Cash / Savings',
  'entity':          'LLC / Business Entity',
  'not_sure':        'Not sure yet'
};
const INVESTMENT_RANGE_MAP = {
  'under_25k':  'Under $25,000', '25k_50k': '$25,000 - $50,000', '50k_100k': '$50,000 - $100,000',
  '100k_250k':  '$100,000 - $250,000', '250k_plus': '$250,000+'
};
const LIEN_MAP = { 'senior_1st': '1st', 'junior_2nd': '2nd', 'unsecured': 'Other' };
const DECISION_SPEED_MAP = { '24_48_hours': '24-48 hours', 'within_a_week': 'Within a week', 'flexible': 'Flexible' };
const MAX_LTV_MAP = { 'under_50':'Under 50%', '50_65':'50-65%', '65_75':'65-75%', '75_85':'75-85%', '85_plus':'85%+', 'no_preference':'No Preference' };
const BUYBOX_INVESTMENT_MAP = {
  'under_5k':'< $5,000', '5k_10k':'$5,000 - $10,000', '10k_25k':'$10,000 - $25,000', '25k_50k':'$25,000 - $50,000',
  '50k_100k':'$50,000 - $100,000', '100k_250k':'$100,000 - $250,000', '250k_500k':'$250,000 - $500,000', 'over_500k':'> $500,000'
};
const BLOG_INVESTOR_TYPE_MAP = {
  'Self-Directed IRA Holder':'Self-Directed IRA (SDIRA)', '401(k) / Solo 401(k) Holder':'401(k) / Solo 401(k)',
  'Private Capital / Cash Investor':'Cash / Savings', 'Just Learning About Note Investing':'Not sure yet'
};
const BLOG_AVATAR_TAG = {
  'Self-Directed IRA Holder':'avatar-sdira', '401(k) / Solo 401(k) Holder':'avatar-401k',
  'Private Capital / Cash Investor':'avatar-private', 'Just Learning About Note Investing':'avatar-learning'
};
const LANDING_INVESTING_WITH = { 'sdira':'Self-Directed IRA (SDIRA)', '401k':'401(k) / Solo 401(k)', 'private':'Cash / Savings' };

// Homepage lane (selector/calculator) -> canonical lane tag
const LANE_TAG = { retiree:'lane-retiree', income:'lane-income', operator:'lane-operator' };
// Pitch-video behaviour -> tag (gate / completed / declined only)
const VIDEO_TAG = { gate:'pitch-video-gate-280', completed:'pitch-video-completed', declined:'declined-pitch-video' };

// ---- helpers ----
function laneTags(data){ return (data.lane && LANE_TAG[data.lane]) ? [LANE_TAG[data.lane]] : []; }
function splitName(full){ const parts = String(full||'').trim().split(/\s+/).filter(Boolean); return { first: parts.shift()||'', last: parts.join(' ')||'' }; }
function utmNote(data){
  const p = [];
  ['utm_source','utm_medium','utm_campaign','utm_term','utm_content'].forEach(k => { if (data[k]) p.push(k.replace('utm_','') + '=' + String(data[k]).slice(0,80)); });
  if (data.referrer) p.push('ref=' + String(data.referrer).slice(0,160));
  return p.length ? 'Source: ' + p.join(' · ') : '';
}
function baseFields(contactType, temp, source){
  return [
    { id: FIELD_IDS.contact_type,     field_value: contactType },
    { id: FIELD_IDS.lead_temperature, field_value: temp },
    { id: FIELD_IDS.contact_source,   field_value: source }
  ];
}
// Upsert by email: merges into an existing contact and accumulates tags (one person = one record).
async function upsert(payload){
  return fetch(GHL_BASE + '/contacts/upsert', { method:'POST', headers: GHL_HEADERS, body: JSON.stringify(payload) });
}

// ---- handlers ----
async function handleIntake(data){
  const tags = ['source-website-intake', ...laneTags(data)];
  if (data._src === 'notebuyer') tags.push('note-buyer', 'note-buyer-inquiry');
  const payload = {
    email: data.email, firstName: data.first_name||'', lastName: data.last_name||'', phone: data.phone||'',
    source: 'Website', tags, locationId: GHL_LOCATION_ID, customFields: baseFields('Investor','Warm','Website')
  };
  if (data.investing_with)   payload.customFields.push({ id: FIELD_IDS.investing_with,   field_value: INVESTING_WITH_MAP[data.investing_with] || data.investing_with });
  if (data.investment_range) payload.customFields.push({ id: FIELD_IDS.investment_range, field_value: INVESTMENT_RANGE_MAP[data.investment_range] || data.investment_range });
  const notes = [data.message||'', utmNote(data)].filter(Boolean).join('\n');
  if (notes) payload.customFields.push({ id: FIELD_IDS.deal_notes, field_value: notes });
  return upsert(payload);
}

async function handleCalculator(data){
  const n = (data.first_name || data.last_name) ? { first: data.first_name||'', last: data.last_name||'' } : splitName(data.name);
  const payload = {
    email: data.email, firstName: n.first, lastName: n.last,
    source: 'Calculator', tags: ['source-calculator', ...laneTags(data)], locationId: GHL_LOCATION_ID,
    customFields: baseFields('Investor','Warm','Calculator')
  };
  const notes = utmNote(data); if (notes) payload.customFields.push({ id: FIELD_IDS.deal_notes, field_value: notes });
  return upsert(payload);
}

async function handleNewsletter(data){
  const payload = {
    email: data.email,
    source: 'TNC Newsletter', tags: ['source-newsletter', 'consent-newsletter'], locationId: GHL_LOCATION_ID,
    customFields: baseFields('Investor','Cold','Newsletter')
  };
  return upsert(payload);
}

async function handleVideo(data){
  const tag = VIDEO_TAG[data.event];
  if (!tag) return { ok: true, json: async () => ({ contact: { id: null } }) };
  const temp = (data.event === 'gate' || data.event === 'completed') ? 'Hot' : 'Warm';
  const payload = {
    email: data.email,
    source: 'Pitch Video', tags: ['source-pitch-video', tag, ...laneTags(data)], locationId: GHL_LOCATION_ID,
    customFields: baseFields('Investor', temp, 'Pitch Video')
  };
  return upsert(payload);
}

async function handleBlog(data){
  const email = (data.email || '').trim().toLowerCase();
  if (!email) return { ok: true, json: async () => ({ contact: { id: null } }) }; // stray comment, no junk contact
  const srcTags = Array.isArray(data.source_tags) ? data.source_tags : [];
  const avatarTag = BLOG_AVATAR_TAG[data.investor_type];
  const tags = Array.from(new Set(['source-blog', 'blog-lead', ...srcTags, ...(avatarTag ? [avatarTag] : [])]));
  const payload = {
    email, firstName: data.first_name || '',
    source: 'Blog', tags, locationId: GHL_LOCATION_ID, customFields: baseFields('Investor','Warm','Blog')
  };
  if (data.investor_type) payload.customFields.push({ id: FIELD_IDS.investing_with, field_value: BLOG_INVESTOR_TYPE_MAP[data.investor_type] || data.investor_type });
  return upsert(payload);
}

async function handleLanding(data){
  const page = ['sdira','401k','private'].includes(data.page) ? data.page : 'private';
  const payload = {
    email: data.email, firstName: data.first_name||'', lastName: data.last_name||'', phone: data.phone||'',
    source: `Landing: ${page}`, tags: [`source-landing-${page}`, 'landing-lead'], locationId: GHL_LOCATION_ID,
    customFields: baseFields('Investor','Warm','Landing Page')
  };
  if (LANDING_INVESTING_WITH[page]) payload.customFields.push({ id: FIELD_IDS.investing_with, field_value: LANDING_INVESTING_WITH[page] });
  const notes = [ data.qualifier ? `Landing (${page}) qualifier: ${data.qualifier}` : '', utmNote(data) ].filter(Boolean).join('\n');
  if (notes) payload.customFields.push({ id: FIELD_IDS.deal_notes, field_value: notes });
  return upsert(payload);
}

async function handleBuyBox(data){
  const assets = data.asset_types || [];
  let noteType = '';
  if (assets.includes('performing') && assets.includes('non_performing')) noteType = 'Both';
  else if (assets.includes('performing')) noteType = 'Performing';
  else if (assets.includes('non_performing')) noteType = 'NPN';
  const liens = data.lien_positions || [];
  const lienValue = liens.length ? (LIEN_MAP[liens[0]] || liens[0]) : '';
  const states = data.target_states || [];
  const isNationwide = states.includes('nationwide');
  let targetStateValue = '';
  if (isNationwide) targetStateValue = 'Other';
  else if (states.length === 1) targetStateValue = states[0];
  else if (states.length > 0) targetStateValue = 'Other';
  const investValue = BUYBOX_INVESTMENT_MAP[data.investment_amount || ''] || '';
  const decisionSpeedValue = DECISION_SPEED_MAP[data.decision_speed] || '';
  const maxLtvValue = MAX_LTV_MAP[data.max_ltv] || '';

  const bb = ['--- NOTE BUYER BUY BOX ---'];
  if (assets.length) bb.push('Asset Types: ' + assets.map(a => a === 'non_performing' ? 'Non-Performing' : 'Performing').join(', '));
  if (liens.length)  bb.push('Lien Positions: ' + liens.map(l => l === 'senior_1st' ? 'Senior (1st)' : l === 'junior_2nd' ? 'Junior (2nd)' : 'Unsecured').join(', '));
  if (isNationwide)  bb.push('Target States: NATIONWIDE'); else if (states.length) bb.push('Target States: ' + states.join(', '));
  if (investValue)   bb.push('Investment Per Deal: ' + investValue);
  if (decisionSpeedValue) bb.push('Decision Speed: ' + decisionSpeedValue);
  if (maxLtvValue)   bb.push('Max LTV: ' + maxLtvValue);
  if (data.preferences) bb.push('Additional Preferences: ' + data.preferences);
  const utm = utmNote(data); if (utm) bb.push(utm);

  const payload = {
    email: data.email, firstName: data.first_name||'', lastName: data.last_name||'', phone: data.phone||'',
    source: 'Website', tags: ['source-buybox', 'buybox-submission', 'note-buyer'], locationId: GHL_LOCATION_ID,
    customFields: [ ...baseFields('Buyer','Hot','Website'), { id: FIELD_IDS.buy_box_details, field_value: bb.join('\n') } ]
  };
  if (noteType)           payload.customFields.push({ id: FIELD_IDS.note_type_interest, field_value: noteType });
  if (lienValue)          payload.customFields.push({ id: FIELD_IDS.lien_position,      field_value: lienValue });
  if (targetStateValue)   payload.customFields.push({ id: FIELD_IDS.target_state,       field_value: targetStateValue });
  if (investValue)        payload.customFields.push({ id: FIELD_IDS.investment_range,   field_value: investValue });
  if (data.preferences)   payload.customFields.push({ id: FIELD_IDS.deal_notes,         field_value: data.preferences });
  if (decisionSpeedValue) payload.customFields.push({ id: FIELD_IDS.decision_speed,     field_value: decisionSpeedValue });
  if (maxLtvValue)        payload.customFields.push({ id: FIELD_IDS.max_ltv,            field_value: maxLtvValue });
  return upsert(payload);
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  let data;
  try { data = JSON.parse(event.body); } catch { return { statusCode: 400, body: JSON.stringify({ error: 'Bad request' }) }; }

  // Bot traps: respond 200 so bots get no signal, but do nothing.
  if (data._hp) return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ success: true }) };
  if (typeof data._elapsed === 'number' && data._elapsed >= 0 && data._elapsed < 2000) {
    return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ success: true }) };
  }

  // Email required + valid for every form except blog (which handles its own comment/opt-in split).
  const email = (data.email || '').trim().toLowerCase();
  if (data._form !== 'blog') {
    if (!EMAIL_RE.test(email)) return { statusCode: 400, body: JSON.stringify({ error: 'A valid email is required.' }) };
    data.email = email;
  }

  try {
    let resp;
    switch (data._form) {
      case 'buybox':      resp = await handleBuyBox(data);    break;
      case 'blog':        resp = await handleBlog(data);      break;
      case 'landing':     resp = await handleLanding(data);   break;
      case 'calculator':  resp = await handleCalculator(data);break;
      case 'newsletter':  resp = await handleNewsletter(data);break;
      case 'pitch-video': resp = await handleVideo(data);     break;
      default:            resp = await handleIntake(data);
    }
    if (resp.ok) {
      const result = await resp.json();
      return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ success: true, contactId: result.contact?.id }) };
    } else {
      const errorText = await resp.text();
      return { statusCode: resp.status, body: JSON.stringify({ error: errorText }) };
    }
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: 'Internal server error' }) };
  }
};
