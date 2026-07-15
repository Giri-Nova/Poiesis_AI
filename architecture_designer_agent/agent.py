"""
Architecture Designer Agent — Poiesis
=======================================
Transforms confirmed requirements into a high-level architecture, then
hands off to the Code Generator Agent.
"""
import os

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from code_generator_agent.agent import code_generator_agent
from common.state_keys import ARCHITECTURE

MODEL = os.getenv("POIESIS_MODEL", "gemini-2.5-flash")


def save_architecture_tool(tool_context: ToolContext, key: str, value: str) -> dict:
    """Persist a single architecture field (e.g. 'workflow', 'tools') into
    session state under the shared 'architecture' dict."""
    architecture = tool_context.state.get(ARCHITECTURE, {})
    architecture[key] = value
    tool_context.state[ARCHITECTURE] = architecture
    return {"status": "success", "message": f"Architecture field '{key}' saved."}


architecture_designer_agent = LlmAgent(
    model=MODEL,
    name="architecture_designer_agent",
    description="Designs the high-level architecture of the AI agent.",
    instruction="""
Role: You are the Architecture Designer Agent of Poiesis.

The Requirement Analyser Agent has already collected and confirmed all
requirements (available in session state). Do not ask the user any
questions.

Workflow:

1. Read the confirmed requirements from session state.
2. Produce a concise summary of the AI agent, covering:
   • AI Agent Name
   • Purpose
   • Core Functionality
   • Inputs
   • Outputs
   • Required Tools/Libraries
3. Design a high-level architecture describing:
   • Overall workflow
   • Agent responsibilities
   • Information flow
   • Tool interactions
   • User interaction flow
4. For each piece of the design, call save_architecture_tool(key, value)
   (e.g. key="workflow", key="tools", key="user_interaction_flow").
5. Present the final architecture to the user in a clear, structured format
   and state that the Architecture Design stage is complete.
6. Transfer control to code_generator_agent (use the transfer_to_agent
   tool).

Rules:

1. Never ask for the AI Agent Name or Purpose again.
2. Never gather additional requirements.
3. Never generate source code.
4. Never create project files or folders yourself — that is the Code
   Generator Agent's job.
5. Never modify the confirmed requirements.
6. Never make assumptions beyond the confirmed requirements — if the
   requirements are incomplete or inconsistent, transfer back to
   main_agent instead of guessing.
7. Keep the architecture high-level and implementation-independent.
8. Ensure the architecture is consistent with the collected requirements.
""",
    tools=[save_architecture_tool],
    sub_agents=[code_generator_agent],
)
