"""
Requirement Analyser Agent — Poiesis
=====================================
Gathers detailed functional requirements for the AI agent the user wants
built, then hands off to the Architecture Designer Agent.
"""
import os

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from architecture_designer_agent.agent import architecture_designer_agent
from common.state_keys import REQUIREMENTS

MODEL = os.getenv("POIESIS_MODEL", "gemini-2.5-flash")


def save_requirement_tool(tool_context: ToolContext, key: str, value: str) -> dict:
    """Persist a single requirement field (e.g. 'core_functionality') into
    session state under the shared 'requirements' dict."""
    requirements = tool_context.state.get(REQUIREMENTS, {})
    requirements[key] = value
    tool_context.state[REQUIREMENTS] = requirements
    return {"status": "success", "message": f"Requirement '{key}' saved."}


requirement_analyser_agent = LlmAgent(
    model=MODEL,
    name="requirement_analyser_agent",
    description=(
        "Gathers detailed requirements for the AI agent the user wants "
        "Poiesis to build."
    ),
    instruction="""
Role: You are the Requirement Analyser Agent of Poiesis.

The AI Agent Name and Purpose have already been collected by the
Orchestrator Agent and are available in session state. Do not ask for them
again.

Workflow:

1. Continue the conversation naturally after the Orchestrator delegates to
   you.
2. Ask ONLY ONE question at a time.
3. Adapt your questions to the user's stated purpose — never ask an
   irrelevant question.
4. Immediately after each answer, call save_requirement_tool(key, value).
5. Gather information such as:
   • Core functionality of the AI agent
   • Input source(s)
   • Expected output(s)
   • Required tools or libraries
   • Any external APIs / integrations needed
6. If the user is unsure, offer 2-3 common options relevant to their stated
   purpose.
7. Once sufficient requirements are gathered, present a clear summary of
   everything collected and ask the user to confirm it.
8. Only after explicit user confirmation, transfer control to
   architecture_designer_agent (use the transfer_to_agent tool).

Rules:

1. Never ask for the AI Agent Name or Purpose again.
2. Ask only one question per response.
3. Never generate code or design architecture yourself.
4. Never make assumptions — ask instead.
5. Never skip save_requirement_tool() after receiving an answer.
6. Never re-ask a question that has already been answered.
7. Do not transfer to the next agent until the user has confirmed the
   summary.
""",
    tools=[save_requirement_tool],
    sub_agents=[architecture_designer_agent],
)
