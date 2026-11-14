"""Load playbook templates from YAML (or JSON) on disk. :-)"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .languages import DEFAULT_PLAYBOOK_LANGUAGES, normalize_language_ids
from .schema import PlaybookSection, PlaybookTemplate

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


class PlaybookNotFoundError(KeyError):
    """Raised when a playbook id is unknown."""


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _parse_sections(raw: Any) -> List[PlaybookSection]:
    sections: List[PlaybookSection] = []
    for item in _as_list(raw):
        if isinstance(item, str):
            sid = item.strip().lower().replace(" ", "_")
            sections.append(PlaybookSection(id=sid, title=item.strip(), instruction=""))
            continue
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("name") or item.get("id") or "").strip()
        sid = str(item.get("id") or title).strip().lower().replace(" ", "_")
        if not sid:
            continue
        sections.append(
            PlaybookSection(
                id=sid,
                title=title or sid,
                instruction=str(item.get("instruction") or item.get("description") or "").strip(),
            )
        )
    return sections


def parse_playbook_dict(data: Dict[str, Any], *, fallback_id: str = "") -> PlaybookTemplate:
    """Validate and normalize a raw template dict into a PlaybookTemplate."""
    if not isinstance(data, dict):
        raise ValueError("Playbook template must be a mapping")

    playbook_id = str(data.get("id") or fallback_id).strip()
    if not playbook_id:
        raise ValueError("Playbook template requires an id")

    name = str(data.get("name") or playbook_id).strip()
    languages = normalize_language_ids(data.get("languages") or DEFAULT_PLAYBOOK_LANGUAGES)
    if not languages:
        languages = list(DEFAULT_PLAYBOOK_LANGUAGES)

    total_words = data.get("total_words")
    if total_words is not None:
        total_words = int(total_words)

    starter = [str(p).strip() for p in _as_list(data.get("starter_prompts")) if str(p).strip()]
    project_defaults = data.get("project_defaults") or {}
    if not isinstance(project_defaults, dict):
        project_defaults = {}

    return PlaybookTemplate(
        id=playbook_id,
        name=name,
        description=str(data.get("description") or "").strip(),
        topic=str(data.get("topic") or "").strip(),
        tone=str(data.get("tone") or "Objective").strip(),
        report_type=str(data.get("report_type") or "research_report").strip(),
        report_source=str(data.get("report_source") or "web").strip(),
        report_format=(str(data["report_format"]).strip() if data.get("report_format") else None),
        total_words=total_words,
        languages=languages,
        structure=_parse_sections(data.get("structure")),
        output_format=str(data.get("output_format") or "markdown_brief").strip(),
        instructions=str(data.get("instructions") or "").strip(),
        starter_prompts=starter,
        agent_role=(str(data["agent_role"]).strip() if data.get("agent_role") else None),
        project_defaults=project_defaults,
    )


def _load_file(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    elif path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        raise ValueError(f"Unsupported playbook format: {path.suffix}")
    if not isinstance(data, dict):
        raise ValueError(f"Playbook file must contain a mapping: {path}")
    return data


@lru_cache(maxsize=1)
def _index_templates(templates_dir: str) -> Dict[str, PlaybookTemplate]:
    root = Path(templates_dir)
    index: Dict[str, PlaybookTemplate] = {}
    if not root.is_dir():
        return index
    for path in sorted(root.glob("*")):
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        if path.name.startswith("_"):
            continue
        data = _load_file(path)
        template = parse_playbook_dict(data, fallback_id=path.stem)
        index[template.id] = template
    return index


def clear_playbook_cache() -> None:
    """Drop the cached template index (for tests / hot reload)."""
    _index_templates.cache_clear()


def list_playbooks(templates_dir: Optional[Path] = None) -> List[PlaybookTemplate]:
    """Return all bundled playbook templates, sorted by id."""
    root = str(templates_dir or TEMPLATES_DIR)
    return sorted(_index_templates(root).values(), key=lambda t: t.id)


def get_playbook(playbook_id: str, templates_dir: Optional[Path] = None) -> PlaybookTemplate:
    """Load one playbook by id or raise PlaybookNotFoundError."""
    if not playbook_id or not str(playbook_id).strip():
        raise PlaybookNotFoundError("playbook_id is required")
    root = str(templates_dir or TEMPLATES_DIR)
    index = _index_templates(root)
    key = str(playbook_id).strip()
    if key not in index:
        raise PlaybookNotFoundError(key)
    return index[key]
