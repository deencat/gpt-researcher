# AI Automation Niches Research — Hong Kong (late 2026)

Local twin of `ai-automation-niches-research-2026.md`. Same eight niches; rewritten for Hong Kong operators.

**What changes vs the global brief**

| Dimension | Global (US/generic) | Hong Kong |
| --- | --- | --- |
| Primary channel | PSTN + SMS | **WhatsApp Business API** first; phone second |
| Language | English | **Cantonese + English code-switch**; Traditional Chinese UI/docs |
| Field CRM | ServiceTitan / Jobber / HCP | Local WhatsApp ops tools, Excel, Mizar-class FSM |
| Clinic stack | Dentrix / Weave | DentoEase / Occlus / ClinicONE / HelloClinic + **eHealth** |
| Property stack | AppFolio / DoorLoop | Estate office WhatsApp + Butler / NineSmart / MRI |
| Ledger | QBO / Xero US | **Xero HK**, **ABSS/MYOB**, AutoCount; HKD + bank FPS |
| Compliance | SOC 2 / HIPAA | **PDPO**, ISO 27001, **Critical Infrastructure (CS) Ordinance**, GL20 |
| Legal | Harvey / Clio | Lexis+ Protégé HK, Lawway on-prem, AI Paralegal, bilingual docs |
| RFP | Loopio security questionnaires | Same + **gov / corporate tenders** (bilingual packs) |
| Pricing | USD | **HKD**; Meta WA message fees on top of platform |

For each niche below:

1. **Competitors** (HK-local + regional + global present in HK)
2. **HK context** (language, regs, platforms)
3. **Minimal MVP stack** (WhatsApp-first)
4. **Interview script** (10 questions, HK wording)
5. **Sub-scenarios** (pain → who pays → what to build → how to validate)

Price figures are public list or vendor-stated ranges as of late 2026. Confirm before budgeting. Meta WhatsApp rates change often — re-check the HK rate card.

---

## How to use this doc

- Pick a niche, then pick **one** sub-scenario as the wedge.
- Run interviews in Cantonese or English (match the owner). Ask for dollars and hours, not opinions.
- Prefer **official WhatsApp Business API** (BSP) over unofficial “scan QR / linked phone” sessions — clinics and PMs care about ban risk and PDPO records.
- If five of ten buyers can name a number they lose today, you have a market.

---

## Cross-cutting HK constraints

1. **PDPO** — personal data (name, phone, address, medical, tenancy) needs purpose limitation, retention rules, and a privacy notice. Direct marketing needs consent; transactional booking/reminders are usually fine.
2. **UEMO** — commercial electronic messages (promos on WhatsApp/SMS/email) need consent / unsubscribe. Appointment utility templates ≠ marketing blasts.
3. **Cantonese voice notes** — HK customers send 語音. STT that fails on Hong Kong Cantonese kills trust; budget for a model that handles code-switch (`幫我 book 聽日`).
4. **District / estate addressing** — use HK districts + estate/block/flat, not US zip. Escalation lists by Kowloon / HK Island / NT / outlying.
5. **Human gate** — never auto-dispatch gas/flood/lift entrapment; never auto-post ledger; never auto-attest PDPO/ISO; never auto-send security/legal tender answers; never give clinical advice.

---

## 1. Home-services after-hours intake

**Tuesday problem:** Night WhatsApps and missed calls lose AC / plumbing / electrical jobs; the shop that replies in Cantonese wins.

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| PingHand | WhatsApp AI receptionist for HK SMEs; Cantonese/Mandarin/English; booking + voice notes | Free trial; Business plan ~HK$1,199/mo (multi-number) |
| CoV | WhatsApp AI ops for HK service businesses (AC, cleaning, repair): enquiry → quote → invoice | Quote / pilot; HK-focused workflows |
| Cenvoi | Native Cantonese AI voice + WhatsApp + web | ~HK$688/mo + ~HK$8/answered call; setup from ~HK$1,800/channel |
| Novelte Engage | Multi-channel AI receptionist (WA / phone / web); Cantonese code-switch | Quote; HK Science Park vendor |
| Sage (HK) | Done-for-you WA booking agent (EN + Yue) | Starter ~HK$1,500/mo + setup; Growth ~HK$2,800/mo |
| Virtual Receptionist HK / similar AI phone desks | AI phone answering with booking | From ~HK$1,799/mo (600 voice min) class |
| Global overlays (ServiceTitan / Jobber / Smith.ai) | Rare as system-of-record in HK SME trades | Usually not adopted; treat as adjacent only |

