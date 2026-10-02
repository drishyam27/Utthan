const INTERVIEW_RESPONSE_KEYS = ['workInterest', 'education', 'mobility', 'preference'];

export function toInterviewResponses(answers = {}) {
  return Object.fromEntries(
    INTERVIEW_RESPONSE_KEYS
      .map(key => [key, answers[key]])
      .filter(([, value]) => value !== undefined),
  );
}

export function hydrateInterviewAnswers(session, { name = '', location = null } = {}) {
  return {
    ...(session?.responses || {}),
    ...(name ? { name } : {}),
    ...(location ? { location } : {}),
  };
}

export function getInterviewResumeStep(session, stepCount = INTERVIEW_RESPONSE_KEYS.length) {
  if (session?.status === 'completed') return stepCount + 3;

  const firstUnanswered = INTERVIEW_RESPONSE_KEYS.findIndex(
    key => !session?.responses?.[key],
  );
  return firstUnanswered === -1 ? stepCount + 3 : firstUnanswered + 3;
}

export { INTERVIEW_RESPONSE_KEYS };
