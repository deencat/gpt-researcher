"""Turn research markdown into Plan / Stories / Scripts project documents. :-)"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

PACK_FILES = (
    ("plan", "01_Plan.md"),
    ("stories", "02_Stories.md"),
    ("scripts", "03_Scripts.md"),
)


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError("Model did not return JSON for the comedy pack")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Pack JSON must be an object")
    return data


async def produce_comedy_pack_markdown(
    *,
    research_markdown: str,
    project_name: str = "Comedy channel",
    goal: str = "",
) -> Dict[str, str]:
    """LLM-split a research brief into plan / scored stories / scripts."""
    from gpt_researcher.config.config import Config
    from gpt_researcher.utils.llm import create_chat_completion, parse_llm_spec

    cfg = Config()
    provider, model = parse_llm_spec(cfg.smart_llm)
    brief = (research_markdown or "").strip()
    if len(brief) > 14000:
        brief = brief[:14000]

    prompt = f"""You are a subject-matter expert in multilingual comedy short-form video.
Convert the research brief into THREE markdown documents for the project “{project_name}”.

Languages must stay distinct: English, Hong Kong Cantonese (粵語), Mainland Mandarin (普通话), Taiwan Mandarin (國語). Never collapse Chinese variants.

Return ONLY valid JSON with keys plan, stories, scripts (each a full markdown string). No fences.

plan: weekly production plan (cadence, pillars, language rotation, KPIs, shoot checklist).
First line must be: # Comedy Channel — Production Plan

stories: scored idea list with at least 8 stories. Each item: id, format, premise, hook, beats (3-6),
languages, Hook/Punch/Local fit/Remake risk (0-5), Ship YES/NO, title options.
First line must be: # Comedy Channel — Scored Story List

scripts: at least 3 fully shootable scripts for different stories. Include dialogue/captions/CTA.
Prefer at least one script with EN + 粵語 + 普通话 + 國語 lines.
First line must be: # Comedy Channel — Shootable Scripts

Project goal (if any): {goal or "(none)"}

Research brief:
---
{brief}
---
"""

    raw = await create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        llm_provider=provider,
        temperature=0.35,
        max_tokens=min(int(getattr(cfg, "smart_token_limit", 8000) or 8000), 12000),
        llm_kwargs=getattr(cfg, "llm_kwargs", {}) or {},
    )
    data = _extract_json(raw if isinstance(raw, str) else str(raw))
    out: Dict[str, str] = {}
    for key, _filename in PACK_FILES:
        body = str(data.get(key) or "").strip()
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
        name = await project_store.save_document(
            user, project_id, filename, pack[key].encode("utf-8")
        )
        if name:
            saved.append(name)
    project = await project_store.get_project(user, project_id)
    return {"files": saved, "project": project}
