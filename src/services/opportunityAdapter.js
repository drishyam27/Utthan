import { getDistrictById, getStateById } from '../data/locations.js';

function locationLabel(opportunity) {
  const district = getDistrictById(opportunity.district_id);
  if (district) {
    const state = getStateById(district.stateId);
    return state ? `${district.name}, ${state.name}` : district.name;
  }

  const state = getStateById(opportunity.state_id);
  return state?.name || (opportunity.state_id ? opportunity.state_id : 'Pan-India');
}

function eligibilityLabels(opportunity) {
  const rules = opportunity.eligibility_rules || {};
  const requirements = [];

  if (opportunity.age_min != null) {
    requirements.push(`Minimum age ${opportunity.age_min} years`);
  }
  if (opportunity.age_max != null) {
    requirements.push(`Maximum age ${opportunity.age_max} years`);
  }
  if (opportunity.education_min) {
    requirements.push(`Minimum education: ${opportunity.education_min.replaceAll('_', ' ')}`);
  }
  if (opportunity.mobility_requirement) {
    requirements.push(`Travel requirement: ${opportunity.mobility_requirement.replaceAll('_', ' ')}`);
  }
  if (rules.panIndia === false && opportunity.district_id) {
    requirements.push(`District-specific opportunity: ${locationLabel(opportunity)}`);
  }

  return requirements;
}

export function mapOpportunity(opportunity = {}, overrides = {}) {
  const skills = Array.isArray(opportunity.skills) ? opportunity.skills : [];
  const scoreVal = overrides.matchScore ?? (typeof opportunity.score === 'number' ? opportunity.score : (typeof opportunity.match_score === 'number' ? opportunity.match_score : (typeof opportunity.matchScore === 'number' ? opportunity.matchScore : null)));
  const reasonsList = overrides.reasons ?? (Array.isArray(opportunity.reasons) ? opportunity.reasons : []);
  const whyMatchesText = overrides.whyMatches ?? (opportunity.why_matches || opportunity.whyMatches || (reasonsList.length > 0 ? reasonsList[0] : null));

  return {
    ...opportunity,
    partner: opportunity.provider || opportunity.partner,
    sourceUrl: opportunity.source_url || opportunity.sourceUrl,
    location: locationLabel(opportunity),
    avgEarnings: opportunity.expected_earnings || opportunity.avgEarnings || null,
    overview: opportunity.overview || null,
    eligibility: eligibilityLabels(opportunity),
    skillsPossessed: [],
    skillsMissing: skills.filter((skill) => skill.is_primary !== false).map((skill) => skill.name),
    actionSteps: Array.isArray(opportunity.action_steps) ? opportunity.action_steps : (Array.isArray(opportunity.actionSteps) ? opportunity.actionSteps : []),
    matchScore: scoreVal,
    whyMatches: whyMatchesText,
    matchedCriteria: overrides.matchedCriteria ?? (Array.isArray(opportunity.matched_criteria) ? opportunity.matched_criteria : (Array.isArray(opportunity.matchedCriteria) ? opportunity.matchedCriteria : [])),
    unmetCriteria: overrides.unmetCriteria ?? (Array.isArray(opportunity.unmet_criteria) ? opportunity.unmet_criteria : (Array.isArray(opportunity.unmetCriteria) ? opportunity.unmetCriteria : [])),
    reasons: reasonsList,
    eligible: overrides.eligible ?? (typeof opportunity.eligible === 'boolean' ? opportunity.eligible : true),
    itemType: 'opportunity',
  };
}

export function mapNSQFQualification(rec = {}) {
  const eligibility = rec.eligibility || {};
  const matched = eligibility.matched_requirements || [];
  const hardFailures = eligibility.hard_failures || [];
  const reasonsList = rec.match_reasons || [];

  return {
    id: rec.q_code || `nsqf-${Math.random()}`,
    q_code: rec.q_code,
    title: rec.title,
    category: rec.sector_name || 'General',
    sector_id: rec.sector_id,
    sector_name: rec.sector_name,
    partner: rec.awarding_body || 'National Skill Development Agency',
    nsqf_level: rec.nsqf_level,
    qualification_type: rec.qualification_type || 'NSQF National Qualification',
    notional_hours_range: rec.notional_hours_range,
    min_notional_hours: rec.min_notional_hours,
    max_notional_hours: rec.max_notional_hours,
    duration: rec.notional_hours_range ? `${rec.notional_hours_range} Hours` : null,
    is_pwd: Boolean(rec.is_pwd),
    pwd_categories: Array.isArray(rec.pwd_categories) ? rec.pwd_categories : [],
    proposed_occupation: rec.proposed_occupation,
    progression_pathway: rec.progression_pathway,
    overview: rec.description || rec.proposed_occupation || null,
    location: 'National NSQF/NQR Standard (All Certified Centers)',
    matchScore: typeof rec.score === 'number' ? rec.score : null,
    rank: rec.rank || 1,
    whyMatches: reasonsList.length > 0 ? reasonsList[0] : null,
    reasons: reasonsList,
    matchedCriteria: matched,
    unmetCriteria: hardFailures,
    warnings: rec.warnings || [],
    eligible: eligibility.eligible ?? true,
    source: 'nsqf_nqr_catalog',
    itemType: 'qualification',
  };
}

