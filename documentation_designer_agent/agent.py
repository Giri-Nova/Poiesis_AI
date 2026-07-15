"""
Documentation Designer Agent — Poiesis
=========================================
Final stage of the pipeline. Produces README.md and a build report for the
generated project, then closes out the session.

NOTE: this agent was referenced by name in every other agent's instructions
in the original code, but no implementation existed for it. This file adds
it as the closing link in the chain.
"""
import os

from google.adk.agents import LlmAgent

from documentation_designer_agent.tools import save_documentation

MODEL = os.getenv("POIESIS_MODEL", "gemini-2.5-flash")


documentation_designer_agent = LlmAgent(
    model=MODEL,
    name="documentation_designer_agent",
    description="Writes the final README and build report for the "
                 "generated AI agent project.",
    instruction="""
Role: You are the Documentation Designer Agent of Poiesis — the final
stage of the pipeline.

Testing has already completed (requirements, architecture, generated
project, and testing results are all available in session state). Do not
ask the user any questions.

Workflow:

1. Read from session state: AI Agent Name, Purpose, Requirements,
   Architecture, and Testing results.
2. Compose a clear README.md for the generated project, including:
   • Title and one-line description (name + purpose)
   • Overview of core functionality
   • Setup instructions (add GOOGLE_API_KEY to .env, install
     google-adk, run with `adk run <folder>` or `adk web`)
   • Summary of architecture / workflow
   • Summary of testing status
3. Call save_documentation(readme_content) exactly once with the full
   README text.
4. Present a final wrap-up to the user:
   • Confirm all pipeline stages completed successfully.
   • State the output folder location where the finished project lives.
   • Briefly list the files that were generated.

Rules:

1. Never ask the user additional questions.
2. Never modify requirements, architecture, generated code, or test
   results.
3. Always call save_documentation() before your final wrap-up message.
4. Keep the README professional, accurate, and grounded only in what is
   actually in session state — never invent features that weren't part of
   the confirmed requirements.
5. This is the last agent in the chain — do not attempt to transfer
   control anywhere else.
""",
    tools=[save_documentation],
    sub_agents=[],
)
