# Perplexity replacement gap analysis (Hexsenses / GPT-Researcher)

**Purpose:** Measure how close this project is to letting you **cancel a Perplexity subscription** (Pro ~US$20/mo, Max ~US$200/mo) — not how close we are to cloning every Perplexity product surface.

**Stack under review:** Live Hexsenses app (`research.sixlines.io` / GPT-Researcher Next.js GR UI) + backend research agent.  
**Compared to:** Perplexity Free / Pro / Max feature set as of late 2026.  
**Related:** `docs/hexsenses-first-100-plan.md` (revenue path); this doc is the **personal “can I cancel?”** scorecard.

---

## Executive verdict

| Question | Answer |
| --- | --- |
| Can Hexsenses **fully** replace Perplexity Pro today? | **No** |
| Can it replace Perplexity for **deep, cited research reports**? | **Mostly yes** (~**80–85%** of that job) |
| Can it replace Perplexity as **daily Google-like search**? | **No** (~**25–35%** of that job) |
| Overall “cancel Pro” readiness (weighted by typical Pro use) | **~55–60%** |
| Overall “cancel Max” readiness | **~35–40%** (Computer / Comet / Brain / high limits dominate Max) |

**Practical recommendation:** Keep Perplexity **Free** (or cancel Pro) **only if** your paid habit was deep reports + Projects. Keep Pro if you still open Perplexity many times a day for **instant** answers, voice, mobile, shopping, or Computer agents.

---

## Scoring method

Each row: **0–5** = how well Hexsenses covers that Perplexity capability for *you as the user*.

| Score | Meaning |
| --- | --- |
| 5 | Parity or better for your research use |
| 4 | Usable daily; small UX / polish gaps |
| 3 | Core works; missing convenience or speed |
| 2 | Partial / workaround only |
| 1 | Barely present |
| 0 | Absent |

**Weight** = how much that feature usually drives a Pro subscription for a research-heavy user (1–5).  
**Weighted gap** = weight × (5 − score). Higher = more painful to cancel.

---

## Feature-by-feature gap table

### A. Core research (what you actually need to cancel)

| # | Capability | Perplexity | Hexsenses now | Score | Wt | Gap | Notes |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| A1 | Instant cited Q&A (seconds) | Search / Pro Search default | Report-first; fastest run ~2 min summary | **1** | 5 | 20 | **Largest cancel blocker.** No “type → answer in 5s” surface. |
| A2 | Multi-step Pro Search | Automatic on Pro | Planner + execution agents inside a research *run* | **3** | 4 | 8 | Strong agent loop, wrong latency/UX vs search bar. |
| A3 | Deep Research long reports | Research / Advanced Deep Research (2–4 min class) | Deep + detailed + multi-agent report types | **4** | 5 | 5 | Core strength; often *deeper* / more configurable. |
| A4 | Inline citations + source list | Strong | Numbered cites + live Sources panel | **4** | 5 | 5 | Competitive for research; polish varies. |
| A5 | Follow-up chat on results | Thread chat + Memory | Post-report chat + optional `quick_search` | **3** | 4 | 8 | Good after a report; not a general chat OS. |
| A6 | Projects / Spaces (files + instructions) | Spaces / Projects, up to 50 files (Pro) | Projects + docs + instructions + setup coach | **4** | 4 | 4 | Explicitly built as Perplexity-style; coach is a plus. |
| A7 | Local / hybrid docs + web | Files + Internal Knowledge | Web / local / hybrid; image vision in loader | **4** | 4 | 4 | Hybrid is a real differentiator; home upload UX still doc-heavy. |
| A8 | Export (PDF / DOCX / MD) | Weak on Pages export; Computer Create elsewhere | PDF, Word, Markdown, logs, share link | **5** | 3 | 0 | **Better than Pages** for shippable briefs. |
| A9 | Model choice in UI | Pro: pick advanced models | Server `.env` slots only; no user picker / BYOK UI | **2** | 3 | 9 | You can route keys on VPS; not “tap Claude/GPT” like Pro. |
| A10 | Usage honesty / limits | Credits, weekly caps (complaint-prone) | No self-serve credit UX; operator-controlled | **3** | 3 | 6 | Can be *fairer* if you set caps; not productized yet. |

**Subtotal A (core):** score mass ≈ **33 / 50** raw · weighted gap ≈ **69** (A1 alone is ~29% of that gap).

### B. Product surface you may not need (but Perplexity sells)

| # | Capability | Perplexity | Hexsenses | Score | Wt | Gap | Cancel impact |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| B1 | Native iOS / Android apps | Full | Responsive web only | **1** | 3 | 12 | High if mobile is habit |
| B2 | Voice mode | Web / Mac / mobile (Pro+) | None in product | **0** | 2 | 10 | High if you voice-search |
| B3 | Comet AI browser | Free browser + tiered assistant | None | **0** | 2 | 10 | Only if you use Comet daily |
| B4 | Computer / Create (docs, sheets, apps, agents) | Pro limited; Max heavy | None (research agent ≠ Computer) | **0** | 3 | 15 | **Blocks canceling Max** |
| B5 | Image / video generation | Pro+ | Report images / scrape; no gen studio | **1** | 2 | 8 | Use external tools |
| B6 | Pages (publish articles) | Shareable Pages | Share report link / export | **2** | 1 | 3 | Low for private research |
| B7 | Memory personalization | Cross-session Memory / Brain (Max) | Project instructions; no global Brain | **2** | 2 | 6 | Projects partially substitute |
| B8 | Shopping / Instant Buy | US shopping | None | **0** | 1 | 5 | Ignore if not US shopper |
| B9 | Finance / Health verticals | Finance, Health | None | **0** | 1 | 5 | Irrelevant for research cancel |
| B10 | Learn Mode / student | Education Pro | None | **0** | 1 | 5 | Irrelevant unless student |
| B11 | Team / Enterprise admin | SCIM, seats, org files | Single-user OAuth Projects | **0** | 1 | 5 | Ignore for personal cancel |
| B12 | Always-on polish & speed | Consumer search UX | Research console UX | **2** | 3 | 9 | Friction vs “just ask” |