### HK context

- Channel: **WhatsApp >> phone >> Instagram DM**. SMS is weak.
- Language: HK Cantonese with English loanwords; Mandarin for some Mainland clients.
- Trades: 冷氣清洗 / 維修, plumbing, electrical, renovation — often sole props + WhatsApp Business app (not API).
- After-hours: typhoon / black rain / water leakage emergencies matter culturally and operationally.

### Minimal MVP stack

Official WhatsApp Business API via a BSP (or Twilio/MessageBird WA) → LLM agent (estate/block, issue, urgency, tomorrow window) in Yue/EN → write Google Calendar or Google Sheet job board → WhatsApp confirm → if keywords (漏水 / 冇電 / 煤氣 / lift) → WhatsApp + call on-call tech. Host: Vercel/Fly + Postgres in a region the buyer accepts (disclose PDPO transfer). Skip native continuous listen for v1; optional Cantonese voice-note STT.

### Interview script (10)

1. 平時夜晚同週末，WhatsApp 同電話大概有幾多查詢一星期？
2. 而家有幾多 % 係第二朝先覆？
3. 如果即刻覆，一個月大概可以多接幾多單？平均一單幾錢？
4. 緊急單（漏水、冇電、煤氣）而家點 call 師傅？
5. 客人多數用廣東話、英文定普通話？有冇語音訊息？
6. 而家用緊咩記單？（WhatsApp、Excel、Mizar、其他）
7. 試過 AI 接待 / 人工 call centre 未？邊度唔掂？
8. 邊啲單絕對唔可以 AI 自動 book？
9. 你寧願按成功預約、按對話，定月費？預算大概幾多 HKD？
10. 如果一個月幫你救返兩單，值唔值付呢個數？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| After-hours WA booking | Night chats die until morning | Owner | Yue/EN WA agent books tomorrow | Missed overnight chats × 2 weeks |
| Emergency escalate | Leak / no power / gas must page human | Owner | Keyword escalate + on-call WA/call | Real emergency keyword list test |
| Daytime overflow | Boss on job; leads go cold | Owner | AI first reply + human takeover | Reply-within-5-min rate |
| Appointment confirm | No-shows waste trips across districts | Owner | WA utility confirm day-before | No-show % |
| Post-job Google/OpenRice ask | Happy customers silent | Owner | Auto WA review link after job | New reviews / month |

**First interview target:** 冷氣 / plumbing owners with 3–20 techs who live in WhatsApp and hate missed night leads.

---

## 2. Dental / med spa front office

**Tuesday problem:** No-shows and empty chairs while 姑娘 drown in WhatsApp confirms, scaling recalls, and intake — under PDPO and (for medical) eHealth expectations.

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| DentoEase | HK dental clinic PMS; auto confirm/remind, scaling recall, WA treatment plans | Quote (HK dental-specific) |
| Occlus | Dental PMS + WA booking/recalls/deposits; Cantonese/EN/ZH; official WA API only | Quote |
| ClinicONE / DentistONE | HK clinic CMS; dental module; WA follow-ups; eHRSS-approved vendor class | From ~HK$699–899/doctor/mo (plan-dependent) |
| HelloClinic | HK AI clinic management; WA inbox + reminders | ~HK$750/mo or ~HK$7,500/yr per doctor |
| Weave / Solutionreach / NexHealth | US patient-comms leaders | Weak HK footprint; rarely the local default |
| Generic WA AI (PingHand / Sage / Cenvoi) | Booking without deep dental charting | See niche 1 pricing |

### HK context

- Channel: WhatsApp confirms dominate; SMS secondary.
- Language: Cantonese + English; Traditional Chinese forms.
- Regs: **PDPO** for patient data; medical records retention; no clinical advice from AI. eHealth / eHRSS relevant for medical clinics.
- Med spa / aesthetic: strong WA deposit culture; “patch test / aftercare” FAQs.

### Minimal MVP stack

Start without full PMS write-back: daily export / CSV of tomorrow’s chairs → WhatsApp Business API utility templates (confirm yes/no) → reschedule handoff to clinic queue → overdue scaling list from spreadsheet → post-visit review WA. Add DentoEase/Occlus/ClinicONE sync after 3 paying clinics. After-hours new-patient consult booking is phase 2. **No diagnosis, no drug advice.**

