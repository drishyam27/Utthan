"""High-entropy anonymous capability token helpers.

This module deliberately has no logging and no persistence/API behavior. Later
services may persist only the hash returned by ``hash_capability_token``.
"""

import hashlib
import hmac
import secrets


def generate_capability_token() -> str:
    """Generate a high-entropy opaque token for an anonymous session."""

    return secrets.token_urlsafe(32)


def hash_capability_token(token: str) -> str:
    """Hash a capability token for server-side storage."""

    if not isinstance(token, str) or not token:
        raise ValueError("capability token must be a non-empty string")
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_capability_token(token: str, token_hash: str) -> bool:
    """Constant-time verification against a stored token hash."""

    if (
        not isinstance(token, str)
        or not isinstance(token_hash, str)
        or not token
        or not token_hash
    ):
        return False
    return hmac.compare_digest(hash_capability_token(token), token_hash)
