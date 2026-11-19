"""Isolated Docker desktop computer (Batch3 / Cinebot / Grok style).

Ports the pattern from
``deencat/Batch3-UAT-Migration-Dashboard`` → ``batch3_live/isolated_computer.py``:

* Linux XFCE + Chromium in Docker (``accetto/ubuntu-vnc-xfce-chromium-g3``)
* noVNC panel for humans
* CDP (:9222) for Playwright automation
* xdotool for type / key when needed

Enable with::

    COMPUTER_USE_MODE=isolated
"""

from __future__ import annotations

import base64
import logging
import os
import re
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

CONTAINER_NAME = os.environ.get("GPTR_COMPUTER_CONTAINER") or "gptr-research-computer"
IMAGE = (
    os.environ.get("GPTR_COMPUTER_IMAGE")
    or "accetto/ubuntu-vnc-xfce-chromium-g3:latest"
)
NOVNC_PORT = int(os.environ.get("GPTR_ISOLATED_NOVNC_PORT") or "6901")
CDP_PORT = int(os.environ.get("GPTR_ISOLATED_CDP_PORT") or "9222")
VNC_PW = (os.environ.get("GPTR_ISOLATED_VNC_PW") or "gptrlab").strip() or "gptrlab"
RESOLUTION = os.environ.get("GPTR_ISOLATED_RESOLUTION") or "1280x800x24"
# Public browser URL (nginx path). Example:
# https://research.hexsenses.com/computer/<token>/vnc.html?...
PUBLIC_EMBED_URL = (os.environ.get("GPTR_ISOLATED_PUBLIC_EMBED_URL") or "").strip()


def _embed_url(*, running: bool) -> Optional[str]:
    if not running:
        return None
    if PUBLIC_EMBED_URL:
        return PUBLIC_EMBED_URL
    return (
        f"http://127.0.0.1:{NOVNC_PORT}/vnc.html"
        f"?autoconnect=1&reconnect=1&resize=off&password={VNC_PW}"
    )

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


def _docker() -> Optional[str]:
    return shutil.which("docker")


def _run(args: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)


def docker_ready() -> tuple[bool, str]:
    exe = _docker()
    if not exe:
        return False, "Docker CLI not found"
    try:
        proc = _run([exe, "info"], timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "docker info failed")[:300]
    return True, "ok"


def container_running() -> bool:
    exe = _docker()
    if not exe:
        return False
    proc = _run([exe, "inspect", "-f", "{{.State.Running}}", CONTAINER_NAME], timeout=20)
    return proc.returncode == 0 and (proc.stdout or "").strip().lower() == "true"


def status() -> Dict[str, Any]:
    ready_docker, docker_msg = docker_ready()
    running = container_running() if ready_docker else False
    return {
        "ok": True,
        "mode": "isolated-docker",
        "ready": bool(ready_docker and running),
        "dockerReady": ready_docker,
        "dockerMessage": docker_msg,
        "container": CONTAINER_NAME,
        "image": IMAGE,
        "running": running,
        "novncPort": NOVNC_PORT,
        "cdpPort": CDP_PORT,
        "embedUrl": _embed_url(running=running),
        "source": (
            "Batch3-UAT-Migration-Dashboard/batch3_live/isolated_computer.py "
            "(Cinebot/Grok-style isolated desktop)"
        ),
        "hint": (
            "Standalone Linux desktop (XFCE + Chromium) in Docker — "
            "same idea as Batch3 isolated_computer / Cinebot / Grok computer."
        ),
    }