### Interview script (10)

1. 過去 90 日 no-show 率大概幾多？
2. 一星期有幾多椅位係取消／冇嚟？
3. 而家邊個做確認？每日花幾耐喺 WhatsApp？
4. 洗牙 recall list 有幾遠？邊個跟？
5. 夜晚／週末有冇人想 book 新症但冇人覆？
6. 用緊邊套診所系統（DentoEase、Occlus、ClinicONE、Excel…）？
7. 試過 AI / 自動提醒未？病人有冇投訴？
8. PDPO／病人私隱有冇硬性規定（同意書、保留期）？
9. AI 絕對唔可以答咩（臨床、價錢承諾、保險）？
10. 一個「梗係值得」嘅月費大概係幾多 HKD？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| WA appointment confirm | No-shows empty chairs | Manager / owner | Utility template yes/no | No-show % |
| Scaling / hygiene recall | Idle chairs | Owner | Overdue-list WA | Booked recalls |
| After-hours new-patient book | Night leads die | Owner | Book consult only | Evening bookings created |
| Pre-visit forms (TC/EN) | Clipboard chaos | Manager | Form link before visit | Incomplete forms at check-in |
| Review + reactivation | Quiet patients leave | Owner | Review + win-back WA | Reviews + rebooks |

**First interview target:** Clinic managers who can name no-show % and already spam WhatsApp manually.

---

## 3. Property-management maintenance triage

**Tuesday problem:** Residents WhatsApp the management office; urgency is guessed; contractors and owners stay in the dark — across estates, not US “units in AppFolio.”

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| Butler (BMS) | AI CRM: WA → ticket with category, urgency, assignment (HK Smart LAB listed) | Quote / enterprise SaaS |
| NineSmart | HK smart property: work orders, resident app, AI chatbot, e-billing | Subscription modules; quote |
| MyPropty | HK landlord PM: tenancy, rent, maintenance | Quote / SME landlord focus |
| MRI Software (HK) | Enterprise property / leasing / ops | Enterprise quote |
| FM Plus (EBSL) | Mobile FM: work orders, patrol, scheduled maintenance | Quote |
| AppFolio / DoorLoop / EliseAI | US PM AI leaders | Rare as default for HK estates |
| Novelte Flow (demo flows) | WA tenant leak → work order example | Quote |

### HK context

- Channel: **WhatsApp to management office** is the real portal; paper forms still exist in some estates.
- Language: Cantonese residents; English for some landlords / corporates; Traditional Chinese notices.
- Urgency: water leakage into downstairs flat, lift entrapment, no electricity, gas — liability and insurance sensitive.
- Buyers: property management companies (嘉里、新鴻基旗下管理處-class) and mid-size estate offices; also small landlord portfolios.

### Minimal MVP stack

One official WA Business number for the estate → classify urgency (red/yellow/green) against written house rules → ticket in Airtable/Notion with photo → WhatsApp/SMS manager for reds only → vendor WA with trade + district. Integrate Butler/NineSmart/MRI later. **Never auto-dispatch reds.**

### Interview script (10)

1. 管理處一星期大概收幾多維修要求？管幾多個單位／座數？
2. 而家經邊啲渠道（WhatsApp、電話、App、紙本、email）？
3. 真正緊急大概佔幾多 %？
4. 上次漏水／死火／困電梯——邊個幾耐收到？
5. 用緊邊套物業／工單系統？定係主要靠 WhatsApp？
6. 常用判頭／承辦商名單有幾長？點分區？
7. 最痛係收單慢、派錯人，定業主追進度？
8. 睇過 Butler、NineSmart、MRI AI / chatbot 未？
9. 工具日常邊個用（客戶服務、技術員、物業經理）？
10. 寧願按單位、按 ticket，定管理處月費？預算單位 HKD？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| Multi-channel → one WA inbox | Chats scatter across staff phones | Ops lead | Shared WA Business inbox + tickets | Time-to-ticket |
| Urgency triage | Wrong guess on emergencies | Ops | Policy red/yellow/green | False-emergency rate |
| Vendor dispatch | Wrong trade / wrong district | Ops | Preferred vendor by trade + district | First-time-fix rate |
| Owner / committee status | Owners nag | PM company | Auto status WA | Owner callback volume |
| After-hours red page | Night flood / lift | On-call | Escalate reds only | Response minutes |

