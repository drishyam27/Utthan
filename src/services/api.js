const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body && !(typeof FormData !== 'undefined' && options.body instanceof FormData)
          ? { 'Content-Type': 'application/json' }
          : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError('The Utthan service is unavailable right now.', 0);
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new ApiError(
      payload?.detail || 'The Utthan service could not complete this request.',
      response.status,
    );
  }

  return payload;
}

export function resolveLocation({ latitude, longitude, accuracy }) {
  return request('/api/locations/resolve', {
    method: 'POST',
    body: JSON.stringify({ latitude, longitude, accuracy: accuracy ?? null }),
  });
}

export function fetchOpportunities({ stateId } = {}) {
  const query = stateId ? `?state_id=${encodeURIComponent(stateId)}` : '';
  return request(`/api/opportunities${query}`);
}

export function fetchOpportunity(opportunityId) {
  return request(`/api/opportunities/${encodeURIComponent(opportunityId)}`);
}

function capabilityHeaders(sessionToken) {
  return sessionToken ? { Authorization: `Bearer ${sessionToken}` } : {};
}

export function createBeneficiary(profile) {
  return request('/api/beneficiaries', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

export function fetchBeneficiary(beneficiaryId, sessionToken) {
  return request(`/api/beneficiaries/${encodeURIComponent(beneficiaryId)}`, {
    headers: capabilityHeaders(sessionToken),
  });
}

export function updateBeneficiary(beneficiaryId, sessionToken, profile) {
  return request(`/api/beneficiaries/${encodeURIComponent(beneficiaryId)}`, {
    method: 'PATCH',
    headers: capabilityHeaders(sessionToken),
    body: JSON.stringify(profile),
  });
}

export function createOrResumeInterview(beneficiaryId, sessionToken, language = 'hi') {
  return request(`/api/beneficiaries/${encodeURIComponent(beneficiaryId)}/interviews`, {
    method: 'POST',
    headers: capabilityHeaders(sessionToken),
    body: JSON.stringify({ language }),
  });
}

export function fetchInterview(interviewId, sessionToken) {
  return request(`/api/interviews/${encodeURIComponent(interviewId)}`, {
    headers: capabilityHeaders(sessionToken),
  });
}

export function updateInterview(interviewId, sessionToken, responses, expectedRevision) {
  return request(`/api/interviews/${encodeURIComponent(interviewId)}`, {
    method: 'PATCH',
    headers: capabilityHeaders(sessionToken),
    body: JSON.stringify({ responses, expected_revision: expectedRevision }),
  });
}

export function completeInterview(interviewId, sessionToken, expectedRevision) {
  return request(`/api/interviews/${encodeURIComponent(interviewId)}/complete`, {
    method: 'POST',
    headers: capabilityHeaders(sessionToken),
    body: JSON.stringify({ expected_revision: expectedRevision }),
  });
}

export function fetchRecommendations(beneficiaryId, sessionToken) {
  return request(`/api/beneficiaries/${encodeURIComponent(beneficiaryId)}/recommendations`, {
    headers: capabilityHeaders(sessionToken),
  });
}

export function transcribeAudio(audioBlob, languageHint, sessionToken) {
  const formData = new FormData();
  const filename = audioBlob.type?.includes('wav') ? 'audio.wav' : 'audio.webm';
  formData.append('file', audioBlob, filename);
  if (languageHint) {
    formData.append('language', languageHint);
  }

  return request('/api/voice/transcribe', {
    method: 'POST',
    headers: sessionToken ? capabilityHeaders(sessionToken) : {},
    body: formData,
  });
}
