const STORAGE_KEY = 'utthan.beneficiary.session';

function getSessionStorage() {
  try {
    return typeof window !== 'undefined' ? window.sessionStorage : null;
  } catch {
    return null;
  }
}

export function saveBeneficiarySession({ beneficiaryId, sessionToken }) {
  if (!beneficiaryId || !sessionToken) return false;

  const storage = getSessionStorage();
  if (!storage) return false;

  try {
    storage.setItem(STORAGE_KEY, JSON.stringify({ beneficiaryId, sessionToken }));
    return true;
  } catch {
    return false;
  }
}

export function loadBeneficiarySession() {
  const storage = getSessionStorage();
  if (!storage) return null;

  try {
    const parsed = JSON.parse(storage.getItem(STORAGE_KEY) || 'null');
    if (
      !parsed
      || typeof parsed.beneficiaryId !== 'string'
      || !parsed.beneficiaryId
      || typeof parsed.sessionToken !== 'string'
      || !parsed.sessionToken
    ) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function clearBeneficiarySession() {
  const storage = getSessionStorage();
  if (!storage) return;

  try {
    storage.removeItem(STORAGE_KEY);
  } catch {
    // Storage can be unavailable in privacy-restricted browsers.
  }
}

export { STORAGE_KEY };