**First interview target:** Estate ops leads drowning in staff WhatsApp for 1–20 buildings.

---

## 4. AP / invoice matching

**Tuesday problem:** Bookkeepers burn hours matching bank lines (HSBC/Hang Seng/BOC FPS exports) to Chinese + English PDF invoices.

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| Xero (HK) AP / AI bill capture | Native draft bills from upload/email | Xero subscription tiers (HK) |
| Datamolino | OCR/AI bills + bank statements → Xero (HK App Store) | Per-doc / plan; quote |
| Tipalti | Global AP + Xero sync | From ~US$99/mo + fees (enterprise often higher) |
| SmartBusiness + ABSS/MYOB | HK AI OCR invoices/statements → ABSS | Product listing ~HK$8,868 class (confirm current) |
| Tofu + AutoCount | AI line items → AutoCount Cloud/Desktop; Chinese names preserved | Quote / usage |
| Dext / Hubdoc | Bookkeeper capture (regional) | Per-client; varies |
| Ramp / BILL / Melio | US bill-pay leaders | Limited HK bank rails; treat as weak local fit |

### HK context

- Ledgers: **Xero, ABSS (MYOB), AutoCount**, some Sage; QBO less dominant than US.
- Docs: Traditional Chinese supplier names, bilingual invoices, company chops on PDFs.
- Payments: FPS, local CHATS, cheque still exists; FX for cross-border CN/SEA suppliers.
- IRD / audit trail: keep original invoice image attached.

### Minimal MVP stack

Upload zone: bank CSV/PDF + invoice PDFs → extract amount/date/vendor (ZH+EN) → propose matches with confidence → Accept / Reject / Split → export to Xero CSV or ABSS import. **No auto-post.** First logo: one HK bookkeeping firm with 5–10 SME clients. Stack: Next.js + Postgres + vision LLM OCR + review queue. Store data with PDPO-aware retention.

### Interview script (10)

1. 你哋一個月 reconcile 幾多盤客戶帳？
2. 每盤花幾多鐘做 invoice ↔ bank matching？
3. 錯配之後點解？有冇試過 double pay？
4. 客戶最多用 Xero、ABSS、AutoCount，定其他？
5. 而家有冇用 Datamolino、Dext、Xero AI bill capture？
6. Invoice 多數經 email、WhatsApp PDF，定紙 scan？
7. 你信唔信 auto-post，定只要 auto-propose 你撳確認？
8. 最頭痛 exception（部分付款、銀行費、人民幣／美金）？
9. 如果 matching 時間減半，一個月值幾多 HKD？
10. 想要轉售畀客戶嘅 SaaS，定事務所內部工具？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| Invoice ↔ bank match | Hours of eyeballing ZH+EN PDFs | Bookkeeper / firm | Propose matches + confidence | Hours saved per client |
| Missing invoice chase | Paid via FPS, no PDF | Firm | WA/email vendor for invoice | Open exceptions aging |
| GL coding suggestions | Wrong codes / tax codes | Controller | Suggest from history | Edit rate after suggest |
| Approval routing | Bills stall in WhatsApp/email | Finance lead | Route by amount/vendor | Days-to-approve |
| Duplicate detection | Double-pay risk | Firm | Flag near-duplicates | Dupes caught before pay |

**First interview target:** Causeway Bay / Kwun Tong bookkeeping firm owners with 10+ SME books.

---

## 5. Compliance evidence staging

**Tuesday problem:** Audit scramble for ISO 27001 / PDPO / Critical Infrastructure — screenshots into folders; evidence goes stale; US GRC tools ignore HK control sets.

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| ComplyNexus | AI GRC; ISO + **PDPO, GL20, CI (CS) Ordinance**; local hosting option | Quote (gov/enterprise) |
| RISK.HK / Doctor A Security | HK continuous risk + compliance automation; audit-ready evidence | Quote / CaaS |
| Vanta / Drata / Secureframe | Global continuous compliance | ~US$12–28k/yr class; weak PDPO/CI mapping out of box |
| Sprinto / Scrut / Thoropass | Mid-market GRC | Quote |
| Big-4 / local consultancy packs | Manual evidence + Excel | Day rates; not product |

### HK context