def start_container() -> Dict[str, Any]:
    ready_docker, docker_msg = docker_ready()
    if not ready_docker:
        return {"ok": False, "error": docker_msg}
    exe = _docker()
    assert exe
    if container_running():
        return {"ok": True, "already": True, "container": CONTAINER_NAME, **status()}
    _run([exe, "rm", "-f", CONTAINER_NAME], timeout=60)
    proc = _run(
        [
            exe,
            "run",
            "-d",
            "--name",
            CONTAINER_NAME,
            "-p",
            f"{NOVNC_PORT}:6901",
            "-p",
            f"{CDP_PORT}:9222",
            "-e",
            f"VNC_PW={VNC_PW}",
            "-e",
            f"VNC_RESOLUTION={RESOLUTION}",
            IMAGE,
        ],
        timeout=180,
    )
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout or "docker run failed")[:500]}
    deadline = time.time() + 40
    while time.time() < deadline:
        if not container_running():
            logs = _run([exe, "logs", "--tail", "20", CONTAINER_NAME], timeout=20)
            return {
                "ok": False,
                "error": "Container exited early",
                "logs": (logs.stdout or "")[-400:],
            }
        try:
            import urllib.request

            with urllib.request.urlopen(
                f"http://127.0.0.1:{NOVNC_PORT}/vnc.html", timeout=2
            ) as resp:
                if resp.status == 200:
                    return {"ok": True, "started": True, "container": CONTAINER_NAME, **status()}
        except Exception:
            pass
        time.sleep(1)
    return {"ok": True, "started": True, "warning": "noVNC slow to answer", **status()}


def stop_container() -> Dict[str, Any]:
    exe = _docker()
    if not exe:
        return {"ok": False, "error": "Docker not found"}
    proc = _run([exe, "rm", "-f", CONTAINER_NAME], timeout=60)
    return {
        "ok": proc.returncode == 0,
        "error": (proc.stderr or "").strip() if proc.returncode else "",
    }


def _ensure_cdp_bridge() -> None:
    exe = _docker()
    if not exe or not container_running():
        return
    _run(
        [
            exe,
            "exec",
            "-u",
            "root",
            CONTAINER_NAME,
            "bash",
            "-lc",
            "export DEBIAN_FRONTEND=noninteractive; "
            "command -v socat >/dev/null 2>&1 || "
            "apt-get update -qq && apt-get install -y -qq socat >/dev/null",
        ],
        timeout=180,
    )
    _run(
        [
            exe,
            "exec",
            "-u",
            "root",
            CONTAINER_NAME,
            "bash",
            "-lc",
            "if [ -f /tmp/gptr_socat_cdp.pid ]; then "
            "kill $(cat /tmp/gptr_socat_cdp.pid) 2>/dev/null || true; fi",
        ],
        timeout=20,
    )
    _run(
        [
            exe,
            "exec",
            "-d",
            "-u",
            "root",
            CONTAINER_NAME,
            "bash",
            "-lc",
            "socat TCP-LISTEN:9222,fork,reuseaddr,bind=0.0.0.0 "
            "TCP:127.0.0.1:9223 >/tmp/socat-cdp.log 2>&1 & "
            "echo $! > /tmp/gptr_socat_cdp.pid",
        ],
        timeout=30,
    )
    time.sleep(0.4)


def _ensure_input_tools() -> Dict[str, Any]:
    exe = _docker()
    if not exe or not container_running():
        return {"ok": False, "error": "container not running"}
    check = _run(
        [exe, "exec", CONTAINER_NAME, "bash", "-lc", "command -v xdotool"],
        timeout=30,
    )
    if check.returncode == 0:
        return {"ok": True}
    install = _run(
        [
            exe,
            "exec",
            "-u",
            "root",
            CONTAINER_NAME,
            "bash",
            "-lc",
            "export DEBIAN_FRONTEND=noninteractive; "
            "apt-get update -qq && apt-get install -y -qq xdotool xclip >/dev/null",
        ],
        timeout=300,
    )
    if install.returncode != 0:
        return {"ok": False, "error": (install.stderr or install.stdout or "apt failed")[:400]}
    return {"ok": True, "installed": True}


