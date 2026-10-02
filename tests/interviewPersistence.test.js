import assert from 'node:assert/strict';
import {
  getInterviewResumeStep,
  hydrateInterviewAnswers,
  toInterviewResponses,
} from '../src/services/interviewPersistence.js';

const draft = {
  status: 'draft',
  responses: {
    workInterest: '☀️ Solar & Electrical Maintenance',
    education: '🎓 10th Pass',
  },
};

assert.equal(getInterviewResumeStep(draft, 4), 5, 'resume begins at the first unanswered question');
assert.deepEqual(
  hydrateInterviewAnswers(draft, { name: 'Asha', location: { state: { id: 'state-up' } } }),
  {
    workInterest: '☀️ Solar & Electrical Maintenance',
    education: '🎓 10th Pass',
    name: 'Asha',
    location: { state: { id: 'state-up' } },
  },
);
assert.deepEqual(
  toInterviewResponses({ ...draft.responses, mobility: '🏡 Within my own village / block', name: 'ignored' }),
  {
    workInterest: '☀️ Solar & Electrical Maintenance',
    education: '🎓 10th Pass',
    mobility: '🏡 Within my own village / block',
  },
);
assert.equal(
  getInterviewResumeStep({ status: 'draft', responses: {
    workInterest: '☀️ Solar & Electrical Maintenance',
    education: '🎓 10th Pass',
    mobility: '🏡 Within my own village / block',
    preference: '📜 Certified Training + Monthly Stipend',
  } }, 4),
  7,
  'a fully answered draft opens the completion state',
);
assert.equal(getInterviewResumeStep({ status: 'completed', responses: {} }, 4), 7);

console.log('✓ interview persistence hydration tests passed');
