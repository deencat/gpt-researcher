# Hexsenses — path to first US$100 (gaps, proof, measurements)

**Brand:** Hexsenses (`hexsenses.com`)  
**Live app today:** [research.sixlines.io](https://research.sixlines.io) (migrate off `.io` before Apr 2027)  
**Goal of this doc:** close the gaps between “working research tool” and **first US$100 from a real outsider payment**, with a **tangible example business** so buyers see *how* to use it.

Related: [hexsenses-go-to-market.md](./hexsenses-go-to-market.md) (offers toward ~US$10k/mo profit).

---

## 1. North star for this phase

| Metric | Target | Why it counts |
|--------|--------|----------------|
| **First revenue** | **≥ US$100** from someone who is not you | Proof people will pay |
| **Proof artifact** | 1 public case study (before → after) | Shows *how* to use the tool |
| **Repeatable run** | Same Project can produce week-2 output without rebuilding | Product is sticky, not a demo |

**Done when:** money received (PayMe / FPS / Stripe / invoice) **and** a short write-up others can copy.

**Not done when:** more features ship but nobody paid and nobody copied a workflow.

---

## 2. Two workstreams (both required)

```
┌─────────────────────────────┐     ┌──────────────────────────────────┐
│ A. TOOL                     │     │ B. EXAMPLE BUSINESS (proof)      │
│ Make Hexsenses better than  │────▶│ Use Hexsenses on a real channel  │
│ the pain that drives people │     │ so strangers see the playbook    │
│ off Perplexity              │     │                                  │
└─────────────────────────────┘     └──────────────────────────────────┘
                 │                                  │
                 └──────────▶ First US$100 ◀────────┘
```

- **A alone** = nice product, $0 (people don’t know what to do with it).  
- **B alone** = you get results, still look like “just another freelancer.”  
- **A + B** = product + proof → someone pays for access or a retainer pack.

---

## 3. Study Perplexity → gaps → our improvement plan

### 3.1 What Perplexity sells (2026 snapshot)

| Plan | Ballpark | Promise |
|------|----------|---------|
| Free | $0 | Capped everyday search |
| Pro | ~US$20/mo (~US$200/yr) | Daily research, Projects, uploads, light media |
| Max | ~US$200/mo | Heavy Computer / deep research limits |
| Enterprise | higher / seat | Team admin |

They also have **Projects** (workspaces: threads, files, custom instructions) — same *category* as ours.

### 3.2 Real customer pain (why people like you look for a way out)

These show up repeatedly in public reviews / complaints (not legal claims — market signal):

| Pain | What it feels like | Hexsenses opportunity |
|------|--------------------|------------------------|
| **Limit / credit surprise** | Mid-task “weekly limit,” vague credits, Pro feels like bait for Max | Clear caps **before** run; no silent credit drain |
| **Support black hole** | Bots, cancelled by mistake, no human | Founder chat for first customers; 24h reply promise |
| **Price jump** | Pro → Max (~10×) for “serious” depth | One honest mid tier (~US$100 Max-equivalent) + retainers |
| **Projects without a job** | Folders exist; still unclear *what to research for a business outcome* | Setup coach + **starter prompts tied to a real playbook** |
| **Generic answers** | Fast Q&A, weak “use this on my niche channel this week” | Project instructions + docs + exportable briefs |

**Rule for conversion:** every Perplexity refugee should feel *less* surprise, *more* clarity, and *a finished asset* they can ship — not another chat dump.

### 3.3 Capability gap table (today vs need-for-first-$100)

| Area | Perplexity | Hexsenses now | Gap for first $100 | Priority |
|------|------------|---------------|--------------------|----------|
| Web research + citations | Strong | Strong enough | Keep quality stable | P0 maintain |
| Projects (files + instructions) | Mature UX | Live (docs, instructions, coach) | Polish coach → published “playbook” templates | **P0** |
| Multi-language research | Good | Possible via prompts | Encode EN / 普通话 / 粤语 / 台語 as project defaults | **P0** |
| Usage honesty | Weak (complaints) | No self-serve billing yet | Manual fair-use; write limits in invite | **P0** |
| Billing / self-serve | Full | None | **Manual pay is OK** until $100 | P2 |
| Public brand | Strong | `sixlines.io` → Hexsenses | Landing on hexsenses.com (even 1 page) | P1 |
| Example business playbook | Thin | Missing as product | **Salon comedy shorts case** (below) | **P0** |
| Video generation in-app | Yes (limited) | Out of scope | Use Flova/Kling outside; research briefs inside | P3 later |
| Team seats | Yes | No | Not needed for $100 | Later |

### 3.4 Product improvement plan (only what unblocks $100)

**Must ship / lock before selling**

1. **Playbook Project template** — “Comedy shorts research pack” with coach answers prefilled (languages, formats, materials, constraints).  
2. **Starter research prompts** that output a *shippable* brief (title options, hook, script outline, sources) — not an essay.  
3. **Honest usage card** — on invite: “You get N deep runs / week; we tell you before you burn them.”  
4. **Export / share** — markdown or PDF brief a client can forward.  
5. **One-page Hexsenses landing** — what it is, who it’s for, link to proof case, how to pay manually.

**Explicitly do *not* build yet**

- In-app Stripe, credit ledger, Max $200 clone, Flova clone, MLM partner portal.

---

## 4. Tangible example business (so others know how to use it)

### 4.1 The example (yours — public proof)

**Business:** wife’s beauty salon → **funny / marketing short-form video channel**  
**Languages:** English + Mainland Mandarin + HK Cantonese + Taiwan Mandarin  
**Tool role:** Hexsenses Project = *source of data & creative angles*; video tools you already pay for = *render*

| Week | Use Hexsenses for | Ship outside the tool | Measurement |
|------|-------------------|------------------------|-------------|
| 0 | Create Project + coach fill (goal, languages, formats) | — | Project has instructions + 3 starter prompts |
| 1 | Run 2 researches: trending funny beauty angles; competitor hooks | 2 scripts → 2 shorts published | Views, saves, comments |
| 2 | Research “what worked / what flopped” + next hooks | 2 more shorts | Views vs week 1; time-to-script |
| 3 | Compile “playbook PDF” from Project history | Post case study on hexsenses.com / social | Inquiries or first paid yes |

### 4.2 What “good” looks like (numbers you can show)

Pick **one** primary channel (e.g. YouTube Shorts *or* IG Reels *or* Douyin) and stick to it for 4 weeks.

| KPI | Baseline (week 0) | Target by first $100 |
|-----|-------------------|----------------------|
| Shorts published | 0 from this system | ≥ **8** |
| Time: idea → shootable script | Guess / ad-hoc | **≤ 45 min** with Project |
| Avg views (or saves) | Current channel avg | **≥ 1.5×** prior 4-week avg *or* clear learning notes if not |
| Reusable Project assets | 0 | ≥ **1** language pack + ≥ **10** hooks bank |
| External interest | 0 | ≥ **3** DMs / “how did you do that?” *or* 1 paid offer |

If views don’t jump, the case study still works if you show **time saved + repeatable process** — honesty beats fake virality.

### 4.3 Playbook others copy (the product of the example)

Publish a short page: **“How we use Hexsenses for multilingual beauty comedy shorts.”**

Steps outsiders follow:

1. Duplicate the Project template (or recreate via coach).  
2. Upload 3–5 competitor / brand docs if they have them.  
3. Run prompt A → hooks; prompt B → script; prompt C → weekly review.  
4. Shoot with their own tools.  
5. Log results back into the Project.

**This is the conversion asset** for Perplexity users: same “research,” but tied to a job-to-be-done.

---

## 5. Path to first US$100 (offers)

Any **one** of these counts:

| Path | Offer | Price | Buyer | Fulfillment |
|------|--------|-------|-------|-------------|
| **A** | 1 month Max / Pro access (manual) | US$20–100 | Frustrated Perplexity user | Invite to app + fair-use note |
| **B** | Research pack (4 briefs) | US$100–150 | Creator / salon marketer | You run Project for them |
| **C** | Video pack deposit | US$100 toward US$300–800 pack | Salon / local biz | Research in Hexsenses + video via existing tools |

**Recommended first:** **B or C** (faster to US$100 than waiting for self-serve subscribers). Use Path A once the playbook page exists.

Payment: FPS / PayMe / PayPal invoice — no Stripe required for first dollar.

---

## 6. Gap checklist until first US$100

### Business / proof gaps

- [ ] Example Project live on Hexsenses (comedy shorts / salon)  
- [ ] ≥ 4 shorts shipped from that Project (aim 8)  
- [ ] Metrics logged (time-to-script, publish dates, views/saves)  
- [ ] 1 public case write-up with steps + numbers  
- [ ] Soft ask: 5 people who hate Perplexity limits see the case  

### Product gaps

- [ ] Playbook template + coach defaults for this niche  
- [ ] Starter prompts output **briefs**, not essays  
- [ ] Fair-use / limit text for invitees  
- [ ] Export shareable brief  
- [ ] Minimal hexsenses.com page (brand + proof + contact/pay)  

### Brand / ops gaps

- [ ] Hexsenses logo lockup (concept A + wordmark) on landing  
- [ ] Plan domain cutover `research.sixlines.io` → Hexsenses host (before Apr 2027)  
- [ ] Manual invoice template ready  

### Explicit non-gaps (ignore until after $100)

- [ ] Full billing engine  
- [ ] In-app video studio  
- [ ] Partner MLM-style tree  
- [ ] Matching every Perplexity feature  

---

## 7. Weekly operating rhythm (until $100)

| Day | Tool work (≤50%) | Example business (≥50%) |
|-----|------------------|-------------------------|
| Mon | Fix one friction in Projects / coach | Run research → 2 hooks |
| Wed | Improve one prompt / export | Publish 1 short |
| Fri | Update gap checklist | Log KPIs; DM 2 potential buyers with case |

**Stop rule:** if a feature idea does not move a checkbox in §6, park it.

---

## 8. Definition of “first US$100” success

1. **Cash:** ≥ US$100 received from an external payer.  
2. **Cause:** They bought because of **tool access** and/or **example playbook / pack**.  
3. **Learn:** One page note — what they wanted, what almost blocked them, what to fix next for second $100.

After that, return to [hexsenses-go-to-market.md](./hexsenses-go-to-market.md) Stage 1 (5 paying customers).

---

## 9. One-sentence strategy

**Make Hexsenses the research home for people burned by Perplexity’s limits — and prove it by running a real multilingual comedy-shorts business in public so buyers copy the method, not just the chat UI.**
