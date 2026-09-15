import { getDistrictById, getStateById } from '../data/locations';

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

export function mapOpportunity(opportunity = {}) {
  const skills = Array.isArray(opportunity.skills) ? opportunity.skills : [];

  return {
    ...opportunity,
    partner: opportunity.provider,
    sourceUrl: opportunity.source_url,
    location: locationLabel(opportunity),
    avgEarnings: opportunity.expected_earnings || null,
    overview: opportunity.overview || null,
    eligibility: eligibilityLabels(opportunity),
    skillsPossessed: [],
    skillsMissing: skills.filter((skill) => skill.is_primary !== false).map((skill) => skill.name),
    actionSteps: Array.isArray(opportunity.action_steps) ? opportunity.action_steps : [],
    matchScore: typeof opportunity.match_score === 'number' ? opportunity.match_score : null,
    whyMatches: opportunity.why_matches || null,
  };
}
