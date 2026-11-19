# Computer use (browser lab + isolated desktop)

Hexsenses can drive a browser (and optionally short Python) when research or chat needs interactive steps — not just a static scrape.

## Source of truth (Batch3)

The real **Cinebot / Grok-style** isolated computer lives in:

[deencat/Batch3-UAT-Migration-Dashboard](https://github.com/deencat/Batch3-UAT-Migration-Dashboard/tree/main) → `batch3_live/isolated_computer.py`

| Piece | Role |
| --- | --- |
| `isolated_computer.py` | Docker XFCE + Chromium + noVNC + CDP + xdotool |
| `uat_computer.py` | Playwright session / screencast / recording |
| `novnc_desktop.py` | noVNC helpers |
| `computer_docker/` | Compose image (`accetto/ubuntu-vnc-xfce-chromium-g3`) |

Hexsenses ports that pattern as `gpt_researcher/computer_use/isolated.py`.

## Modes

| `COMPUTER_USE_MODE` | What runs |
| --- | --- |
| `playwright` (default) | Headless Chromium on the host (fast, no GUI) |
| `isolated` | Batch3-style Docker desktop — watch via noVNC |

Also checked on the VPS earlier:

| Project | Status |
| --- | --- |
| **Cinebot-v1** | Playwright computer use specified but Agents 4–5 still Sprint 2 stubs |
| **Hermes** | Real `computer_use` is **macOS + cua-driver**; Linux has `browser_tool` + `code_execution_tool` |

## Setup

### Playwright mode (default)

```bash
pip install playwright
playwright install chromium
```

```bash
# backend .env
COMPUTER_USE_ENABLED=true
# COMPUTER_USE_MODE=playwright
# COMPUTER_USE_HEADLESS=true
```

### Isolated mode (Batch3 desktop)

Requires Docker on the host, then:

```bash
COMPUTER_USE_ENABLED=true
COMPUTER_USE_MODE=isolated
# optional:
# GPTR_COMPUTER_IMAGE=accetto/ubuntu-vnc-xfce-chromium-g3:latest
# GPTR_ISOLATED_NOVNC_PORT=6901
# GPTR_ISOLATED_CDP_PORT=9222
# GPTR_ISOLATED_VNC_PW=gptrlab
```

First `status` / `start` / `navigate` pulls and runs the container. Open the returned `embedUrl` (noVNC) to watch the desktop.

For **research runs**, add the MCP preset **Computer use** in Settings (`python -m gpt_researcher.computer_use`).

## Actions

`status` · `start` · `navigate` · `snapshot` · `click` · `type` · `scroll` · `extract` · `screenshot` · `run_python` · `close`

Typical loop: `navigate` → `snapshot` → `click`/`type` by `ref=eN` → `extract`.

In isolated mode, `click` can also take desktop `x`/`y` (xdotool) when no ref is available.

## Safety

- Blocks localhost / private IPs / `.internal` hosts.
- `run_python` rejects `open(`, `subprocess`, `os.system`, etc., and runs in a scrubbed env with a timeout.

## Not included (yet)

- macOS desktop control (Hermes cua-driver)
- Auto CAPTCHA solving (same policy as Cinebot SRS)
- Full Perplexity Computer / Cursor Cloud Agent orchestration
