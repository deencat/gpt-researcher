"""Turn research markdown into Plan / Stories / Scripts project documents. :-)"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

PACK_FILES = (
    ("plan", "01_Plan.md"),
    ("stories", "02_Stories.md"),
    ("scripts", "03_Scripts.md"),
)

# Ten scored stories per market → 40 total in 02_Stories.md. :-)
STORY_LANGUAGES: Sequence[Dict[str, str]] = (
    {
        "id": "EN",
        "label": "English",
        "heading": "## English (EN) — 10 stories",
        "id_prefix": "EN",
    },
    {
        "id": "YUE",
        "label": "Hong Kong Cantonese (粵語)",
        "heading": "## Hong Kong Cantonese (粵語) — 10 stories",
        "id_prefix": "YUE",
    },
    {
        "id": "CMN",
        "label": "Mainland Mandarin (普通话)",
        "heading": "## Mainland Mandarin (普通话) — 10 stories",
        "id_prefix": "CMN",
    },
    {
        "id": "TW",
        "label": "Taiwan Mandarin (國語)",
        "heading": "## Taiwan Mandarin (國語) — 10 stories",
        "id_prefix": "TW",
    },
)

STORIES_PER_LANGUAGE = 10


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError("Model did not return JSON for the comedy pack")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Pack JSON must be an object")
    return data


def _trim_brief(research_markdown: str, limit: int = 12000) -> str:
    brief = (research_markdown or "").strip()
    if len(brief) > limit:
        return brief[:limit]
    return brief


async def _llm_json(
    *,
    prompt: str,
    temperature: float = 0.35,
    max_tokens: int = 8000,
) -> Dict[str, Any]:
    from gpt_researcher.config.config import Config
    from gpt_researcher.utils.llm import create_chat_completion, parse_llm_spec

    cfg = Config()
    provider, model = parse_llm_spec(cfg.smart_llm)
    cap = min(int(getattr(cfg, "smart_token_limit", 8000) or 8000), max_tokens)
    raw = await create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        llm_provider=provider,
        temperature=temperature,
        max_tokens=cap,
        llm_kwargs=getattr(cfg, "llm_kwargs", {}) or {},
    )
    return _extract_json(raw if isinstance(raw, str) else str(raw))


def assemble_stories_markdown(sections: Sequence[str]) -> str:
    """Join per-language story batches into one scored list document. :-)"""
    header = (
        "# Comedy Channel — Scored Story List\n\n"
        "> Scoring: **Hook / Punch / Local fit / Remake risk** (0–5). "
        "Higher = better, except **Remake risk** where higher = more common/less original.\n\n"
        f"> Target: **{STORIES_PER_LANGUAGE} stories per language** "
        f"({STORIES_PER_LANGUAGE * len(STORY_LANGUAGES)} total) across "
        "English, Hong Kong Cantonese (粵語), Mainland Mandarin (普通话), "
        "and Taiwan Mandarin (國語).\n\n"
    )
    body = "\n\n".join(s.strip() for s in sections if (s or "").strip())
    out = header + body + "\n"
    return out


async def _produce_stories_for_language(
    *,
    brief: str,
    project_name: str,
    goal: str,
    lang: Dict[str, str],
) -> str:
    """Generate exactly 10 scored stories for one language market. :-)"""
    prompt = f"""You are a subject-matter expert in multilingual comedy short-form video.
Project: “{project_name}”
Goal: {goal or "(none)"}

Write EXACTLY {STORIES_PER_LANGUAGE} scored comedy short story ideas for ONE market only:
**{lang['label']}**

Return ONLY valid JSON: {{"markdown": "<markdown string>"}}. No fences.

