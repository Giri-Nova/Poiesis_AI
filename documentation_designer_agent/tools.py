"""
Tools for the Documentation Designer Agent.

This agent did not exist in the original code even though every other
agent's instructions referenced it as the final handoff target. It writes
the closing artifacts into the generated project's output folder:
README.md and a full pipeline build report.
"""
import os

from google.adk.tools import ToolContext

from common.state_keys import (
    AI_NAME,
    PURPOSE,
    REQUIREMENTS,
    ARCHITECTURE,
    GENERATED_PROJECT,
    TESTING,
    DOCUMENTATION,
)


def save_documentation(tool_context: ToolContext, readme_content: str) -> dict:
    """
    Write the final README.md into the generated project's output folder,
    plus a POIESIS_BUILD_REPORT.md summarizing the full pipeline (requirements,
    architecture, and testing results) pulled from session state.

    Call this once, after composing the full README content.
    """
    project = tool_context.state.get(GENERATED_PROJECT)
    if not project:
        return {
            "status": "error",
            "message": "No generated project found in session state.",
        }

    project_dir = project["project_dir"]

    readme_path = os.path.join(project_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    summary_lines = [
        f"# Poiesis Build Report — {tool_context.state.get(AI_NAME, 'Unnamed Agent')}",
        "",
        f"**Purpose:** {tool_context.state.get(PURPOSE, 'N/A')}",
        "",
        "## Requirements",
        str(tool_context.state.get(REQUIREMENTS, {})),
        "",
        "## Architecture",
        str(tool_context.state.get(ARCHITECTURE, {})),
        "",
        "## Testing",
        str(tool_context.state.get(TESTING, {})),
    ]
    summary_path = os.path.join(project_dir, "POIESIS_BUILD_REPORT.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    tool_context.state[DOCUMENTATION] = {
        "readme_path": readme_path,
        "summary_path": summary_path,
    }

    return {
        "status": "success",
        "message": f"Documentation written to {project_dir}",
        "files": [readme_path, summary_path],
    }
