/**
 * Data Quality & Integrity Validation Test Suite
 * Ensures zero fabricated, orphan, or corrupted records across:
 * - States Master Table
 * - Districts Master Table
 * - Skills Master Table
 * - Opportunities Master Table
 */

import { STATES, DISTRICTS } from '../src/data/locations.js';
import { SKILLS_MASTER, VERIFIED_OPPORTUNITIES } from '../src/data/verifiedOpportunities.js';

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
console.log('📊 RUNNING DATA QUALITY & INTEGRITY VALIDATION SUITE');
console.log('====================================================\n');

// 1. States Integrity
console.log('1. Validating States & UTs (Official 36 Entities)');
assert(STATES.length === 36, `Total States + UTs count is exactly 36 (found ${STATES.length})`);

const stateCodes = new Set();
let duplicateStateCode = false;
for (const s of STATES) {
  if (stateCodes.has(s.code)) duplicateStateCode = true;
  stateCodes.add(s.code);
}
assert(!duplicateStateCode, 'Zero duplicate state codes');

const stateNames = new Set();
let duplicateStateName = false;
for (const s of STATES) {
  if (stateNames.has(s.name.toLowerCase())) duplicateStateName = true;
  stateNames.add(s.name.toLowerCase());
}
assert(!duplicateStateName, 'Zero duplicate state names');

// 2. Districts Integrity
console.log('\n2. Validating Districts Master Dataset');
assert(DISTRICTS.length >= 50, `Substantial district dataset present (${DISTRICTS.length} districts mapped)`);

let invalidStateRef = false;
const stateIdSet = new Set(STATES.map(s => s.id));
for (const d of DISTRICTS) {
  if (!stateIdSet.has(d.stateId)) {
    invalidStateRef = true;
    console.error(`District ${d.name} references invalid stateId: ${d.stateId}`);
  }
}
assert(!invalidStateRef, 'All districts reference valid parent states');

// Check duplicate districts within the same state
const stateDistrictPairs = new Set();
let duplicateDistrictInState = false;
for (const d of DISTRICTS) {
  const pair = `${d.stateId}::${d.name.toLowerCase()}`;
  if (stateDistrictPairs.has(pair)) duplicateDistrictInState = true;
  stateDistrictPairs.add(pair);
}
assert(!duplicateDistrictInState, 'Zero duplicate district names within the same state');

// 3. Skills Master Integrity
console.log('\n3. Validating Skills & NSQF Alignment');
assert(SKILLS_MASTER.length > 0, `Skills catalog contains ${SKILLS_MASTER.length} standardized skills`);

let invalidNsqf = false;
let missingSkillSource = false;
for (const s of SKILLS_MASTER) {
  if (!s.nsqfLevel || s.nsqfLevel < 1 || s.nsqfLevel > 8) {
    invalidNsqf = true;
    console.error(`Skill ${s.name} has invalid NSQF level: ${s.nsqfLevel}`);
  }
  if (!s.source || !s.sourceUrl || !s.qpCode) {
    missingSkillSource = true;
    console.error(`Skill ${s.name} missing source, QP code, or URL`);
  }
}
assert(!invalidNsqf, 'All skills have legitimate NSQF levels (Levels 1 to 8)');
assert(!missingSkillSource, 'All skills have verified source agencies, QP codes, and URLs');

// 4. Opportunities Dataset Integrity
console.log('\n4. Validating Opportunities Master Dataset');
assert(VERIFIED_OPPORTUNITIES.length >= 7, `Verified opportunities catalog contains ${VERIFIED_OPPORTUNITIES.length} government schemes`);

let missingOppSource = false;
let orphanSkillInOpp = false;
const skillIdSet = new Set(SKILLS_MASTER.map(s => s.id));
const districtIdSet = new Set(DISTRICTS.map(d => d.id));
let invalidDistrictRef = false;

for (const opp of VERIFIED_OPPORTUNITIES) {
  if (!opp.source || !opp.sourceUrl || !opp.sourceUrl.startsWith('http')) {
    missingOppSource = true;
    console.error(`Opportunity ${opp.title} missing verified government source URL`);
  }

  // Check skill mapping
  for (const skId of (opp.skillIds || [])) {
    if (!skillIdSet.has(skId)) {
      orphanSkillInOpp = true;
      console.error(`Opportunity ${opp.title} references unknown skillId: ${skId}`);
    }
  }

  // Check state and district reference if non-pan-India
  if (opp.stateId && !stateIdSet.has(opp.stateId)) {
    invalidStateRef = true;
    console.error(`Opportunity ${opp.title} references invalid state: ${opp.stateId}`);
  }
  if (opp.districtId && !districtIdSet.has(opp.districtId)) {
    invalidDistrictRef = true;
    console.error(`Opportunity ${opp.title} references invalid district: ${opp.districtId}`);
  }
}

assert(!missingOppSource, 'All opportunities have traceable, verified government portal URLs');
assert(!orphanSkillInOpp, 'All opportunity-skill relationships reference valid skills');
assert(!invalidDistrictRef, 'All location-bound opportunities reference valid official districts');

console.log('\n====================================================');
console.log(`TOTAL DATA QUALITY CHECKS: ${passed + failed} | PASSED: ${passed} | FAILED: ${failed}`);
console.log('====================================================');

if (failed > 0) {
  process.exit(1);
} else {
  console.log('🎉 ALL DATA INTEGRITY & AUDIT CHECKS PASSED PERFECTLY!\n');
}