The markdown value must:
1. Start with this exact heading line:
{lang['heading']}
2. Then list exactly {STORIES_PER_LANGUAGE} stories numbered 1–{STORIES_PER_LANGUAGE}.
3. Each story id must use prefix {lang['id_prefix']} (e.g. {lang['id_prefix']}01 … {lang['id_prefix']}{STORIES_PER_LANGUAGE:02d}).
4. Each story includes: id, format, premise, hook, beats (3–6), languages (this market primary),
   Scores: Hook / Punch / Local fit / Remake risk (0–5 each), Ship YES/NO, title options (2+ in this market's language/script).
5. Stories must be distinct premises — not the same joke rewritten ten times.
6. Keep Chinese variants distinct; do NOT mix 粵語 / 普通话 / 國語 into other markets' primary language.
7. Prefer salon / service-culture / everyday misunderstanding comedy grounded in the research brief when useful.

Research brief (context only):
---
{brief}
---
"""
    data = await _llm_json(prompt=prompt, temperature=0.4, max_tokens=10000)
    md = str(data.get("markdown") or "").strip()
    if not md:
        raise ValueError(f"Empty stories batch for {lang['label']}")
    if lang["heading"] not in md and not md.startswith("##"):
        md = f"{lang['heading']}\n\n{md}"
    return md


async def produce_stories_markdown(
    *,
    research_markdown: str,
    project_name: str = "Comedy channel",
    goal: str = "",
) -> str:
    """Build 02_Stories.md with 10 stories × 4 languages (40 total). :-)"""
    brief = _trim_brief(research_markdown)
    batches = await asyncio.gather(
        *[
            _produce_stories_for_language(
                brief=brief,
                project_name=project_name,
                goal=goal,
                lang=lang,
            )
            for lang in STORY_LANGUAGES
        ]
    )
    return assemble_stories_markdown(batches)


# How many catching stories to turn into full shootable scripts. :-)
SCRIPTS_TARGET = 10
SCRIPTS_MIN_PER_LANGUAGE = 2


def assemble_scripts_markdown(sections: Sequence[str]) -> str:
    """Join shootable scripts into one document. :-)"""
    header = (
        "# Comedy Channel — Shootable Scripts\n\n"
        f"> Up to **{SCRIPTS_TARGET}** catching stories from the scored backlog "
        "(EN / 粵語 / 普通话 / 國語), each as a timed ~30–60s short with hard captions.\n\n"
    )
    body = "\n\n".join(s.strip() for s in sections if (s or "").strip())
    return header + body + "\n"


def _slice_stories_for_language(stories_markdown: str, lang: Dict[str, str]) -> str:
    """Extract one language section from 02_Stories.md when present. :-)"""
    text = (stories_markdown or "").strip()
    if not text:
        return ""
    heading = lang["heading"]
    # Match "## English..." through the next language heading or EOF.
    pattern = (
        re.escape(heading)
        + r"[\s\S]*?(?=\n## (?:English|Hong Kong|Mainland|Taiwan)\b|\Z)"
    )
    match = re.search(pattern, text)
    if match:
        return match.group(0).strip()
    # Fallback: prefix id filter (EN01, YUE01, …)
    prefix = lang["id_prefix"]
    lines = []
    keep = False
    for line in text.splitlines():
        if line.startswith("## ") and "— 10 stories" in line:
            keep = lang["label"].split("(")[0].strip() in line or prefix in line
        if keep:
            lines.append(line)
    return "\n".join(lines).strip()


def _parse_story_cards(stories_markdown: str) -> List[Dict[str, Any]]:
    """Parse scored story cards from 02_Stories.md into rankable dicts. :-)"""
    text = stories_markdown or ""
    cards: List[Dict[str, Any]] = []
    # Blocks start at "1. **EN01" / "1. **EN01 — title**"
    parts = re.split(r"(?m)^(?=\d+\.\s+\*\*)", text)
    for part in parts:
        head = re.match(
            r"\d+\.\s+\*\*((?:EN|YUE|CMN|TW)\d{2})(?:\s*[—–\-]\s*([^*]+))?\*\*",
            part.strip(),
        )
        if not head:
            continue
        story_id = head.group(1)
        title = (head.group(2) or "").strip()
        ship_m = re.search(r"\*\*Ship\s*[:：]\s*\*\*\s*(\w+)", part, flags=re.I)
        scores_m = re.search(r"\*\*Scores?\s*[:：]\s*\*\*\s*(.+)", part, flags=re.I)
        premise_m = re.search(
            r"\*\*(?:Premise|premise)\s*[:：]\s*\*\*\s*(.+)", part
        )
        hook_m = re.search(r"\*\*(?:Hook|hook)\s*[:：]\s*\*\*\s*(.+)", part)
        ship = (ship_m.group(1) if ship_m else "").upper()
        scores_raw = scores_m.group(1).strip() if scores_m else ""
        nums = {
            k.lower(): int(v)
            for k, v in re.findall(
                r"(Hook|Punch|Local fit|Remake risk)\s*(\d)", scores_raw, flags=re.I
            )
        }
        prefix = re.sub(r"\d+$", "", story_id)
        lang = next((L for L in STORY_LANGUAGES if L["id_prefix"] == prefix), None)
        cards.append(
            {
                "id": story_id,
                "title": title,
                "prefix": prefix,
                "lang": lang,
                "ship": ship,
                "hook": nums.get("hook", 0),
                "punch": nums.get("punch", 0),
                "local_fit": nums.get("local fit", 0),
                "remake_risk": nums.get("remake risk", 0),
                "premise": (premise_m.group(1).strip() if premise_m else ""),
                "hook_line": (hook_m.group(1).strip() if hook_m else ""),
                "card": part.strip(),
            }
        )
    return cards


def select_catching_stories(
    stories_markdown: str,
    *,
    target: int = SCRIPTS_TARGET,
    min_per_language: int = SCRIPTS_MIN_PER_LANGUAGE,
) -> List[Dict[str, Any]]:
    """Pick the strongest Ship:YES stories, balanced across languages. :-)"""
    cards = [
        c
        for c in _parse_story_cards(stories_markdown)
        if c.get("ship") == "YES" and c.get("lang")
    ]

    def rank_key(c: Dict[str, Any]) -> tuple:
        good = c["hook"] + c["punch"] + c["local_fit"]
        return (good, -c["remake_risk"], c["hook"], c["punch"])

    cards.sort(key=rank_key, reverse=True)
    selected: List[Dict[str, Any]] = []
    counts = {L["id_prefix"]: 0 for L in STORY_LANGUAGES}

    # First pass: ensure min_per_language from each market's best cards.
    for lang in STORY_LANGUAGES:
        prefix = lang["id_prefix"]
        pool = [c for c in cards if c["prefix"] == prefix]
        for c in pool[:max(0, min_per_language)]:
            if c["id"] not in {s["id"] for s in selected}:
                selected.append(c)
                counts[prefix] += 1

    # Second pass: fill to target with remaining global best.
    for c in cards:
        if len(selected) >= target:
            break
        if c["id"] in {s["id"] for s in selected}:
            continue
        selected.append(c)
        counts[c["prefix"]] += 1

    selected.sort(key=lambda c: (c["prefix"], c["id"]))
    return selected[:target]


async def _produce_script_for_story(
    *,
    brief: str,
    story: Dict[str, Any],
    project_name: str,
    goal: str,
) -> str:
    """Write one timed shootable script for a specific story id. :-)"""
    lang = story["lang"]
    label = lang["label"] if lang else story["prefix"]
    story_context = story.get("card") or ""
    prompt = f"""You are a subject-matter expert in multilingual comedy short-form video.