def launch_chromium(url: str) -> Dict[str, Any]:
    if not container_running():
        started = start_container()
        if not started.get("ok"):
            return {"ok": False, "error": started.get("error") or "start failed"}
    exe = _docker()
    assert exe
    target = (url or "").strip()
    if target and not target.startswith(("http://", "https://")):
        target = "https://" + target
    if target and target not in {"about:blank", ""}:
        err = _host_allowed(target)
        if err:
            return {"ok": False, "error": err}
    _ensure_cdp_bridge()
    cmd = [
        exe,
        "exec",
        "-d",
        "-u",
        "headless",
        "-e",
        "DISPLAY=:1",
        CONTAINER_NAME,
        "chromium-browser",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--ignore-certificate-errors",
        "--remote-debugging-port=9223",
        "--remote-allow-origins=*",
        target or "about:blank",
    ]
    proc = _run(cmd, timeout=60)
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout or "chromium launch failed")[:500]}
    _ensure_input_tools()
    time.sleep(1.5)
    return {
        "ok": True,
        "url": target,
        "cdp": f"http://127.0.0.1:{CDP_PORT}",
        "embedUrl": status().get("embedUrl"),
        "message": "Chromium launched in isolated desktop — open noVNC to watch.",
    }


def type_text_desktop(text: str, *, press_enter: bool = False) -> Dict[str, Any]:
    if not container_running():
        return {"ok": False, "error": "Isolated computer not running"}
    tools = _ensure_input_tools()
    if not tools.get("ok"):
        return tools
    exe = _docker()
    assert exe
    payload = text or ""
    if len(payload) > 8000:
        return {"ok": False, "error": "Text too long (max 8000)"}
    if payload:
        proc = _run(
            [
                exe,
                "exec",
                "-u",
                "headless",
                "-e",
                "DISPLAY=:1",
                CONTAINER_NAME,
                "xdotool",
                "type",
                "--clearmodifiers",
                "--delay",
                "12",
                "--",
                payload,
            ],
            timeout=120,
        )
        if proc.returncode != 0:
            return {"ok": False, "error": (proc.stderr or proc.stdout or "type failed")[:400]}
    if press_enter:
        _run(
            [
                exe,
                "exec",
                "-u",
                "headless",
                "-e",
                "DISPLAY=:1",
                CONTAINER_NAME,
                "xdotool",
                "key",
                "--clearmodifiers",
                "Return",
            ],
            timeout=30,
        )
    return {"ok": True, "chars": len(payload), "pressEnter": press_enter}


def click_xy(x: int, y: int) -> Dict[str, Any]:
    if not container_running():
        return {"ok": False, "error": "Isolated computer not running"}
    tools = _ensure_input_tools()
    if not tools.get("ok"):
        return tools
    exe = _docker()
    assert exe
    for args in (
        ["xdotool", "mousemove", str(int(x)), str(int(y))],
        ["xdotool", "click", "1"],
    ):
        proc = _run(
            [exe, "exec", "-u", "headless", "-e", "DISPLAY=:1", CONTAINER_NAME, *args],
            timeout=30,
        )
        if proc.returncode != 0:
            return {"ok": False, "error": (proc.stderr or proc.stdout or "click failed")[:400]}
    return {"ok": True, "x": x, "y": y}


def screenshot_png() -> Dict[str, Any]:
    """Grab the isolated desktop via ImageMagick import."""
    if not container_running():
        return {"ok": False, "error": "Isolated computer not running"}
    exe = _docker()
    assert exe
    _run(
        [
            exe,
            "exec",
            "-u",
            "root",
            CONTAINER_NAME,
            "bash",
            "-lc",
            "export DEBIAN_FRONTEND=noninteractive; "
            "command -v import >/dev/null 2>&1 || "
            "apt-get update -qq && apt-get install -y -qq imagemagick >/dev/null",
        ],
        timeout=180,
    )
    proc = _run(
        [
            exe,
            "exec",
            "-u",
            "headless",
            "-e",
            "DISPLAY=:1",
            CONTAINER_NAME,
            "bash",
            "-lc",
            "import -window root /tmp/gptr_desk.png && base64 -w0 /tmp/gptr_desk.png",
        ],
        timeout=60,
    )
    if proc.returncode != 0 or not (proc.stdout or "").strip():
        return {"ok": False, "error": (proc.stderr or proc.stdout or "screenshot failed")[:400]}
    b64 = (proc.stdout or "").strip()
    return {
        "ok": True,
        "mime": "image/png",
        "image_base64": b64,
        "bytes": len(base64.b64decode(b64)),
    }


