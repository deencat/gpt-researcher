"""Project instructions must steer the agent, not become the research topic. :-)"""

from backend.server.project_context import apply_project_instructions


def test_instructions_do_not_rewrite_the_query():
    task, source, role, prompt = apply_project_instructions(
        task="請用六爻解此卦",
        report_source="hybrid",
        project={"instructions": "你是六爻解盤助手。必含八項輸出。"},
        has_docs=True,
        agent_role=None,
        custom_prompt="",
    )
    assert task == "請用六爻解此卦"
    assert "Follow these project instructions" not in task
    assert role.startswith("你是六爻解盤助手")
    assert "CRITICAL" in prompt
    assert source == "hybrid"


def test_empty_project_docs_falls_back_to_web():
    task, source, role, prompt = apply_project_instructions(
        task="q",
        report_source="hybrid",
        project={"instructions": ""},
        has_docs=False,
    )
    assert task == "q"
    assert source == "web"
    assert role is None


def test_web_promotes_to_hybrid_when_docs_exist():
    _, source, _, _ = apply_project_instructions(
        task="q",
        report_source="web",
        project={"instructions": "role"},
        has_docs=True,
    )
    assert source == "hybrid"


def test_merges_existing_agent_role():
    _, _, role, prompt = apply_project_instructions(
        task="q",
        report_source="web",
        project={"instructions": "Project SOP"},
        has_docs=False,
        agent_role="Be concise",
        custom_prompt="Use markdown",
    )
    assert "Project SOP" in role
    assert "Be concise" in role
    assert prompt.startswith("CRITICAL")
    assert "Use markdown" in prompt
