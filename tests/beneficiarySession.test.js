import assert from 'node:assert/strict';
import {
  clearBeneficiarySession,
  loadBeneficiarySession,
  saveBeneficiarySession,
} from '../src/services/beneficiarySession.js';

const values = new Map();
globalThis.window = {
  sessionStorage: {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  },
};

clearBeneficiarySession();
assert.equal(loadBeneficiarySession(), null, 'empty session storage returns no beneficiary session');

const session = { beneficiaryId: 'beneficiary-1', sessionToken: 'opaque-capability-token' };
assert.equal(saveBeneficiarySession(session), true, 'valid beneficiary session is stored');
assert.deepEqual(loadBeneficiarySession(), session, 'stored session can hydrate after reload');

values.set('utthan.beneficiary.session', JSON.stringify({ beneficiaryId: '', sessionToken: 'token' }));
assert.equal(loadBeneficiarySession(), null, 'malformed stored session is ignored');

saveBeneficiarySession(session);
clearBeneficiarySession();
assert.equal(loadBeneficiarySession(), null, 'clearing session removes the capability');

console.log('✓ beneficiary session storage tests passed');
