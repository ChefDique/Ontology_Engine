"""
Supabase Client — Shared client and JWT verification for the Ontology Engine API.

Provides:
    - get_supabase_client(): initialized Supabase admin client (service role)
    - verify_jwt(token): validates Supabase access tokens, returns user_id
    - get_anon_client(): public client for frontend-compatible operations
"""

import os
import logging
from functools import lru_cache

import jwt
from supabase import create_client, Client

logger = logging.getLogger(__name__)


def _require_env(key: str) -> str:
    """Get required env var or raise."""
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Get the Supabase admin client (service role — bypasses RLS).

    Use this for backend operations: inserting analysis results,
    uploading files to storage, checking rate limits.
    """
    url = _require_env("SUPABASE_URL")
    service_key = _require_env("SUPABASE_SERVICE_KEY")
    return create_client(url, service_key)


def verify_jwt(token: str) -> dict:
    """Verify a Supabase access token and return the decoded payload.

    Args:
        token: JWT access token from Supabase Auth (from Authorization header).

    Returns:
        Decoded JWT payload dict with at minimum:
            - sub: user UUID
            - email: user email
            - role: 'authenticated' or 'anon'

    Raises:
        jwt.InvalidTokenError: If token is invalid, expired, or malformed.
    """
    jwt_secret = _require_env("SUPABASE_JWT_SECRET")

    payload = jwt.decode(
        token,
        jwt_secret,
        algorithms=["HS256"],
        audience="authenticated",
    )

    return payload


def get_user_id_from_token(token: str) -> str:
    """Extract user_id (UUID) from a verified JWT.

    Args:
        token: Supabase access token.

    Returns:
        User UUID string.

    Raises:
        jwt.InvalidTokenError: If token is invalid.
        KeyError: If 'sub' claim is missing.
    """
    payload = verify_jwt(token)
    return payload["sub"]
