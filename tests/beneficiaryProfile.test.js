import assert from 'node:assert/strict';
import {
  toCreatePayload,
  toResolvedLocation,
  toUpdatePayload,
  toUserProfile,
} from '../src/services/beneficiaryProfile.js';

const beneficiary = {
  id: 'beneficiary-1',
  name: 'Asha Devi',
  preferred_language: 'hi',
  state_id: 'state-up',
  district_id: 'dist-up-varanasi',
  education_level: '10th_pass',
  current_occupation: 'Tailor',
  mobility_preference: 'within_15km',
};

assert.equal(toResolvedLocation(beneficiary).district.name, 'Varanasi');
assert.equal(toUserProfile(beneficiary).fullName, 'Asha Devi');
assert.equal(toUserProfile(beneficiary).education, '10th Pass');

assert.deepEqual(
  toCreatePayload({
    name: ' Asha Devi ',
    languageId: 'hi',
    resolvedLocation: { state: { id: 'state-up' }, district: { id: 'dist-up-varanasi' } },
  }),
  {
    name: 'Asha Devi',
    preferred_language: 'hi',
    state_id: 'state-up',
    district_id: 'dist-up-varanasi',
  },
);

const update = toUpdatePayload({
  fullName: 'Asha Singh',
  education: '10th Pass',
  currentWork: 'Tailor',
  mobilityPreference: 'Within 15 km of home block',
  location: 'This is display-only',
  skills: ['Demo skill'],
}, 'hi');
assert.deepEqual(update, {
  name: 'Asha Singh',
  preferred_language: 'hi',
  education_level: '10th_pass',
  current_occupation: 'Tailor',
  mobility_preference: 'within_15km',
});
assert.equal(Object.prototype.hasOwnProperty.call(update, 'location'), false);

console.log('✓ beneficiary profile mapping tests passed');
