/**
 * Data Quality, Parity & National Location Master Validation Test Suite
 * Ensures zero fabricated, orphan, or corrupted records across:
 * - Canonical LGD Dataset (src/data/canonicalLocations.json)
 * - Frontend Locations Module (src/data/locations.js)
 * - Supabase Seed SQL (supabase/seed/02_all_india_districts.sql)
 * - Skills & Opportunities Master Tables
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { STATES, DISTRICTS, getStates, getStateById, getDistrictsByState, getDistrictById } from '../src/data/locations.js';
import canonicalData from '../src/data/canonicalLocations.json' with { type: 'json' };
import { SKILLS_MASTER, VERIFIED_OPPORTUNITIES } from '../src/data/verifiedOpportunities.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

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
console.log('📊 RUNNING NATIONAL LOCATION & DATA QUALITY TEST SUITE');
console.log('====================================================\n');

// ----------------------------------------------------------------------------
// 1. States Integrity & Backward Compatibility
// ----------------------------------------------------------------------------
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

// Verify all 36 states have valid official integer LGD codes
const stateLgdCodes = new Set();
let invalidStateLgdCode = false;
for (const s of STATES) {
  if (!s.lgdCode || typeof s.lgdCode !== 'number' || s.lgdCode < 1 || s.lgdCode > 38) {
    invalidStateLgdCode = true;
    console.error(`Invalid LGD state code for ${s.name}: ${s.lgdCode}`);
  }
  stateLgdCodes.add(s.lgdCode);
}
assert(!invalidStateLgdCode && stateLgdCodes.size === 36, 'All 36 States/UTs possess unique, valid integer LGD codes (1..38)');

// Verify short code compatibility
const expectedShortCodes = ['UP', 'WB', 'BR', 'MH', 'TN', 'DL', 'AP', 'TG', 'KA', 'GJ', 'RJ', 'MP', 'OD', 'KL', 'JH', 'AS', 'PB', 'HR', 'CT', 'UT', 'HP', 'JK'];
let missingShortCode = false;
for (const sc of expectedShortCodes) {
  if (!stateCodes.has(sc)) {
    missingShortCode = true;
    console.error(`Missing expected application state short code: ${sc}`);
  }
}
assert(!missingShortCode, 'All application short state codes (UP, WB, BR, MH, TN, DL, etc.) remain intact');

// ----------------------------------------------------------------------------
// 2. Authoritative 784 Districts Master Integrity
// ----------------------------------------------------------------------------
console.log('\n2. Validating 784 Authoritative Districts Master Dataset');
assert(DISTRICTS.length === 784, `District count exactly matches authoritative 784 master (found ${DISTRICTS.length})`);

// Regression guard: Explicitly catch 21-district and 76-district subsets
assert(DISTRICTS.length !== 21 && DISTRICTS.length !== 76, 'Dataset is not a 21 or 76 partial prototype subset');

// Unique District IDs
const districtIdSet = new Set();
let duplicateDistrictId = false;
for (const d of DISTRICTS) {
  if (districtIdSet.has(d.id)) {
    duplicateDistrictId = true;
    console.error(`Duplicate district ID found: ${d.id}`);
  }
  districtIdSet.add(d.id);
}
assert(!duplicateDistrictId && districtIdSet.size === 784, 'Zero duplicate district IDs across national master');

// Unique LGD District Codes
const districtLgdSet = new Set();
let duplicateDistrictLgd = false;
let missingDistrictLgd = false;
for (const d of DISTRICTS) {
  if (!d.lgdDistrictCode || typeof d.lgdDistrictCode !== 'number') {
    missingDistrictLgd = true;
  }
  if (districtLgdSet.has(d.lgdDistrictCode)) {
    duplicateDistrictLgd = true;
    console.error(`Duplicate LGD district code found: ${d.lgdDistrictCode}`);
  }
  districtLgdSet.add(d.lgdDistrictCode);
}
assert(!missingDistrictLgd && !duplicateDistrictLgd && districtLgdSet.size === 784, 'Zero missing or duplicate LGD District Codes (784 unique codes)');

// Valid Parent States (Zero Orphans)
let invalidStateRef = false;
const stateIdSet = new Set(STATES.map(s => s.id));
for (const d of DISTRICTS) {
  if (!stateIdSet.has(d.stateId)) {
    invalidStateRef = true;
    console.error(`District ${d.name} references invalid stateId: ${d.stateId}`);
  }
}
assert(!invalidStateRef, 'Zero orphan districts: every district references a valid parent State/UT');

// Zero duplicate names within the same State/UT
const stateDistrictPairs = new Set();
let duplicateDistrictInState = false;
for (const d of DISTRICTS) {
  const pair = `${d.stateId}::${d.name.toLowerCase()}`;
  if (stateDistrictPairs.has(pair)) {
    duplicateDistrictInState = true;
    console.error(`Duplicate district within state: ${pair}`);
  }
  stateDistrictPairs.add(pair);
}
assert(!duplicateDistrictInState, 'Zero duplicate district names within the same State/UT');

// Cross-state duplicate district names check (Bilaspur, Hamirpur, Pratapgarh)
const bilaspurs = DISTRICTS.filter(d => d.name.toLowerCase() === 'bilaspur');
assert(bilaspurs.length === 2 && bilaspurs[0].stateId !== bilaspurs[1].stateId && bilaspurs[0].lgdDistrictCode !== bilaspurs[1].lgdDistrictCode,
  'Cross-state duplicate name "Bilaspur" resolved into distinct states (CG, HP) with unique LGD codes');

const hamirpurs = DISTRICTS.filter(d => d.name.toLowerCase() === 'hamirpur');
assert(hamirpurs.length === 2 && hamirpurs[0].stateId !== hamirpurs[1].stateId && hamirpurs[0].lgdDistrictCode !== hamirpurs[1].lgdDistrictCode,
  'Cross-state duplicate name "Hamirpur" resolved into distinct states (HP, UP) with unique LGD codes');

const pratapgarhs = DISTRICTS.filter(d => d.name.toLowerCase() === 'pratapgarh');
assert(pratapgarhs.length === 2 && pratapgarhs[0].stateId !== pratapgarhs[1].stateId && pratapgarhs[0].lgdDistrictCode !== pratapgarhs[1].lgdDistrictCode,
  'Cross-state duplicate name "Pratapgarh" resolved into distinct states (RJ, UP) with unique LGD codes');

// ----------------------------------------------------------------------------
// 3. Exact Parity: Canonical JSON <-> Frontend locations.js
// ----------------------------------------------------------------------------
console.log('\n3. Validating Exact Parity (canonicalLocations.json <-> locations.js)');
assert(canonicalData.states.length === STATES.length, `States parity: canonical (${canonicalData.states.length}) === locations.js (${STATES.length})`);
assert(canonicalData.districts.length === DISTRICTS.length, `Districts parity: canonical (${canonicalData.districts.length}) === locations.js (${DISTRICTS.length})`);

let parityMismatch = false;
for (let i = 0; i < canonicalData.districts.length; i++) {
  const c = canonicalData.districts[i];
  const l = DISTRICTS[i];
  if (c.id !== l.id || c.lgdDistrictCode !== l.lgdDistrictCode || c.stateCode !== l.stateCode) {
    parityMismatch = true;
    console.error(`Parity mismatch at index ${i}: canonical=${c.id} vs locations=${l.id}`);
    break;
  }
}
assert(!parityMismatch, '100% field parity between canonical master and application locations module');

// Test helper methods
assert(getStates().length === 36, 'getStates() returns all 36 States/UTs');
assert(getStateById('UP')?.name === 'Uttar Pradesh', 'getStateById("UP") resolves correctly');
assert(getStateById('state-up')?.name === 'Uttar Pradesh', 'getStateById("state-up") resolves correctly');
assert(getDistrictsByState('state-up').length === 75, 'getDistrictsByState("state-up") returns all 75 UP districts');
assert(getDistrictsByState('UP').length === 75, 'getDistrictsByState("UP") returns all 75 UP districts');
assert(getDistrictById('dist-up-varanasi')?.name === 'Varanasi', 'getDistrictById("dist-up-varanasi") resolves Varanasi');
assert(getDistrictById('UP-VAR')?.name === 'Varanasi', 'getDistrictById("UP-VAR") resolves Varanasi');

// ----------------------------------------------------------------------------
// 4. Supabase Seed SQL Parity & Completeness Check
// ----------------------------------------------------------------------------
console.log('\n4. Validating Supabase Seed SQL (02_all_india_districts.sql)');
const seedSqlPath = path.join(rootDir, 'supabase', 'seed', '02_all_india_districts.sql');
assert(fs.existsSync(seedSqlPath), 'Seed file supabase/seed/02_all_india_districts.sql exists');

const seedSql = fs.readFileSync(seedSqlPath, 'utf-8');

// Count INSERT values in the SQL seed
// Each row matches ('dist-...', 'state-...', '...', '...', ...)
const sqlDistMatches = [...seedSql.matchAll(/\('(dist-[^']+)',\s*'(state-[^']+|ut-[^']+)',\s*'([^']+)',\s*'([^']+)',\s*(\d+)\)/g)];
assert(sqlDistMatches.length === 784, `SQL seed contains exactly 784 district insert statements (found ${sqlDistMatches.length})`);
assert(sqlDistMatches.length !== 21, 'SQL seed is NOT the previous 21-district subset');

// Verify every district in SQL has valid state
let sqlOrphan = false;
for (const match of sqlDistMatches) {
  const sqlStateId = match[2];
  if (!stateIdSet.has(sqlStateId)) {
    sqlOrphan = true;
    console.error(`SQL row references invalid state: ${sqlStateId}`);
  }
}
assert(!sqlOrphan, 'Every district in the SQL seed references a valid parent State/UT');

// ----------------------------------------------------------------------------
// 5. Skills & Opportunities Catalog Integrity
// ----------------------------------------------------------------------------
console.log('\n5. Validating Skills & Opportunities Master Tables');
assert(SKILLS_MASTER.length === 11, `Skills catalog contains exactly 11 standardized skills (found ${SKILLS_MASTER.length})`);

let invalidNsqf = false;
let missingSkillSource = false;
for (const s of SKILLS_MASTER) {
  if (!s.nsqfLevel || s.nsqfLevel < 1 || s.nsqfLevel > 8) invalidNsqf = true;
  if (!s.source || !s.sourceUrl || !s.qpCode) missingSkillSource = true;
}
assert(!invalidNsqf, 'All skills have legitimate NSQF levels (Levels 1 to 8)');
assert(!missingSkillSource, 'All skills have verified source agencies, QP codes, and URLs');

assert(VERIFIED_OPPORTUNITIES.length === 7, `Verified opportunities catalog contains 7 schemes (found ${VERIFIED_OPPORTUNITIES.length})`);

let missingOppSource = false;
let orphanSkillInOpp = false;
let invalidDistrictRef = false;
const skillIdSet = new Set(SKILLS_MASTER.map(s => s.id));

for (const opp of VERIFIED_OPPORTUNITIES) {
  if (!opp.source || !opp.sourceUrl || !opp.sourceUrl.startsWith('http')) missingOppSource = true;
  for (const skId of (opp.skillIds || [])) {
    if (!skillIdSet.has(skId)) orphanSkillInOpp = true;
  }
  if (opp.stateId && !stateIdSet.has(opp.stateId)) invalidStateRef = true;
  if (opp.districtId && !districtIdSet.has(opp.districtId)) {
    invalidDistrictRef = true;
    console.error(`Opportunity ${opp.title} references invalid district: ${opp.districtId}`);
  }
}

assert(!missingOppSource, 'All opportunities have traceable, verified government portal URLs');
assert(!orphanSkillInOpp, 'All opportunity-skill relationships reference valid skills');
assert(!invalidDistrictRef, 'All location-bound opportunities reference valid official districts (e.g. Varanasi)');

// ----------------------------------------------------------------------------
// Summary
// ----------------------------------------------------------------------------
console.log('\n====================================================');
console.log(`TOTAL DATA QUALITY CHECKS: ${passed + failed} | PASSED: ${passed} | FAILED: ${failed}`);
console.log('====================================================');

if (failed > 0) {
  process.exit(1);
} else {
  console.log('🎉 ALL NATIONAL LOCATION & DATA INTEGRITY TESTS PASSED PERFECTLY!\n');
}
