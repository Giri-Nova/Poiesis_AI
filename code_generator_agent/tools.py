"""
Tools for the Code Generator Agent.

The original design only *instructed* the LLM to "generate" a project but
gave it no way to actually write files to disk. This tool closes that gap:
it takes the three generated file contents and writes them into a real
`output/<Agent_Name>/` folder so later stages (testing, documentation) have
something concrete to validate and finalize.
"""
import os
import re

from google.adk.tools import ToolContext

from common.state_keys import GENERATED_PROJECT

OUTPUT_ROOT = os.getenv("POIESIS_OUTPUT_DIR", "output")


def _sanitize(name: str) -> str:
    """Turn an arbitrary agent name into a safe folder / package name."""
    name = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip())
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "generated_agent"


def write_agent_project(
    tool_context: ToolContext,
    agent_name: str,
    init_content: str,
    env_content: str,
    agent_py_content: str,
) -> dict:
    """
    Write the generated Google ADK agent project to disk as:

        output/<Agent_Name>/__init__.py
        output/<Agent_Name>/.env
        output/<Agent_Name>/agent.py

    Call this exactly once, after you have composed the full contents of
    all three files. The written path is saved to session state so the
    Testing Agent and Documentation Designer Agent can find it.
    """
    folder_name = _sanitize(agent_name)
    project_dir = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(project_dir, exist_ok=True)

    files = {
        "__init__.py": init_content,
        ".env": env_content,
        "agent.py": agent_py_content,
    }

    written = []
    for filename, content in files.items():
        path = os.path.join(project_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)

    tool_context.state[GENERATED_PROJECT] = {
        "agent_folder": folder_name,
        "project_dir": project_dir,
        "files": written,
    }

    return {
        "status": "success",
        "message": f"Project written to {project_dir}",
        "files": written,
    }