# --- Playwright-over-CDP helpers (Batch3 smart path) ---

_cdp_pw = None
_cdp_browser = None
_cdp_page = None
_cdp_elements: Dict[str, str] = {}


async def cdp_connect() -> Dict[str, Any]:
    global _cdp_pw, _cdp_browser, _cdp_page
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        return {"ok": False, "error": f"playwright missing: {e}"}
    if not container_running():
        started = start_container()
        if not started.get("ok"):
            return started
    _ensure_cdp_bridge()
    try:
        if _cdp_page is None:
            _cdp_pw = await async_playwright().start()
            _cdp_browser = await _cdp_pw.chromium.connect_over_cdp(
                f"http://127.0.0.1:{CDP_PORT}"
            )
            contexts = _cdp_browser.contexts
            if contexts and contexts[0].pages:
                _cdp_page = contexts[0].pages[0]
            else:
                ctx = contexts[0] if contexts else await _cdp_browser.new_context()
                _cdp_page = await ctx.new_page()
        return {"ok": True, "url": _cdp_page.url}
    except Exception as e:
        launch_chromium("about:blank")
        time.sleep(2)
        try:
            if _cdp_pw is None:
                _cdp_pw = await async_playwright().start()
            _cdp_browser = await _cdp_pw.chromium.connect_over_cdp(
                f"http://127.0.0.1:{CDP_PORT}"
            )
            contexts = _cdp_browser.contexts
            _cdp_page = (
                contexts[0].pages[0]
                if contexts and contexts[0].pages
                else await contexts[0].new_page()
            )
            return {"ok": True, "url": _cdp_page.url, "relaunched": True}
        except Exception as e2:
            return {"ok": False, "error": f"CDP connect failed: {e}; retry: {e2}"}


async def cdp_navigate(url: str) -> Dict[str, Any]:
    err = _host_allowed(url)
    if err:
        return {"ok": False, "error": err}
    conn = await cdp_connect()
    if not conn.get("ok"):
        return launch_chromium(url)
    assert _cdp_page is not None
    await _cdp_page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    return {"ok": True, "url": _cdp_page.url, "title": await _cdp_page.title(), "via": "cdp"}


async def cdp_snapshot(max_elements: int = 40) -> Dict[str, Any]:
    global _cdp_elements
    conn = await cdp_connect()
    if not conn.get("ok"):
        return conn
    assert _cdp_page is not None
    _cdp_elements = {}
    lines: List[str] = []
    idx = 0
    handles = await _cdp_page.query_selector_all(
        "a, button, input, textarea, select, [role='button'], [role='link'], "
        "[role='textbox'], [role='checkbox'], [role='menuitem']"
    )
    for handle in handles:
        if idx >= max_elements:
            break
        try:
            if not await handle.is_visible():
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
            await handle.evaluate("(el, r) => el.setAttribute('data-gptr-ref', r)", ref)
            _cdp_elements[ref] = f"[data-gptr-ref='{ref}']"
            lines.append(f"- {ref}: role={role} name={name!r}")
            idx += 1
        except Exception:
            continue
    return {
        "ok": True,
        "url": _cdp_page.url,
        "title": await _cdp_page.title(),
        "elements": lines,
        "count": len(_cdp_elements),
        "via": "cdp-isolated",
    }


