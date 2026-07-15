"""
Main Orchestrator Agent — Poiesis
==================================
Entry point of the pipeline:

    main_agent
        -> requirement_analyser_agent
            -> architecture_designer_agent
                -> code_generator_agent
                    -> testing_agent
                        -> documentation_designer_agent

This agent only collects the AI Agent Name and Purpose, saves them to
session state, and hands off to the Requirement Analyser Agent.
"""
import os

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from requirement_analyser_agent.agent import requirement_analyser_agent
from common.state_keys import AI_NAME, PURPOSE

MODEL = os.getenv("POIESIS_MODEL", "gemini-2.5-flash")


def save_tool(tool_context: ToolContext, ai_name: str, purpose: str) -> dict:
    """Persist the collected agent name and purpose into session state.

    Call this ONLY once both ai_name and purpose are known.
    """
    tool_context.state[AI_NAME] = ai_name
    tool_context.state[PURPOSE] = purpose
    return {
        "status": "success",
        "message": f"Saved AI agent name '{ai_name}' and purpose.",
    }


root_agent = LlmAgent(
    model=MODEL,
    name="main_agent",
    description=(
        "The primary orchestrator agent that welcomes the user and kicks "
        "off the AI-agent-creation pipeline."
    ),
    instruction="""
Role: You are the Primary Orchestrator Agent of Poiesis.

Your responsibility is to coordinate the AI Agent creation process. You do
NOT gather detailed requirements yourself. You identify the user's intent,
collect only the basic information required, save it, and delegate to the
Requirement Analyser Agent.

Workflow:

1. Welcome the user with a short introduction explaining that Poiesis helps
   generate production-ready Google ADK agents from natural language.

2. Collect the following information ONE AT A TIME:
   • AI Agent Name
   • Purpose of the AI Agent
   Ask only ONE question per response. Never ask both in the same turn.

3. As soon as BOTH pieces of information are known, call
   save_tool(ai_name, purpose) exactly once with both values together.
   Never call it with only one value filled in.

4. Immediately after save_tool() succeeds, transfer control to
   requirement_analyser_agent (use the transfer_to_agent tool). Do not ask
   the user anything else and do not attempt to gather requirements
   yourself.

5. After transferring, stop responding — let requirement_analyser_agent
   continue the conversation.

Rules:

1. Ask one question at a time.
2. Keep responses concise and professional.
3. Never skip save_tool() once both values are known.
4. Never fabricate user information.
5. Never continue past step 2 until both Name and Purpose are collected.
6. Never generate requirements, architecture, or code yourself.
7. Maintain conversation context throughout the session.
""",
    tools=[save_tool],
    sub_agents=[requirement_analyser_agent],
)
