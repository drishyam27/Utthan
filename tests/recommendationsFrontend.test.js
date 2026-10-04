import assert from 'node:assert/strict';
import { mapOpportunity } from '../src/services/opportunityAdapter.js';

// Test 1: mapOpportunity preserves backend recommendation score, reasons, and criteria
const rawCatalogOpp = {
  id: 'opp-solar-rooftop',
  title: 'PM Surya Ghar: Rooftop Solar Technician',
  category: 'Green Energy',
  provider: 'Ministry of New & Renewable Energy',
  source_url: 'https://pmsuryaghar.gov.in',
  state_id: null,
  district_id: null,
  education_min: '10th_pass',
  mobility_requirement: 'within_15km',
  stipend: 'Free Training + Certificate',
  expected_earnings: 'Rs 18,000/mo',
  duration: '3 months',
};

const recommendationItem = {
  opportunity_id: 'opp-solar-rooftop',
  title: 'PM Surya Ghar: Rooftop Solar Technician',
  eligible: true,
  score: 95,
  matched_criteria: ['Pan-India eligibility applies', 'Meets education qualification threshold'],
  unmet_criteria: [],
  reasons: ['Direct alignment with your selected craft interest', 'Convenient distance matching travel preference'],
  nsqf_level: 4,
  qp_code: 'SGJ/Q0101',
};

const mapped = mapOpportunity(rawCatalogOpp, {
  matchScore: recommendationItem.score,
  matchedCriteria: recommendationItem.matched_criteria,
  unmetCriteria: recommendationItem.unmet_criteria,
  reasons: recommendationItem.reasons,
  whyMatches: recommendationItem.reasons[0],
  eligible: true,
});

assert.equal(mapped.id, 'opp-solar-rooftop');
assert.equal(mapped.matchScore, 95);
assert.equal(mapped.eligible, true);
assert.equal(mapped.whyMatches, 'Direct alignment with your selected craft interest');
assert.equal(mapped.matchedCriteria.length, 2);
assert.equal(mapped.unmetCriteria.length, 0);

// Test 2: Ineligible opportunity preserves unmet criteria reasons
const rawHandloomOpp = {
  id: 'opp-pm-ajay-handloom-varanasi',
  title: 'PM-AJAY GIA: Handloom Cluster Development',
  category: 'Traditional Craft',
  provider: 'Ministry of Social Justice',
  state_id: 'state-up',
  district_id: 'dist-up-varanasi',
};

const ineligibleRecommendationItem = {
  opportunity_id: 'opp-pm-ajay-handloom-varanasi',
  title: 'PM-AJAY GIA: Handloom Cluster Development',
  eligible: false,
  score: 0,
  matched_criteria: [],
  unmet_criteria: ['Location restricted to state: state-up'],
  reasons: ['Location restricted to state: state-up'],
};

const mappedIneligible = mapOpportunity(rawHandloomOpp, {
  matchScore: 0,
  matchedCriteria: ineligibleRecommendationItem.matched_criteria,
  unmetCriteria: ineligibleRecommendationItem.unmet_criteria,
  reasons: ineligibleRecommendationItem.reasons,
  whyMatches: ineligibleRecommendationItem.unmet_criteria[0],
  eligible: false,
});

assert.equal(mappedIneligible.id, 'opp-pm-ajay-handloom-varanasi');
assert.equal(mappedIneligible.matchScore, 0);
assert.equal(mappedIneligible.eligible, false);
assert.equal(mappedIneligible.unmetCriteria.length, 1);
assert.equal(mappedIneligible.unmetCriteria[0], 'Location restricted to state: state-up');

console.log('✓ recommendation frontend integration adapter tests passed');
