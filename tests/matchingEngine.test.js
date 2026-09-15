/**
 * Automated Tests for Utthan Deterministic Matching Engine
 * 
 * Verifies the 5 Mandatory Core Test Cases:
 * Case 1: Strong Match (eligible = true, high score >= 80)
 * Case 2: Geographic Mismatch (eligible = false, reason explains location)
 * Case 3: Education Mismatch (eligible = false, reason explains education)
 * Case 4: Mobility Mismatch (eligible = false, reason explains travel requirement)
 * Case 5: Partial Match (eligible = true, moderate score)
 */

import { matchOpportunities, checkHardEligibility, calculateMatchScore } from '../src/services/recommendationEngine.js';
import { VERIFIED_OPPORTUNITIES } from '../src/data/verifiedOpportunities.js';

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  ✓ PASS: ${message}`);
    passed++;
  } else {
    console.error(`  ✗ FAIL: ${message}`);
    failed++;
  }
}

console.log('====================================================');
console.log('🧪 RUNNING MATCHING ENGINE DETERMINISTIC TEST SUITE');
console.log('====================================================\n');

// ----------------------------------------------------------------------------
// TEST CASE 1: Strong Match
// Beneficiary is 10th pass, wants solar electrical maintenance, travels up to 15km
// ----------------------------------------------------------------------------
console.log('Test Case 1: Strong Match Scenario (Solar Rooftop Technician)');
const beneficiaryStrong = {
  name: 'Soham Das',
  trade: 'solar and electrical maintenance',
  education: '10th Pass',
  mobility: 'Up to 15 km (Nearby Market / Town)',
  goal: 'Certified Training + Monthly Stipend',
  stateId: 'state-up',
  districtId: 'dist-up-varanasi',
  age: 22
};

const results1 = matchOpportunities(beneficiaryStrong, VERIFIED_OPPORTUNITIES);
const topMatch1 = results1[0];

assert(topMatch1.opportunity.id === 'opp-solar-rooftop', 'Top recommended scheme is Solar Rooftop Technician');
assert(topMatch1.eligible === true, 'Beneficiary is marked eligible');
assert(topMatch1.score >= 85, `Score is high (${topMatch1.score} >= 85)`);
assert(topMatch1.unmetCriteria.length === 0, 'Zero unmet criteria');
assert(topMatch1.reasons.length > 0, 'Provides transparent match explanations');

// ----------------------------------------------------------------------------
// TEST CASE 2: Geographic Mismatch
// Regional opportunity (PM-AJAY Varanasi Handloom) tested against a beneficiary in West Bengal
// ----------------------------------------------------------------------------
console.log('\nTest Case 2: Geographic Mismatch Scenario (Varanasi Regional Scheme vs Kolkata Beneficiary)');
const beneficiaryGeoMismatch = {
  name: 'Anupam Sen',
  trade: 'handloom weaving',
  education: '10th Pass',
  mobility: 'village_block',
  stateId: 'state-wb',
  districtId: 'dist-wb-kolkata',
  age: 28
};

const varanasiOpp = VERIFIED_OPPORTUNITIES.find(o => o.id === 'opp-pm-ajay-handloom-varanasi');
const geoCheck = checkHardEligibility(beneficiaryGeoMismatch, varanasiOpp);

assert(geoCheck.eligible === false, 'Regional scheme correctly marks cross-state applicant ineligible');
assert(geoCheck.unmetCriteria.some(c => c.includes('state-up')), 'Explicit reason identifies required state jurisdiction');

// ----------------------------------------------------------------------------
// TEST CASE 2B: Missing Canonical Location
// Restricted opportunities must never qualify without verified State/District IDs.
// ----------------------------------------------------------------------------
console.log('\nTest Case 2B: Missing Canonical Location Scenario');
const beneficiaryMissingLocation = {
  name: 'Unresolved Citizen',
  trade: 'handloom weaving',
  education: '10th Pass',
  mobility: 'district_wide',
  age: 28
};

const missingLocationCheck = checkHardEligibility(beneficiaryMissingLocation, varanasiOpp);
assert(missingLocationCheck.eligible === false, 'Restricted scheme rejects beneficiary without canonical location');
assert(missingLocationCheck.unmetCriteria.some(c => c.includes('Canonical State and District')), 'Missing-location reason requires canonical State and District IDs');

// ----------------------------------------------------------------------------
// TEST CASE 3: Education Mismatch
// Drone Pilot requires minimum 10th Pass. Beneficiary has no formal schooling.
// ----------------------------------------------------------------------------
console.log('\nTest Case 3: Education Mismatch Scenario (Drone Pilot vs No Formal Schooling)');
const beneficiaryLowEdu = {
  name: 'Ramu',
  trade: 'farming and drone spraying',
  education: 'No formal schooling (Eager to learn)',
  mobility: 'district_wide',
  stateId: 'state-up',
  age: 25
};

const droneOpp = VERIFIED_OPPORTUNITIES.find(o => o.id === 'opp-kisan-drone-pilot');
const eduCheck = checkHardEligibility(beneficiaryLowEdu, droneOpp);

assert(eduCheck.eligible === false, 'Education gatekeeper correctly rejects applicant below 10th pass');
assert(eduCheck.unmetCriteria.some(c => c.includes('10th pass')), 'Explicit reason mentions 10th pass requirement');

// ----------------------------------------------------------------------------
// TEST CASE 4: Mobility Mismatch
// Drone Pilot requires district-wide travel. Beneficiary is only willing to stay within village/block.
// ----------------------------------------------------------------------------
console.log('\nTest Case 4: Mobility Mismatch Scenario (District-Wide Travel vs Village-Only Mobility)');
const beneficiaryLowMobility = {
  name: 'Sunita Devi',
  trade: 'agriculture and drone pilot',
  education: '10th Pass',
  mobility: 'Within my own village / block',
  stateId: 'state-br',
  age: 24
};

const mobCheck = checkHardEligibility(beneficiaryLowMobility, droneOpp);
assert(mobCheck.eligible === false, 'Mobility gatekeeper correctly flags insufficient travel radius');
assert(mobCheck.unmetCriteria.some(c => c.includes('district wide')), 'Explicit reason mentions district wide mobility requirement');

// ----------------------------------------------------------------------------
// TEST CASE 5: Partial Match
// Beneficiary is eligible for Solar, but their goal is self-employment/shop instead of training stipend
// ----------------------------------------------------------------------------
console.log('\nTest Case 5: Partial Match Scenario (Solar Opportunity with Secondary Goal)');
const beneficiaryPartial = {
  name: 'Vikram',
  trade: 'solar maintenance',
  education: '12th Pass',
  mobility: 'Up to 15 km',
  goal: 'Start My Own Micro-Business / Shop',
  age: 30
};

const solarOpp = VERIFIED_OPPORTUNITIES.find(o => o.id === 'opp-solar-rooftop');
const partialCheck = checkHardEligibility(beneficiaryPartial, solarOpp);
const partialScore = calculateMatchScore(beneficiaryPartial, solarOpp);

assert(partialCheck.eligible === true, 'Beneficiary is eligible for the course');
assert(partialScore.score >= 60 && partialScore.score < 95, `Yields moderate match score (${partialScore.score})`);
assert(partialScore.reasons.length > 0, 'Reasons detail trade match and goal adjustment');

console.log('\n====================================================');
console.log(`TOTAL TESTS: ${passed + failed} | PASSED: ${passed} | FAILED: ${failed}`);
console.log('====================================================');

if (failed > 0) {
  process.exit(1);
} else {
  console.log('🎉 ALL 5 MANDATORY MATCHING TESTS PASSED PERFECTLY!\n');
}
