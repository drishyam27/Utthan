import { getDistrictById, getStateById } from '../data/locations.js';
import { LANGUAGES } from '../data/languages.js';

const EDUCATION_LABELS = {
  no_formal: 'No formal schooling',
  '8th_pass': '8th Pass or below',
  '10th_pass': '10th Pass',
  '12th_pass': '12th Pass',
  iti_vocational: 'ITI / Vocational Diploma',
  graduate: 'Graduate',
};

const MOBILITY_LABELS = {
  village_block: 'Within village / block',
  within_15km: 'Within 15 km of home block',
  district_wide: 'Across the district',
  relocate_hostel: 'Relocate for training with hostel',
};

const EDUCATION_ALIASES = {
  'no formal schooling': 'no_formal',
  '8th pass or below': '8th_pass',
  '8th pass': '8th_pass',
  '10th pass': '10th_pass',
  '12th pass': '12th_pass',
  'iti / vocational diploma': 'iti_vocational',
  'iti/vocational diploma': 'iti_vocational',
  graduate: 'graduate',
};

const MOBILITY_ALIASES = {
  'within village / block': 'village_block',
  'within 15 km of home block': 'within_15km',
  'across the district': 'district_wide',
  'relocate for training with hostel': 'relocate_hostel',
};

export const EMPTY_USER_PROFILE = {
  fullName: '',
  preferredLanguage: 'English',
  education: 'Not provided',
  currentWork: 'Not provided',
  skills: [],
  interests: [],
  location: 'Location not detected',
  mobilityPreference: 'Not provided',
  availability: 'Not collected yet',
  phone: '',
  aadhaarStatus: 'Not collected',
};

export function toResolvedLocation(beneficiary) {
  const state = getStateById(beneficiary?.state_id);
  const district = getDistrictById(beneficiary?.district_id);
  if (!state || !district || district.stateId !== state.id) return null;
  return { state, district };
}

export function toUserProfile(beneficiary) {
  const location = toResolvedLocation(beneficiary);
  const language = LANGUAGES.find(item => item.id === beneficiary?.preferred_language);

  return {
    ...EMPTY_USER_PROFILE,
    fullName: beneficiary?.name || '',
    preferredLanguage: language?.name || beneficiary?.preferred_language || 'English',
    education: EDUCATION_LABELS[beneficiary?.education_level] || 'Not provided',
    currentWork: beneficiary?.current_occupation || 'Not provided',
    location: location ? `${location.district.name}, ${location.state.name}` : 'Location not detected',
    mobilityPreference: MOBILITY_LABELS[beneficiary?.mobility_preference] || 'Not provided',
  };
}

export function toCreatePayload({ name, languageId, resolvedLocation }) {
  const stateId = resolvedLocation?.state?.id;
  const districtId = resolvedLocation?.district?.id;
  if (!name?.trim() || !languageId || !stateId || !districtId) return null;

  return {
    name: name.trim(),
    preferred_language: languageId,
    state_id: stateId,
    district_id: districtId,
  };
}

function normalizeAlias(value, aliases) {
  if (!value || typeof value !== 'string') return null;
  const normalized = value.trim().toLowerCase();
  return aliases[normalized] || normalized;
}

export function toUpdatePayload(profile, languageId) {
  const payload = {};
  if (profile?.fullName?.trim()) payload.name = profile.fullName.trim();
  if (languageId) payload.preferred_language = languageId;

  if (profile?.currentWork && profile.currentWork !== 'Not provided') {
    payload.current_occupation = profile.currentWork.trim();
  }

  const education = normalizeAlias(profile?.education, EDUCATION_ALIASES);
  if (education && Object.prototype.hasOwnProperty.call(EDUCATION_LABELS, education)) {
    payload.education_level = education;
  }

  const mobility = normalizeAlias(profile?.mobilityPreference, MOBILITY_ALIASES);
  if (mobility && Object.prototype.hasOwnProperty.call(MOBILITY_LABELS, mobility)) {
    payload.mobility_preference = mobility;
  }

  return payload;
}
