"""Apply Perplexity-style project instructions without polluting the query. :-)"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def apply_project_instructions(
    *,
    task: str,
    report_source: str,
    project: Dict[str, Any],
    has_docs: bool,
    agent_role: Optional[str] = None,
    custom_prompt: str = "",
) -> Tuple[str, str, Optional[str], str]:
    """Return (task, report_source, agent_role, custom_prompt).

    Project instructions become the agent role (system prompt) and a writer
    reminder. They must NOT be prepended to ``task``, or the researcher treats
    the instructions as the research topic.
    """
    source = report_source
    if has_docs and source == "web":
        source = "hybrid"
    elif not has_docs and source in ("hybrid", "local"):
        source = "web"

    instructions = str(project.get("instructions") or "").strip()
    if not instructions:
        return task, source, agent_role, custom_prompt or ""

    role = instructions
    if agent_role and agent_role.strip() and agent_role.strip() != instructions:
        role = f"{instructions}\n\n---\nAdditional role guidance:\n{agent_role.strip()}"

    reminder = (
        "CRITICAL: Follow the project system instructions in your agent role exactly. "
        "Use the required method routing, output sections, language, and prohibitions. "
        "Do not replace the assigned method with a generic summary."
    )
    prompt = custom_prompt.strip() if custom_prompt else f"Write the research report for this question:\n{task}"
    if reminder not in prompt:
        prompt = f"{reminder}\n\n{prompt}"

    return task, source, role, prompt
