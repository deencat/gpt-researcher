"""Select a playbook and merge it into a research start request. :-)"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .languages import format_language_directive, normalize_language_ids
from .loader import get_playbook
from .schema import AppliedPlaybook, PlaybookTemplate


def build_custom_prompt(
    template: PlaybookTemplate,
    *,
    query: str,
    language_directive: str,
) -> str:
    """Turn playbook structure + instructions into the report custom_prompt.

    This rides on GPTResearcher's existing custom_prompt path in
    actions/report_generation.py so playbooks stay first-class without a
    new ReportType for every niche.
    """
    lines: List[str] = [
        "You are writing a shippable research brief from the selected playbook — "
        "not a long essay.",
        f"Playbook: {template.name} ({template.id}).",
    ]
    if template.topic:
        lines.append(f"Topic focus: {template.topic}.")
    lines.append(f"Research query: {query}")
    lines.append(f"You MUST write the brief in: {language_directive}.")
    lines.append(f"Output format: {template.output_format}.")

    if template.instructions:
        lines.append("")
        lines.append("Playbook instructions:")
        lines.append(template.instructions.strip())

    if template.structure:
        lines.append("")
        lines.append("Required structure (use these section headings in order):")
        for section in template.structure:
            detail = f" — {section.instruction}" if section.instruction else ""
            lines.append(f"- ## {section.title}{detail}")

    lines.extend(
        [
            "",
            "Rules:",
            "- Prefer concrete, actionable items (hooks, titles, beat sheets, references) over vague advice.",
            "- Cite sources with markdown links when available.",
            "- Keep the brief scannable; use short bullets under each heading.",
            "- Separate markets/languages when findings differ.",
            "- Flag culture-sensitive jokes and platform policy risks when relevant.",
        ]
    )
    return "\n".join(lines).strip()


def structure_as_subtopics(template: PlaybookTemplate) -> List[Dict[str, str]]:
    """Seed DetailedReport subtopics from playbook structure when useful."""
    return [
        {
            "task": section.title,
            "description": section.instruction or section.title,
        }
        for section in template.structure
    ]


def apply_playbook(
    playbook_id: str,
    *,
    query: str,
    report_type: Optional[str] = None,
    report_source: Optional[str] = None,
    tone: Optional[str] = None,
    language_ids: Optional[Sequence[str]] = None,
    templates_dir=None,
) -> AppliedPlaybook:
    """Resolve a playbook with optional per-request overrides.

    Explicit request fields win over template defaults. Language ids from the
    request replace the template defaults when provided.
    """
    template = get_playbook(playbook_id, templates_dir=templates_dir)
    langs = normalize_language_ids(language_ids) or list(template.languages)
    language = format_language_directive(langs)

    resolved_type = (report_type or template.report_type or "research_report").strip()
    resolved_source = (report_source or template.report_source or "web").strip()
    resolved_tone = (tone or template.tone or "Objective").strip()

    return AppliedPlaybook(
        playbook_id=template.id,
        playbook_name=template.name,
        report_type=resolved_type,
        report_source=resolved_source,
        tone=resolved_tone,
        language=language,
        language_ids=langs,
        custom_prompt=build_custom_prompt(
            template, query=query, language_directive=language
        ),
        report_format=template.report_format,
        total_words=template.total_words,
        agent_role=template.agent_role,
        subtopics=structure_as_subtopics(template),
        starter_prompts=list(template.starter_prompts),
        output_format=template.output_format,
    )


def apply_to_researcher(researcher: Any, applied: AppliedPlaybook) -> None:
    """Mutate a GPTResearcher instance with playbook language / format / role."""
    if applied.language:
        researcher.cfg.language = applied.language
    if applied.report_format:
        researcher.cfg.report_format = applied.report_format
    if applied.total_words is not None:
        researcher.cfg.total_words = int(applied.total_words)
    if applied.agent_role:
        # Prefer the playbook role over auto-chosen agent copy.
        researcher.agent = applied.agent_role
        researcher.role = applied.agent_role


def _playbook_id_from_payload(data: Dict[str, Any]) -> Optional[str]:
    """Extract a playbook id from start payload fields.

    Accepts `playbook_id` or a string `playbook` alias. Ignores non-string
    `playbook` values (e.g. an already-merged metadata dict).
    """
    for key in ("playbook_id", "playbook"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def merge_start_payload(json_data: Any) -> Dict[str, Any]:
    """If playbook_id is present, merge resolved defaults into the start payload.

    Returns a shallow-copied dict suitable for extract_command_data. Adds
    `custom_prompt`, `language`, and `playbook` metadata keys used downstream.
    Malformed non-mapping inputs are treated as an empty payload.
    """
    if not isinstance(json_data, dict):
        return {}
    data = dict(json_data)
    playbook_id = _playbook_id_from_payload(data)
    if not playbook_id:
        return data

    language_ids = data.get("language_ids")
    if language_ids is None:
        language_ids = data.get("languages")
    # Empty list should fall through to template defaults inside apply_playbook.
    applied = apply_playbook(
        playbook_id,
        query=str(data.get("task") or ""),
        report_type=data.get("report_type") if isinstance(data.get("report_type"), str) else None,
        report_source=data.get("report_source") if isinstance(data.get("report_source"), str) else None,
        tone=data.get("tone") if isinstance(data.get("tone"), str) else None,
        language_ids=language_ids if isinstance(language_ids, (list, tuple)) else None,
    )

    # Template fills blanks; explicit request values already preferred in apply_playbook
    # when passed through — here we still set the resolved fields for the runner.
    data["report_type"] = applied.report_type
    data["report_source"] = applied.report_source
    data["tone"] = applied.tone
    data["custom_prompt"] = applied.custom_prompt
    data["language"] = applied.language
    data["language_ids"] = applied.language_ids
    data["playbook_id"] = applied.playbook_id
    data["playbook"] = applied.to_dict()
    if applied.report_format:
        data["report_format"] = applied.report_format
    if applied.total_words is not None:
        data["total_words"] = applied.total_words
    if applied.subtopics and not data.get("subtopics"):
        data["subtopics"] = applied.subtopics
    return data