**Subtotal B:** most rows are **intentionally out of scope** for a research-agent product.

---

## Where Hexsenses is already ahead (keep these)

1. **Long-form report quality controls** — summary / detailed / deep / multi-agent with human plan review.  
2. **Hybrid local + web** with project docs (incl. image→vision path in the loader).  
3. **Export to PDF / DOCX / MD** as first-class.  
4. **Playbooks + setup coach** (job-to-be-done), which Perplexity Spaces don’t productize the same way.  
5. **BYOK / multi-provider on your VPS** — you own cost curve instead of Pro→Max upsell (ops skill required).  
6. **No US-only shopping lock-in** — irrelevant noise removed if your job is research.

---

## Gap ranking (what still blocks canceling Pro)

Ordered by weighted gap × “likely you use this”:

| Rank | Gap | Why it blocks cancel | Effort to close |
| --- | --- | --- | --- |
| **1** | **Instant search mode** (A1) | Perplexity’s default habit loop | Medium — new “Quick answer” path (Tavily/search + cite, &lt;15s) without full report pipeline |
| **2** | **Mobile / voice** (B1–B2) | Habit on the go | High for native; Medium for PWA + browser STT |
| **3** | **In-UI model picker** (A9) | Pro users switch models constantly | Low–Medium |
| **4** | **Follow-up as primary chat** (A5) | Thread-first vs report-first | Medium — home = chat, “Deep research” = button |
| **5** | **Computer / Create** (B4) | Only if you paid for Max / Computer | High — **do not build** to cancel Pro; use Cursor/Claude for that job |
| **6** | **Comet** (B3) | Browser sidecar | Out of scope; keep Chrome + this app |

---

## Two cancel scenarios

### Scenario 1 — “I pay Pro for research reports & Projects”

| Need | Covered? |
| --- | --- |
| Deep / multi-source reports | Yes |
| Citations + exports | Yes |
| Project files + instructions | Yes |
| Occasional follow-ups | Yes (post-report) |
| Instant daily trivia / news | **No** → use Free Perplexity or Google |

**Cancel Pro?** **Yes, with Free Perplexity as a side tool** — or fully cancel if you tolerate 2+ min for everything.  
**Fit score:** **~80%**.

### Scenario 2 — “Perplexity is my default browser search + voice + Computer”

| Need | Covered? |
| --- | --- |
| Instant answers | No |
| Voice / mobile app | No |
| Comet / Computer | No |
| Deep reports | Yes (overkill for most queries) |

**Cancel Pro/Max?** **No** — Hexsenses is a **research workstation**, not a search OS.  
**Fit score:** **~35–45%**.

---

## Scoreboard (personal cancel decision)

Assume weights from section A + selected B (mobile, voice, Computer, polish):

| Bundle | Approx coverage | Meaning |
| --- | --- | --- |
| Deep-research job only (A3–A8) | **~82%** | Safe to lean on Hexsenses |
| Pro “daily driver” (A + B1/B2/B12) | **~55%** | Not a full cancel yet |
| Max driver (+ B3/B4/B7) | **~38%** | Stay on Max or split tools |

```
Perplexity Pro daily-driver coverage (Hexsenses)
████████████░░░░░░░░  ~55%

Deep-report / Projects coverage
████████████████░░░░  ~82%
```

---

## Minimum build list to raise “cancel Pro” to ~75%+

Do **only** these (aligned with original purpose; ignore HK niche GTM for now):

1. **Quick Answer mode** — search bar → cited answer in &lt;15s; “Run full research” as secondary CTA.  
2. **Home = conversation** — follow-ups without requiring a finished report first (or auto-light-research).  
3. **Model selector** in Settings (map to existing FAST/SMART slots).  
4. **Mobile-usable PWA** + optional browser voice input (not a native app).  
5. **Honest usage card** — so you trust Hexsenses more than Pro’s credit surprise.

**Explicitly skip for cancel-Pro:** Comet clone, Shopping, Finance, Health, Learn Mode, Stripe Max tier, in-app video gen.

---

## Cost note (why cancel still matters)

| Tool | Ballpark |
| --- | --- |
| Perplexity Pro | ~US$17–20 / mo |
| Perplexity Max | ~US$167–200 / mo |
| Hexsenses | Your LLM + search API spend on VPS (variable; often &lt; Pro if usage is report-bursty) |

Canceling Pro saves ~US$200–240/yr **if** Quick Answer closes the daily habit gap; otherwise you may keep Free/Pro and still use Hexsenses for deep runs (best of both).

---

## Suggested next step (back on purpose)

1. Decide which scenario you are: **1 (reports)** or **2 (daily search OS)**.  
2. If scenario 1 → cancel Pro after one week of only Hexsenses for deep work; keep Free if needed.  
3. If scenario 2 → build **Quick Answer** before talking about niches, comedy, or GTM again.

**Companion docs:** `hexsenses-first-100-plan.md`, `hexsenses-go-to-market.md`.
