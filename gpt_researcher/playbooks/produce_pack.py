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


def assemble_scripts_markdown(sections: Sequence[str]) -> str:
    """Join per-language shootable scripts into one document. :-)"""
    header = (
        "# Comedy Channel — Shootable Scripts\n\n"
        "> One shootable short per language market, grounded in the scored story "
        "backlog (EN / 粵語 / 普通话 / 國語). Timed beats ~30–60s with hard captions.\n\n"
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


async def _produce_script_for_language(
    *,
    brief: str,
    stories_slice: str,
    project_name: str,
    goal: str,
    lang: Dict[str, str],
) -> str:
    """Write one timed shootable script for a language market. :-)"""
    story_context = stories_slice or "(No story slice — invent from research, still use this market's id prefix.)"
    prompt = f"""You are a subject-matter expert in multilingual comedy short-form video.
Project: “{project_name}”
Goal: {goal or "(none)"}

Write ONE fully shootable comedy short script for this market only:
**{lang['label']}**

Return ONLY valid JSON: {{"markdown": "<markdown string>"}}. No fences.

Rules:
1. Pick the strongest Ship: YES story from the story list below (prefer highest Hook+Punch+Local fit, then lower Remake risk).
2. Script heading must cite that story id, e.g.
   ## Script ({lang['id_prefix']}0X): “Title” (35–55s, {lang['label']})
3. Include: **Cast**, **Props**, **On-screen style**, then timed sections:
   HOOK → SETUP → ESCALATION → PUNCH + CTA (total ~30–60 seconds).
4. Dialogue and hard captions in this market's language/script. Keep Chinese variants distinct.
5. Do NOT use legacy ids S01/S05/S06 — only {lang['id_prefix']}01–{lang['id_prefix']}{STORIES_PER_LANGUAGE:02d}.
6. Keep lines short; leave room for captions.

Story list for this market:
---
{story_context[:9000]}
---

Research brief (secondary context):
---
{brief[:4000]}
---
"""
    data = await _llm_json(prompt=prompt, temperature=0.35, max_tokens=5000)
    md = str(data.get("markdown") or "").strip()
    if not md:
        raise ValueError(f"Empty script for {lang['label']}")
    if not md.lstrip().startswith("#"):
        md = f"## Script ({lang['id_prefix']}): {lang['label']}\n\n{md}"
    return md


async def produce_scripts_markdown(
    *,
    research_markdown: str,
    stories_markdown: str = "",
    project_name: str = "Comedy channel",
    goal: str = "",
) -> str:
    """Build 03_Scripts.md: one timed script per language from the 40-story list. :-)"""
    brief = _trim_brief(research_markdown, limit=8000)
    stories = (stories_markdown or "").strip()
    batches = await asyncio.gather(
        *[
            _produce_script_for_language(
                brief=brief,
                stories_slice=_slice_stories_for_language(stories, lang),
                project_name=project_name,
                goal=goal,
                lang=lang,
            )
            for lang in STORY_LANGUAGES
        ]
    )
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