async def cdp_click(ref: str) -> Dict[str, Any]:
    conn = await cdp_connect()
    if not conn.get("ok"):
        return conn
    assert _cdp_page is not None
    key = (ref or "").lstrip("@")
    selector = _cdp_elements.get(key) or f"[data-gptr-ref='{key}']"
    await _cdp_page.click(selector, timeout=15_000)
    return {"ok": True, "clicked": key, "url": _cdp_page.url}


async def cdp_type(ref: str, text: str) -> Dict[str, Any]:
    conn = await cdp_connect()
    if not conn.get("ok"):
        return conn
    assert _cdp_page is not None
    key = (ref or "").lstrip("@")
    if key:
        selector = _cdp_elements.get(key) or f"[data-gptr-ref='{key}']"
        await _cdp_page.fill(selector, text, timeout=15_000)
        return {"ok": True, "typed_into": key, "chars": len(text)}
    return type_text_desktop(text)


async def cdp_scroll(direction: str = "down", amount: int = 600) -> Dict[str, Any]:
    conn = await cdp_connect()
    if not conn.get("ok"):
        return conn
    assert _cdp_page is not None
    delta = amount if direction == "down" else -amount
    await _cdp_page.mouse.wheel(0, delta)
    return {"ok": True, "scrolled": direction, "amount": amount}


async def cdp_extract(selector: Optional[str] = None) -> Dict[str, Any]:
    conn = await cdp_connect()
    if not conn.get("ok"):
        return conn
    assert _cdp_page is not None
    if selector:
        text = await _cdp_page.inner_text(selector, timeout=10_000)
    else:
        text = await _cdp_page.inner_text("body", timeout=10_000)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) > 12_000:
        text = text[:12_000] + "\n…[truncated]"
    return {"ok": True, "url": _cdp_page.url, "text": text}


async def cdp_screenshot() -> Dict[str, Any]:
    conn = await cdp_connect()
    if conn.get("ok") and _cdp_page is not None:
        raw = await _cdp_page.screenshot(type="png", full_page=False)
        b64 = base64.b64encode(raw).decode("ascii")
        return {
            "ok": True,
            "url": _cdp_page.url,
            "mime": "image/png",
            "image_base64": b64,
            "bytes": len(raw),
            "via": "cdp",
        }
    return screenshot_png()


async def cdp_close() -> Dict[str, Any]:
    global _cdp_pw, _cdp_browser, _cdp_page, _cdp_elements
    try:
        if _cdp_browser:
            await _cdp_browser.close()
    except Exception:
        pass
    try:
        if _cdp_pw:
            await _cdp_pw.stop()
    except Exception:
        pass
    _cdp_pw = _cdp_browser = _cdp_page = None
    _cdp_elements = {}
    return stop_container()


async def handle_isolated(args: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch one action against the Batch3-style isolated desktop."""
    action = (args.get("action") or "").strip()
    if action == "status":
        return status()
    if action == "start":
        return start_container()
    if action == "close":
        return await cdp_close()
    if action == "navigate":
        return await cdp_navigate(args.get("url") or "")
    if action == "snapshot":
        return await cdp_snapshot()
    if action == "click":
        ref = args.get("ref") or ""
        if ref:
            return await cdp_click(ref)
        x, y = args.get("x"), args.get("y")
        if x is not None and y is not None:
            return click_xy(int(x), int(y))
        return {"ok": False, "error": "click needs ref or x/y"}
    if action == "type":
        return await cdp_type(args.get("ref") or "", args.get("text") or "")
    if action == "scroll":
        return await cdp_scroll(
            direction=args.get("direction") or "down",
            amount=int(args.get("amount") or 600),
        )
    if action == "extract":
        return await cdp_extract(args.get("selector"))
    if action == "screenshot":
        return await cdp_screenshot()
    return {"ok": False, "error": f"unknown isolated action: {action}"}
