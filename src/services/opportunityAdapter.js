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
  };
}
