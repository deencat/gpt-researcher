"""Structured playbook template schema. :-)"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PlaybookSection:
    """One required section in the playbook output."""

    id: str
    title: str
    instruction: str = ""


@dataclass(frozen=True)
class PlaybookTemplate:
    """A reusable research playbook riding on GPT Researcher's prompt path."""

    id: str
    name: str
    description: str = ""
    topic: str = ""
    tone: str = "Objective"
    report_type: str = "research_report"
    report_source: str = "web"
    report_format: Optional[str] = None
    total_words: Optional[int] = None
    languages: List[str] = field(default_factory=list)
    structure: List[PlaybookSection] = field(default_factory=list)
    output_format: str = "markdown_brief"
    instructions: str = ""
    starter_prompts: List[str] = field(default_factory=list)
    agent_role: Optional[str] = None
    project_defaults: Dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> Dict[str, Any]:
        """JSON-safe summary for API clients (no internal-only fields)."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "topic": self.topic,
            "tone": self.tone,
            "report_type": self.report_type,
            "report_source": self.report_source,
            "report_format": self.report_format,
            "total_words": self.total_words,
            "languages": list(self.languages),
            "structure": [asdict(s) for s in self.structure],
            "output_format": self.output_format,
            "instructions": self.instructions,
            "starter_prompts": list(self.starter_prompts),
            "agent_role": self.agent_role,
            "project_defaults": dict(self.project_defaults or {}),
        }


@dataclass
class AppliedPlaybook:
    """Resolved research knobs after selecting a playbook + request overrides."""

    playbook_id: str
    playbook_name: str
    report_type: str
    report_source: str
    tone: str
    language: str
    language_ids: List[str]
    custom_prompt: str
    report_format: Optional[str] = None
    total_words: Optional[int] = None
    agent_role: Optional[str] = None
    subtopics: List[Dict[str, str]] = field(default_factory=list)
    starter_prompts: List[str] = field(default_factory=list)
    output_format: str = "markdown_brief"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