- Frameworks: **ISO 27001**, SOC 2 (for US buyers), **PDPO**, HKMA/SFC circulars for finance, **Critical Infrastructure (Computer-system) Ordinance**, PCPD guidance.
- Data residency: some buyers demand HK/on-prem hosting — selling point vs US SaaS.
- Questionnaires: enterprise customers still send SIG/CAIQ-style packs in EN (+ some ZH).

### Minimal MVP stack

Don’t replace Vanta day one. Wedge: one control family (access reviews or PDPO inventory) → connect Google Workspace / M365 + GitHub + cloud IAM read APIs → weekly snapshot into control folders → Slack/Teams digest of diffs → human sign-off checklist. Sell as “evidence packer” beside ComplyNexus/RISK.HK or to teams stuck in SharePoint before buying GRC. **Never auto-attest.**

### Interview script (10)

1. 今年追邊啲 framework（ISO 27001、SOC 2、PDPO、CI Ordinance）？
2. 下一次 audit / surveillance 係幾時？
3. 上次 evidence scramble 花咗幾多工時？邊個做？
4. 真相喺邊（M365、Google、AWS/Azure、Okta、HRIS、Jira）？
5. 而家用 Vanta/Drata、ComplyNexus、RISK.HK，定 Excel/SharePoint？
6. 即使買咗 GRC，仲有邊度最人手？
7. 邊個必須簽署 attestation？會唔會俾 software 代簽？
8. Security questionnaire 係咪第二份全職？
9. 合規工具 + audit fee 一年預算幾多 HKD？
10. 如果一個 control family 成日 green，你肯付幾多？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| Continuous evidence pack | Audit scramble | Compliance lead | Weekly snapshots by control | Hours before next audit |
| Access review packs | User lists go stale | Security | Export users/roles + diffs | Review cycle time |
| PDPO / vendor evidence | Third-party docs pile up | DPO / security | Stage docs by control | Questionnaire turnaround |
| Control gap alerts | Drift mid-quarter | CISO | Slack/Teams when control breaks | Mean time to notice |
| Audit-room export | Auditor wants zip tonight | Compliance | One-click pack | Prep days cut |

**First interview target:** First-time ISO 27001 / PDPO-ready SaaS or fintech (30–500 people) mid-scramble in HK / Cyberport / Science Park.

---

## 6. Small-firm legal intake / contracts

**Tuesday problem:** Messy WhatsApp/email intake and manual playbook redlines burn associate hours; Harvey-class tools have enterprise floors and weak HK bilingual workflows.

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| Lexis+ with Protégé (HK) | Research, drafting, Vault contract review; CaseBase HK | Custom quote |
| Lawway (Blockway) | On-prem AI legal workflows; playbook review; lawyer gate | Hardware + licence quote; ~≤15-lawyer focus |
| AI Paralegal (hkparalegal.ai) | HK templates, bilingual docs, contract risk, Labour Dept timelines | Quote |
| Lawzana Flow | Small-firm PM + AI playbook reviews | SaaS; quote / plan |
| Harvey / Legora / Spellbook | Global legal AI | High seat mins; US/EU skew |
| Clio Duo | PM AI; not deep HK ordinance grounding | ~US$49–59/user/mo on Clio |

### HK context

- Language: bilingual ENG + Traditional Chinese contracts; stamp duty calculations matter for some matter types.
- Matter types: NDA, employment, tenancy, SME commercial — plus PI / Labour Tribunal adjacent for some firms.
- Privacy: many firms refuse US cloud for client docs → **on-prem / HK hosting** is a wedge (Lawway-class positioning).
- Practice: small solicitor firms + chambers; WhatsApp with clients is common (PDPO caution).

### Minimal MVP stack

Two thin wedges: (A) intake form / WA transcript → structured matter memo PDF (EN or TC); (B) upload NDA/employment → diff against 15-clause firm playbook → redline DOCX + one-page partner memo. Partner approve gate mandatory. Stack: Next.js + private model endpoint or HK/region VPC + playbook store. Market against Harvey seat floors for 2–15 lawyer shops.

### Interview script (10)

