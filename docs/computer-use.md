# Computer use (browser lab)

Hexsenses can drive a **headless browser** (and optionally short Python) when a research or chat question needs interactive steps — not just a static scrape.

## What we found on the VPS

| Project | Status |
| --- | --- |
| **Cinebot-v1** | Playwright computer use is **specified** (Higgsfield web UI) but **not implemented** (Agents 4–5 are Sprint 2 stubs). |
| **Hermes** (`~/.hermes/hermes-agent`) | Real `computer_use` exists, but is **macOS + cua-driver**. Also has Linux-friendly `browser_tool` + `code_execution_tool`. |

This Hexsenses module ports the **Hermes browser / Cinebot Playwright** idea for **Linux VPS**: Playwright Chromium + accessibility-style element refs + optional sandboxed `run_python`.

## Setup

```bash
pip install playwright
playwright install chromium
```

Optional chat tool:

```bash
# in backend .env
COMPUTER_USE_ENABLED=true
```

For **research runs**, add the MCP preset **Computer use** in Settings (runs `python -m gpt_researcher.computer_use`).

## Actions

`navigate` · `snapshot` · `click` · `type` · `scroll` · `extract` · `screenshot` · `run_python` · `close`

Typical loop: `navigate` → `snapshot` → `click`/`type` by `ref=eN` → `extract`.

## Safety

- Blocks localhost / private IPs / `.internal` hosts.
- `run_python` rejects `open(`, `subprocess`, `os.system`, etc., and runs in a scrubbed env with a timeout.

## Not included (yet)

- macOS desktop control (Hermes cua-driver)
- Auto CAPTCHA solving (same policy as Cinebot SRS)
- Full Perplexity Computer / Cursor Cloud Agent orchestration
