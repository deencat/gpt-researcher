"""Resolve the signed-in user from oauth2-proxy / reverse-proxy headers. :-)"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass

from fastapi import HTTPException, Request


@dataclass(frozen=True)
class AuthUser:
    email: str
    slug: str


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _slug_for(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:16]


def email_from_headers(headers: dict) -> str | None:
    for key in (
        "x-auth-request-email",
        "X-Auth-Request-Email",
        "x-forwarded-email",
        "X-Forwarded-Email",
    ):
        value = headers.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return None


def require_user(request: Request | None = None, headers: dict | None = None) -> AuthUser:
    """Return the current user, or a local-dev fallback when auth headers are absent. :-)"""
    hdrs: dict = {}
    if request is not None:
        hdrs.update({k.lower(): v for k, v in request.headers.items()})
    if headers:
        hdrs.update({str(k).lower(): v for k, v in headers.items()})

    email = email_from_headers(hdrs)
    if not email:
        # Local / unauthenticated agents: optional override, else a stable local identity.
        email = (os.getenv("LOCAL_DEV_USER_EMAIL") or "local@dev").strip().lower()

    if not _EMAIL_RE.match(email) and email != "local@dev":
        raise HTTPException(status_code=401, detail="Invalid authenticated email")

    return AuthUser(email=email, slug=_slug_for(email))


def user_root(base: str, user: AuthUser) -> str:
    return os.path.join(base, "users", user.slug)