1. 一個月大約開幾多新 matter？邊個做 intake？
2. 由第一封 email／WhatsApp 到可用 summary 要幾耐？
3. 每星期最常 redline 邊類約（NDA、僱傭、租約、MSA）？
4. Playbook 係寫低咗，定喺 partner 腦入面？
5. 用緊邊套 PM（Clio、本地系統、Excel）？
6. 試過 Lexis+ Protégé、Harvey、ChatGPT、Lawway 未？
7. 客戶文件可唔可以上 cloud？要唔要香港／on-prem？
8. 出文件前係咪一定要 partner approve？
9. Associate 一小時 charge 幾多 HKD？
10. 寧願按 seat，定事務所 flat fee（intake + playbook）？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| Client intake memo | Messy WA/email | Partner | Structured matter summary | Hours to first memo |
| NDA playbook redline | Same clauses weekly | Partner | Mark deviations + suggest | Partner edit rate |
| Employment / tenancy playbook | Higher stakes, bilingual | Partner | Same engine, harder playbook | Cycle days |
| Deadline / conflict checklist | Missed dates | Firm | Checklist from matter type | Near-misses caught |
| Client update drafts | Status emails eat time | Firm | Draft from matter notes | Send-ready edit count |

**First interview target:** Transactional partners at 2–20 solicitor firms who bill associates by the hour and hate Harvey’s minimums.

---

## 7. Trades dispatch / estimating

**Tuesday problem:** Quotes go out the next night via WhatsApp; leads go cold; dispatch is tribal knowledge in group chats — AC / renovation / electrical crews.

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| CoV | WA enquiry → quote → invoice for HK AC / home repair | Quote / pilot |
| Mizar | HK field service: jobs, photos, quotes, invoices, WA/WeChat chat | Tiered Standard→Enterprise; quote |
| VentureTech 維修師傅系統 | Visits, quotes, payments + WA assistant | Promo ~HK$298–458/mo class |
| WorkDocket | Quote / invoice / progress for HK SMEs; one-tap WA | Solo ~HK$800/yr; Standard ~HK$3,650/yr |
| Baal trade systems | Custom HVAC/plumbing FSM for Asia | Custom quote |
| ServiceTitan / Jobber / Housecall Pro | US FSM giants | Rare default for HK SME crews |
| PingHand / Cenvoi / Sage | Front-door AI; light estimating | See niche 1 |

### HK context

- Jobs: 冷氣清洗/維修, electrical, plumbing, renovation, waterproofing — photo-heavy, estate access (大門密碼 / 管理處).
- Price books: often WhatsApp-forwarded Excel; “套餐價” culture.
- Speed-to-lead: Google / Facebook / OpenRice / referral → WhatsApp; after 10pm replies win.
- District travel time (cross-harbour) matters more than US zip skill tags.

### Minimal MVP stack

Don’t rebuild Mizar. Wedge: photo + job type → draft estimate lines from shop price book (Google Sheet) → WhatsApp quote PDF → on accept, create job row (Sheet/Mizar/WorkDocket via Zapier). Optional: inbound WA → suggest tech by district + skill. Target 3–15 van shops not ready for enterprise FSM.

### Interview script (10)

1. 一星期出幾多個報價？成交率大概幾多？
2. 由睇場／收相到出報價要幾耐？
3. Price book 而家喺邊（Excel、腦、舊報價）？
4. 每日開邊套系統（Mizar、WorkDocket、Excel、淨係 WhatsApp）？
5. 新客從邊嚟（Google、FB、轉介、管理處）？
6. 夜晚 10 點嚟嘅 WhatsApp，你幾快覆？
7. 邊個派工？兩個緊急單一齊嚟會點？
8. 睇過 ServiceTitan / Jobber 未？係咪因為貴／唔合香港？
9. AI 自動出價會唔會驚報錯價／責任？
10. 如果當日出到價，一個月可以多幾多單？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| Same-day estimate from photos | Quotes next night | Owner | Price book + photos → WA quote | Quote lag + close rate |
| Speed-to-lead | Night WA leads die | Owner | Instant WA first reply | Contact-within-5-min |
| Tech assignment | Wrong district / skill | Dispatcher | Suggest by district + skill + load | Re-dispatch rate |
| Open-estimate follow-up | Forgotten quotes | Owner | WA drip until yes/no | Rescued revenue |
| Maintenance plan attach | One-off-only customers | Owner | Offer 保養 plan after job | Plan attach rate |

**First interview target:** AC / renovation owners with 5–30 workers still quoting from Excel the next night.

---

## 8. B2B RFP / proposal drafting

