"""Playwright browser session for computer use.

Optional dependency: ``pip install playwright && playwright install chromium``.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "metadata.google.internal",
}


def _host_allowed(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
    except Exception:
        return "invalid URL"
    if parsed.scheme not in {"http", "https"}:
        return "only http(s) URLs are allowed"
    host = (parsed.hostname or "").lower()
    if not host:
        return "missing host"
    if host in _BLOCKED_HOSTS or host.endswith(".local") or host.endswith(".internal"):
        return f"blocked host: {host}"
    if re.match(r"^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[0-1])\.)", host):
        return f"private network host blocked: {host}"
    return None


@dataclass
class ElementRef:
    ref: str
    role: str
    name: str
    selector: str


@dataclass
class BrowserSession:
    session_id: str
    _playwright: Any = None
    _browser: Any = None
    _page: Any = None
    _elements: Dict[str, ElementRef] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def ensure(self) -> None:
        if self._page is not None:
            return
        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            raise RuntimeError(
                "playwright is not installed. Run: "
                "pip install playwright && playwright install chromium"
            ) from e

        headless = os.getenv("COMPUTER_USE_HEADLESS", "true").lower() not in {
            "0",
            "false",
            "no",
        }
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=headless)
        self._page = await self._browser.new_page(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
        )

    async def close(self) -> None:
        async with self._lock:
            try:
                if self._browser:
                    await self._browser.close()
            finally:
                self._browser = None
                self._page = None
                if self._playwright:
                    await self._playwright.stop()
                self._playwright = None
                self._elements.clear()

    async def navigate(self, url: str) -> Dict[str, Any]:
        err = _host_allowed(url)
        if err:
            return {"ok": False, "error": err}
        async with self._lock:
            await self.ensure()
            assert self._page is not None
            await self._page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            title = await self._page.title()
            return {"ok": True, "url": self._page.url, "title": title}

    async def snapshot(self, max_elements: int = 40) -> Dict[str, Any]:
        async with self._lock:
            await self.ensure()
            assert self._page is not None
            self._elements.clear()
            lines: List[str] = []
            idx = 0
            # Prefer interactive nodes for click targets.
            handles = await self._page.query_selector_all(
                "a, button, input, textarea, select, [role='button'], [role='link'], "
                "[role='textbox'], [role='checkbox'], [role='menuitem']"
            )
            for handle in handles:
                if idx >= max_elements:
                    break
                try:
                    visible = await handle.is_visible()
                    if not visible:
                        continue
                    role = (
                        await handle.get_attribute("role")
                        or await handle.evaluate("el => el.tagName.toLowerCase()")
                    )
                    name = (
                        (await handle.inner_text() or "").strip()
                        or (await handle.get_attribute("aria-label") or "")
                        or (await handle.get_attribute("placeholder") or "")
                        or (await handle.get_attribute("name") or "")
                        or (await handle.get_attribute("value") or "")
                    )
                    name = re.sub(r"\s+", " ", name)[:80]
                    ref = f"e{idx + 1}"
                    # Stable-ish selector via data attribute we stamp.
                    await handle.evaluate(
                        "(el, r) => el.setAttribute('data-gptr-ref', r)", ref
                    )
                    selector = f"[data-gptr-ref='{ref}']"
                    self._elements[ref] = ElementRef(ref, role, name, selector)
                    lines.append(f"- {ref}: role={role} name={name!r}")
                    idx += 1
                except Exception:
                    continue
            title = await self._page.title()
            return {
                "ok": True,
                "url": self._page.url,
                "title": title,
                "elements": lines,
                "count": len(self._elements),
            }

    def _resolve(self, ref: str) -> ElementRef:
        key = ref.lstrip("@")
        if key not in self._elements:
            raise KeyError(f"unknown ref {ref!r}; call snapshot first")
        return self._elements[key]

    async def click(self, ref: str) -> Dict[str, Any]:
        async with self._lock:
            await self.ensure()
            assert self._page is not None
            el = self._resolve(ref)
            await self._page.click(el.selector, timeout=15_000)
            return {"ok": True, "clicked": el.ref, "name": el.name, "url": self._page.url}

    async def type_text(self, ref: str, text: str) -> Dict[str, Any]:
        async with self._lock:
            await self.ensure()
            assert self._page is not None
            el = self._resolve(ref)
            await self._page.fill(el.selector, text, timeout=15_000)
            return {"ok": True, "typed_into": el.ref, "chars": len(text)}

    async def scroll(self, direction: str = "down", amount: int = 600) -> Dict[str, Any]:
        async with self._lock:
            await self.ensure()
            assert self._page is not None
            delta = amount if direction == "down" else -amount
            await self._page.mouse.wheel(0, delta)
            return {"ok": True, "scrolled": direction, "amount": amount}

    async def extract(self, selector: Optional[str] = None) -> Dict[str, Any]:
        async with self._lock:
            await self.ensure()
            assert self._page is not None
            if selector:
                text = await self._page.inner_text(selector, timeout=10_000)
            else:
                text = await self._page.inner_text("body", timeout=10_000)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if len(text) > 12_000:
                text = text[:12_000] + "\n…[truncated]"
            return {"ok": True, "url": self._page.url, "text": text}

    async def screenshot(self) -> Dict[str, Any]:
        async with self._lock:
            await self.ensure()
            assert self._page is not None
            import base64

            raw = await self._page.screenshot(type="png", full_page=False)
            b64 = base64.b64encode(raw).decode("ascii")
            return {
                "ok": True,
                "url": self._page.url,
                "mime": "image/png",
                "image_base64": b64,
                "bytes": len(raw),
            }


_SESSIONS: Dict[str, BrowserSession] = {}
_SESSIONS_LOCK = asyncio.Lock()


async def get_session(session_id: str = "default") -> BrowserSession:
    async with _SESSIONS_LOCK:
        if session_id not in _SESSIONS:
            _SESSIONS[session_id] = BrowserSession(session_id=session_id)
        return _SESSIONS[session_id]


async def close_session(session_id: str = "default") -> None:
    async with _SESSIONS_LOCK:
        sess = _SESSIONS.pop(session_id, None)
    if sess:
        await sess.close()
