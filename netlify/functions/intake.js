const GHL_API_KEY = process.env.GHL_API_KEY;
const GHL_LOCATION_ID = process.env.GHL_LOCATION_ID;

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
  '401k':            '401(k) / Solo 401(k)',
  'cash':            'Cash / Savings',
  'entity':          'LLC / Business Entity',
  'not_sure':        'Not sure yet'
};

const INVESTMENT_RANGE_MAP = {
  'under_25k':  'Under $25,000',
  '25k_50k':    '$25,000 - $50,000',
  '50k_100k':   '$50,000 - $100,000',
  '100k_250k':  '$100,000 - $250,000',
  '250k_plus':  '$250,000+'
};

const LIEN_MAP = { 'senior_1st': '1st', 'junior_2nd': '2nd', 'unsecured': 'Other' };

const DECISION_SPEED_MAP = {
  '24_48_hours':    '24-48 hours',
  'within_a_week':  'Within a week',
  'flexible':       'Flexible'
};

const MAX_LTV_MAP = {
  'under_50':      'Under 50%',
  '50_65':         '50-65%',
  '65_75':         '65-75%',
  '75_85':         '75-85%',
  '85_plus':       '85%+',
  'no_preference': 'No Preference'
};

const BUYBOX_INVESTMENT_MAP = {
  'under_5k':   '< $5,000',
  '5k_10k':     '$5,000 - $10,000',
  '10k_25k':    '$10,000 - $25,000',
  '25k_50k':    '$25,000 - $50,000',
  '50k_100k':   '$50,000 - $100,000',
  '100k_250k':  '$100,000 - $250,000',
  '250k_500k':  '$250,000 - $500,000',
  'over_500k':  '> $500,000'
};

async function createGHLContact(payload) {
  return fetch('https://services.leadconnectorhq.com/contacts/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${GHL_API_KEY}`, 'Version': '2021-07-28', 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

async function handleIntake(data) {
  const ghlPayload = {
    firstName: data.first_name || '', lastName: data.last_name || '',
    email: data.email || '', phone: data.phone || '',
    source: 'Website', tags: ['website-intake'], locationId: GHL_LOCATION_ID,
    customFields: [
      { id: FIELD_IDS.contact_type,     field_value: 'Investor' },
      { id: FIELD_IDS.lead_temperature, field_value: 'Warm' },
      { id: FIELD_IDS.contact_source,   field_value: 'Website' }
    ]
  };
  if (data.investing_with) {
    ghlPayload.customFields.push({ id: FIELD_IDS.investing_with, field_value: INVESTING_WITH_MAP[data.investing_with] || data.investing_with });
  }
  if (data.investment_range) {
    ghlPayload.customFields.push({ id: FIELD_IDS.investment_range, field_value: INVESTMENT_RANGE_MAP[data.investment_range] || data.investment_range });
  }
  if (data.message) {
    ghlPayload.customFields.push({ id: FIELD_IDS.deal_notes, field_value: data.message });
  }
  return createGHLContact(ghlPayload);
}

async function handleBuyBox(data) {
  const assets = data.asset_types || [];
  let noteType = '';
  if (assets.includes('performing') && assets.includes('non_performing')) noteType = 'Both';
  else if (assets.includes('performing')) noteType = 'Performing';
  else if (assets.includes('non_performing')) noteType = 'NPN';

  const liens = data.lien_positions || [];
  let lienValue = liens.length >= 1 ? (LIEN_MAP[liens[0]] || liens[0]) : '';

  const states = data.target_states || [];
  const isNationwide = states.includes('nationwide');
  let targetStateValue = '';
  if (isNationwide) targetStateValue = 'Other';
  else if (states.length === 1) targetStateValue = states[0];
  else if (states.length > 0) targetStateValue = 'Other';

  const investAmt = data.investment_amount || '';
  const investValue = BUYBOX_INVESTMENT_MAP[investAmt] || '';

  let bbParts = ['--- NOTE BUYER BUY BOX ---'];
  if (assets.length) bbParts.push('Asset Types: ' + assets.map(a => a === 'non_performing' ? 'Non-Performing' : 'Performing').join(', '));
  if (liens.length) bbParts.push('Lien Positions: ' + liens.map(l => l === 'senior_1st' ? 'Senior (1st)' : l === 'junior_2nd' ? 'Junior (2nd)' : 'Unsecured').join(', '));
  if (isNationwide) bbParts.push('Target States: NATIONWIDE');
  else if (states.length) bbParts.push('Target States: ' + states.join(', '));
  if (investValue) bbParts.push('Investment Per Deal: ' + investValue);
  const decisionSpeedValue = DECISION_SPEED_MAP[data.decision_speed] || '';
  const maxLtvValue = MAX_LTV_MAP[data.max_ltv] || '';
  if (decisionSpeedValue) bbParts.push('Decision Speed: ' + decisionSpeedValue);
  if (maxLtvValue) bbParts.push('Max LTV: ' + maxLtvValue);
  if (data.preferences) bbParts.push('Additional Preferences: ' + data.preferences);

  const ghlPayload = {
    firstName: data.first_name || '', lastName: data.last_name || '',
    email: data.email || '', phone: data.phone || '',
    source: 'Website', tags: ['buybox-submission', 'note-buyer'], locationId: GHL_LOCATION_ID,
    customFields: [
      { id: FIELD_IDS.contact_type,     field_value: 'Buyer' },
      { id: FIELD_IDS.lead_temperature, field_value: 'Hot' },
      { id: FIELD_IDS.contact_source,   field_value: 'Website' },
      { id: FIELD_IDS.buy_box_details,  field_value: bbParts.join('\n') }
    ]
  };
  if (noteType)         ghlPayload.customFields.push({ id: FIELD_IDS.note_type_interest, field_value: noteType });
  if (lienValue)        ghlPayload.customFields.push({ id: FIELD_IDS.lien_position,      field_value: lienValue });
  if (targetStateValue) ghlPayload.customFields.push({ id: FIELD_IDS.target_state,       field_value: targetStateValue });
  if (investValue)      ghlPayload.customFields.push({ id: FIELD_IDS.investment_range,   field_value: investValue });
  if (data.preferences) ghlPayload.customFields.push({ id: FIELD_IDS.deal_notes,         field_value: data.preferences });
  if (decisionSpeedValue) ghlPayload.customFields.push({ id: FIELD_IDS.decision_speed,   field_value: decisionSpeedValue });
  if (maxLtvValue)        ghlPayload.customFields.push({ id: FIELD_IDS.max_ltv,           field_value: maxLtvValue });
  return createGHLContact(ghlPayload);
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  try {
    const data = JSON.parse(event.body);
    const response = (data._form === 'buybox') ? await handleBuyBox(data) : await handleIntake(data);
    if (response.ok) {
      const result = await response.json();
      return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ success: true, contactId: result.contact?.id }) };
    } else {
      const errorText = await response.text();
      return { statusCode: response.status, body: JSON.stringify({ error: errorText }) };
    }
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: 'Internal server error' }) };
  }
};