Project: “{project_name}”
Goal: {goal or "(none)"}

Write ONE fully shootable comedy short script for this exact story:
**{story['id']}** — {story.get('title') or '(see card)'}
Market: **{label}**

Return ONLY valid JSON: {{"markdown": "<markdown string>"}}. No fences.

Rules:
1. Script MUST be for story id {story['id']} only (do not switch to another id).
2. Heading format:
   ## Script ({story['id']}): “Title” (35–55s, {label})
3. Include: **Cast**, **Props**, **On-screen style**, then timed sections:
   HOOK → SETUP → ESCALATION → PUNCH + CTA (total ~30–60 seconds).
4. Dialogue and hard captions in this market's language/script. Keep Chinese variants distinct.
5. Do NOT use legacy ids like S01/S05/S06.
6. Keep lines short; leave room for captions.
7. Ground beats in the story card below (premise/hook/beats/scores).

Story card:
---
{story_context[:7000]}
---

Research brief (secondary context):
---
{brief[:3000]}
---
"""
    data = await _llm_json(prompt=prompt, temperature=0.35, max_tokens=5000)
    md = str(data.get("markdown") or "").strip()
    if not md:
        raise ValueError(f"Empty script for {story['id']}")
    if story["id"] not in md:
        md = f"## Script ({story['id']}): {story.get('title') or label}\n\n{md}"
    if not md.lstrip().startswith("#"):
        md = f"## Script ({story['id']}): {story.get('title') or label}\n\n{md}"
    return md


async def produce_scripts_markdown(
    *,
    research_markdown: str,
    stories_markdown: str = "",
    project_name: str = "Comedy channel",
    goal: str = "",
) -> str:
    """Build 03_Scripts.md for ~10 catching stories from the 40-story list. :-)"""
    brief = _trim_brief(research_markdown, limit=8000)
    stories = (stories_markdown or "").strip()
    selected = select_catching_stories(stories)
    if not selected:
        # Fallback: one script per language from raw slices (legacy behavior). :-)
        selected = []
        for lang in STORY_LANGUAGES:
            selected.append(
                {
                    "id": f"{lang['id_prefix']}01",
                    "title": "",
                    "prefix": lang["id_prefix"],
                    "lang": lang,
                    "ship": "YES",
                    "hook": 0,
                    "punch": 0,
                    "local_fit": 0,
                    "remake_risk": 0,
                    "premise": "",
                    "hook_line": "",
                    "card": _slice_stories_for_language(stories, lang),
                }
            )

    # Generate in waves to avoid hammering the LLM provider. :-)
    batches: List[str] = []
    wave = 4
    for i in range(0, len(selected), wave):
        chunk = selected[i : i + wave]
        parts = await asyncio.gather(
            *[
                _produce_script_for_story(
                    brief=brief,
                    story=story,
                    project_name=project_name,
                    goal=goal,
                )
                for story in chunk
            ]
        )
        batches.extend(parts)
    return assemble_scripts_markdown(batches)


async def _produce_plan(
    *,
    brief: str,
    project_name: str,
    goal: str,
) -> str:
    prompt = f"""You are a subject-matter expert in multilingual comedy short-form video.
