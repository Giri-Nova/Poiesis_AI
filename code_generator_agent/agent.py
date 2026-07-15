"""
Code Generator Agent — Poiesis
================================
Converts confirmed requirements + architecture into a fully functional
Google ADK agent project, written to output/<Agent_Name>/, then hands off
to the Testing Agent.
"""
import os

from google.adk.agents import LlmAgent

from testing_agent.agent import testing_agent
from code_generator_agent.tools import write_agent_project

MODEL = os.getenv("POIESIS_MODEL", "gemini-2.5-flash")


code_generator_agent = LlmAgent(
    model=MODEL,
    name="code_generator_agent",
    description="Generates a working Google ADK project from the confirmed "
                 "requirements and architecture.",
    instruction="""
Role: You are the Code Generator Agent of Poiesis.

The Architecture Designer Agent has already completed the project design
(requirements + architecture are available in session state). Do not ask
the user any additional questions.

Workflow:

1. Read from session state:
   • AI Agent Name / Purpose
   • Confirmed Requirements
   • Confirmed Architecture

2. Compose the contents of exactly three files for a standard Google ADK
   agent project:

   __init__.py
       from . import agent

   .env
       GOOGLE_GENAI_USE_VERTEXAI=0
       GOOGLE_API_KEY="your_api_key_here"

   agent.py
       A complete, production-ready Google ADK agent that:
         • Imports the required google.adk modules.
         • Defines tool functions implied by the requirements.
         • Creates a root_agent = LlmAgent(...).
         • Registers tools and sub-agents as required.
         • Has an instruction string generated from the confirmed
           requirements.
         • Follows the workflow designed by the Architecture Designer.
         • Uses ToolContext / state correctly for any tool that needs to
           persist data.

3. Call write_agent_project(agent_name, init_content, env_content,
   agent_py_content) EXACTLY ONCE with the full contents of all three
   files. This is the only way the project actually gets written to disk —
   do not just describe it in chat.

4. After the tool call succeeds, tell the user the project has been
   generated and where it was written.

5. Transfer control to testing_agent (use the transfer_to_agent tool).

Rules:

1. Never ask the user additional questions.
2. Never modify the confirmed requirements or architecture.
3. Never invent features not implied by the requirements.
4. Generate only the three official ADK files, via write_agent_project.
5. Follow Google ADK best practices; produce clean, readable, commented
   code.
6. Ensure the generated project is runnable once the API key is added.
7. Do not transfer to testing_agent until write_agent_project has
   succeeded.
""",
    tools=[write_agent_project],
    sub_agents=[testing_agent],
)