**Tuesday problem:** Security questionnaires and bilingual corporate/gov tenders burn SE days; teams decline bids for bandwidth; US tools ignore Traditional Chinese packs.

### Competitors

| Name | What they are | Price signal |
| --- | --- | --- |
| Loopio | Answer library + AI for RFPs / SQs | ~US$12–59k/yr class (median ~US$24k) |
| Responsive (ex-RFPIO) | Enterprise response platform | ~US$6–40k/yr class |
| AutogenAI | Narrative bid / proposal AI | Often US$30k+/yr class |
| Nexify Secure AI Quotation Review (Smart LAB) | On-prem bilingual tender completeness / compliance check | Quote (NVIDIA on-prem workstation class) |
| Vanta/Drata questionnaire modules | Security questionnaires only | Module ~US$10–16k/yr class |
| AutoRFP.ai / RFP.ai-class | AI-native responders | Some ~US$899+/mo or lower EU tiers |
| Big-4 / bid consultancies | Human-heavy tender writing | Day rates |

### HK context

- Buyers: SaaS selling to banks/insurers, IT vendors bidding **gov / semi-gov / MTR / hospital** tenders, professional services.
- Language: bilingual EN + Traditional Chinese tender packs; mixed-language annexes.
- Sensitivity: some tenders forbid cloud AI → on-prem review (Nexify-class) is a wedge.
- Overlap with niche 5: security questionnaires for enterprise sales.

### Minimal MVP stack

Security questionnaire wedge first: upload past answered XLSX + trust docs → answer cell-by-cell with citation + confidence → red cells need human → export XLSX. Phase 2: bilingual tender section drafts from past wins + completeness checklist. Stack: Next.js + vector store of past answers + Claude/GPT in an approved region (or air-gapped for regulated bids). **Never auto-send security/legal rows.**

### Interview script (10)

1. 上季做咗幾多份 RFP／標書／security questionnaire？
2. 平均一份 questionnaire vs 完整標書花幾多人日？
3. Answer library 而家邊個管（SE、security、bid manager）？
4. 舊答案放邊（SharePoint、Loopio、Google Drive、電郵）？
5. 有幾多 % 答案係 reuse vs 重寫？中英文比例？
6. 評估過 Loopio、Responsive、AutogenAI、本地 on-prem 未？
7. 最驚嘅 failure mode（錯答「我哋 support X」、中文 annex 漏交）？
8. Security／legal row 邊個必須批？
9. 有幾常因為人手唔夠而放棄投標？
10. 如果 cycle time 減半，預算大概幾多 HKD／年？

### Sub-scenarios

| Sub-scenario | Pain | Who pays | What to build | How to validate |
| --- | --- | --- | --- | --- |
| Security questionnaire fill | Spreadsheet hell | SE lead | Answer from vault + citations | Person-days per SQ |
| Bilingual tender draft | EN+TC prose bids | Bid manager | Draft sections from past wins | First-draft time |
| Completeness gate | Missing annex = reject | Bid manager | Pre-submit checklist + citations | Rejected-for-incomplete ↓ |
| Answer library freshness | Stale “yes we have X” | Security | Flag low-confidence / outdated | Wrong answers caught |
| Bid / decline decision | Bandwidth kills pursuits | Sales lead | Score effort vs fit | Fewer regret declines |

**First interview target:** Teams who declined or rushed a bank/gov tender last quarter because they were underwater.

---

## Cross-cutting rules (HK)

1. Sell a **measurable recovery** (missed WA jobs, empty chairs, hours, audit days, associate hours, same-day quotes, declined tenders) — not “AI.”
2. Prefer wedges that **connect to a system of record** (Google Calendar, clinic PMS, estate ticket tool, Xero/ABSS, answer vault).
3. Keep a **human gate** on emergencies, ledger posts, attestations, legal send, and security/tender answers.
4. Design for **Cantonese code-switch + Traditional Chinese** from day one; English-only demos lose SME owners.
5. Budget **WhatsApp Business API + Meta message fees** separately from your SaaS fee; disclose PDPO processing.
6. Validate with **10 buyer conversations** (mix Cantonese/English) before building past a demo.

---

## Suggested next step

Pick one niche → one sub-scenario → list 20 real HK buyer names (districts / estates / firms) → run the 10-question script → decide go / no-go on a 2-week WhatsApp-first MVP.

**Companion doc:** `docs/ai-automation-niches-research-2026.md` (global / US-centric version).
