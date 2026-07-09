from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

import httpx
import jwt
from fastapi import Header, HTTPException, Query, status
from jwt.algorithms import RSAAlgorithm

from .config import get_settings


@lru_cache(maxsize=1)
def get_jwks() -> dict[str, Any]:
    settings = get_settings()
    jwks_url = settings["supabase_jwks_url"]

    if not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWKS_URL is not configured",
        )

    response = httpx.get(jwks_url, timeout=10.0)
    response.raise_for_status()
    return response.json()


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must use Bearer token format",
        )

    return token.strip()


def _verify_supabase_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    supabase_url = settings["supabase_url"]

    if not supabase_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL is not configured",
        )

    jwks = get_jwks()
    header = jwt.get_unverified_header(token)
    key_id = header.get("kid")
    if not key_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing key id")

    keys = jwks.get("keys", [])
    jwk = next((item for item in keys if item.get("kid") == key_id), None)
    if jwk is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signing key not found")

    public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[header.get("alg", "RS256")],
            audience="authenticated",
            issuer=f"{supabase_url}/auth/v1",
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Supabase token") from error

    return payload


def resolve_user_id(
    authorization: str | None = Header(default=None),
    user_id: str | None = Query(default=None),
) -> str | None:
    token = _extract_bearer_token(authorization)
    if token:
        payload = _verify_supabase_token(token)
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing subject")
        return str(subject)

    if user_id:
        return user_id

    return None
