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
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
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