Write ONE markdown production plan for the project “{project_name}”.

Languages must stay distinct: English, Hong Kong Cantonese (粵語), Mainland Mandarin (普通话), Taiwan Mandarin (國語).

Return ONLY valid JSON: {{"plan": "<markdown string>"}}. No fences.

plan: weekly production plan (cadence, pillars, language rotation, KPIs, shoot checklist, phrase bank).
Note that the story backlog has {STORIES_PER_LANGUAGE} ideas per language ({STORIES_PER_LANGUAGE * len(STORY_LANGUAGES)} total).
First line must be: # Comedy Channel — Production Plan

Project goal (if any): {goal or "(none)"}

Research brief:
---
{brief}
---
"""
    data = await _llm_json(prompt=prompt, temperature=0.35, max_tokens=6000)
    body = str(data.get("plan") or "").strip()
    if not body:
        raise ValueError("Pack missing section: plan")
    return body if body.endswith("\n") else body + "\n"


async def produce_comedy_pack_markdown(
    *,
    research_markdown: str,
    project_name: str = "Comedy channel",
    goal: str = "",
    sections: Optional[Sequence[str]] = None,
    stories_markdown: Optional[str] = None,
) -> Dict[str, str]:
    """LLM-split a research brief into plan / scored stories / scripts.

    Stories are generated as 10 per language (40 total) in parallel batches.
    Scripts are grounded in the 40-story list (one timed script per language).
    Pass sections=["stories"] or ["scripts"] to regenerate only that section.
    """
    brief = _trim_brief(research_markdown)
    wanted = {s.strip().lower() for s in (sections or ("plan", "stories", "scripts"))}
    wanted &= {"plan", "stories", "scripts"}
    if not wanted:
        wanted = {"plan", "stories", "scripts"}

    out: Dict[str, str] = {}
    tasks: List[Any] = []

    async def _stories() -> None:
        out["stories"] = await produce_stories_markdown(
            research_markdown=brief,
            project_name=project_name,
            goal=goal,
        )

    async def _plan() -> None:
        out["plan"] = await _produce_plan(
            brief=brief, project_name=project_name, goal=goal
        )

    async def _scripts() -> None:
        # Prefer freshly generated stories in this run; else caller-supplied backlog. :-)
        backlog = out.get("stories") or (stories_markdown or "")
        out["scripts"] = await produce_scripts_markdown(
            research_markdown=brief,
            stories_markdown=backlog,
            project_name=project_name,
            goal=goal,
        )

    if "stories" in wanted:
        tasks.append(_stories())
    if "plan" in wanted:
        tasks.append(_plan())

    # Stories first when both stories+scripts requested so scripts can use them.
    if tasks:
        await asyncio.gather(*tasks)
        tasks = []

    if "scripts" in wanted:
        await _scripts()

    for key in wanted:
        body = str(out.get(key) or "").strip()
        if not body:
            raise ValueError(f"Pack missing section: {key}")
        out[key] = body if body.endswith("\n") else body + "\n"
    return out


async def save_pack_to_project(
    project_store: Any,
    user: Any,
    project_id: str,
    pack: Dict[str, str],
    *,
    research_markdown: Optional[str] = None,
) -> Dict[str, Any]:
    """Write pack markdown files into the project docs folder."""
    saved = []
    if research_markdown and research_markdown.strip():
        name = await project_store.save_document(
            user, project_id, "research_report.md", research_markdown.encode("utf-8")
        )
        if name:
            saved.append(name)
    for key, filename in PACK_FILES:
        if key not in pack:
            continue
        name = await project_store.save_document(
            user, project_id, filename, pack[key].encode("utf-8")
        )
        if name:
            saved.append(name)
    project = await project_store.get_project(user, project_id)
    return {"files": saved, "project": project}
