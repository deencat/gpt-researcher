"""Playbook templates for structured, reusable research briefs. :-)"""

from .apply import apply_playbook, apply_to_researcher, merge_start_payload
from .languages import LANGUAGE_CATALOG, catalog_public, format_language_directive
from .loader import (
    PlaybookNotFoundError,
    clear_playbook_cache,
    get_playbook,
    list_playbooks,
    parse_playbook_dict,
)
from .schema import AppliedPlaybook, PlaybookSection, PlaybookTemplate

__all__ = [
    "LANGUAGE_CATALOG",
    "AppliedPlaybook",
    "PlaybookNotFoundError",
    "PlaybookSection",
    "PlaybookTemplate",
    "apply_playbook",
    "apply_to_researcher",
    "catalog_public",
    "clear_playbook_cache",
    "format_language_directive",
    "get_playbook",
    "list_playbooks",
    "merge_start_payload",
    "parse_playbook_dict",
]
