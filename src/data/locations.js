/**
 * Official Location Master Data for India
 * Authoritative Source: Local Government Directory (LGD), Ministry of Panchayati Raj, Govt of India (lgdirectory.gov.in)
 * Canonical Master: src/data/canonicalLocations.json
 * 28 States + 8 Union Territories = 36 Administrative Entities | 784 Total Districts
 * 
 * Auto-generated from canonicalLocations.json. Do not edit manually.
 */

import canonicalData from './canonicalLocations.json' with { type: 'json' };

export const STATES = canonicalData.states.map(s => ({
  id: s.id,
  code: s.code,
  name: s.name,
  type: s.type === 'UT' ? 'union_territory' : 'state',
  lgdCode: s.lgdCode,
  entityType: s.type
}));

export const DISTRICTS = canonicalData.districts.map(d => ({
  id: d.id,
  stateId: d.stateId,
  stateCode: d.stateCode,
  name: d.name,
  code: d.code,
  lgdDistrictCode: d.lgdDistrictCode,
  census2001Code: d.census2001Code,
  census2011Code: d.census2011Code
}));

export function getStates() {
  return STATES;
}

export function getStateById(stateId) {
  if (!stateId) return null;
  return STATES.find(s => s.id === stateId || s.code === stateId);
}

export function getDistrictsByState(stateId) {
  if (!stateId) return [];
  return DISTRICTS.filter(d => d.stateId === stateId || d.stateCode === stateId);
}

export function getDistrictById(districtId) {
  if (!districtId) return null;
  return DISTRICTS.find(
    d => d.id === districtId || 
         d.code === districtId || 
         d.lgdDistrictCode === Number(districtId)
  );
}
