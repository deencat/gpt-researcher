"""Auth gate for playbook catalog APIs (oauth2-proxy header based). :-)"""

from __future__ import annotations

import os
import re
from typing import Optional

from fastapi import HTTPException, Request

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

AUTH_HEADER_CANDIDATES = (
    "x-auth-request-email",
    "x-forwarded-email",
)


def auth_disabled() -> bool:
    """When true, playbook GETs stay open (local OSS / CI without a proxy)."""
    return os.getenv("PLAYBOOKS_REQUIRE_AUTH", "1").strip().lower() in {
        "0",
        "false",
        "no",
        "off",
    }


def email_from_request(request: Request) -> Optional[str]:
    headers = {k.lower(): v for k, v in request.headers.items()}
    for key in AUTH_HEADER_CANDIDATES:
        value = headers.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return None


def require_playbook_auth(request: Request) -> str:
    """Require a signed-in email from the reverse proxy, unless auth is disabled.

    Production (Hexsenses / oauth2-proxy) leaves PLAYBOOKS_REQUIRE_AUTH at the
    default of ``1`` so unauthenticated GETs receive 401. Local open-source
    runs can set ``PLAYBOOKS_REQUIRE_AUTH=0``.
    """
    if auth_disabled():
        return email_from_request(request) or "anonymous@local"

    email = email_from_request(request)
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for playbook catalog",
        )
    if not _EMAIL_RE.match(email):
        raise HTTPException(status_code=401, detail="Invalid authenticated email")
    return email
