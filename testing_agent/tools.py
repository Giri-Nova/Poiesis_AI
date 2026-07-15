"""
Tools for the Testing Agent.

The original design asked the LLM to "validate" the project purely by
reasoning about it. This adds a real, deterministic validation pass
(file presence, Python syntax check via `ast`, required-component checks,
.env template check) so the pipeline doesn't rely solely on the model's
self-report.
"""
import ast
import os

from google.adk.tools import ToolContext

from common.state_keys import GENERATED_PROJECT, TESTING

REQUIRED_FILES = ["__init__.py", ".env", "agent.py"]


def validate_project(tool_context: ToolContext) -> dict:
    """
    Run automated checks against the project written by the Code Generator
    Agent: required file presence, Python syntax validity, presence of key
    ADK components (root_agent, LlmAgent), and .env template correctness.

    Call this BEFORE save_test_result so your verdict is grounded in real
    findings rather than assumption.
    """
    project = tool_context.state.get(GENERATED_PROJECT)
    if not project:
        return {
            "status": "error",
            "message": "No generated project found in session state.",
        }

    project_dir = project["project_dir"]
    errors = []
    warnings = []

    for filename in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(project_dir, filename)):
            errors.append(f"Missing required file: {filename}")

    agent_py_path = os.path.join(project_dir, "agent.py")
    if os.path.isfile(agent_py_path):
        with open(agent_py_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = None
        try:
            tree = ast.parse(source, filename="agent.py")
        except SyntaxError as e:
            errors.append(f"Syntax error in agent.py: {e}")

        if tree is not None:
            assigned_names = {
                target.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Assign)
                for target in node.targets
                if isinstance(target, ast.Name)
            }
            if "root_agent" not in assigned_names:
                errors.append("agent.py does not define a 'root_agent' variable.")
            if "LlmAgent" not in source:
                warnings.append("agent.py does not appear to use LlmAgent.")
            if not tree.body or not any(
                isinstance(n, (ast.Import, ast.ImportFrom)) for n in tree.body
            ):
                warnings.append("agent.py has no top-level imports — check completeness.")
    else:
        errors.append("agent.py not found; cannot run syntax check.")

    init_py_path = os.path.join(project_dir, "__init__.py")
    if os.path.isfile(init_py_path):
        with open(init_py_path, "r", encoding="utf-8") as f:
            init_source = f.read()
        if "agent" not in init_source:
            warnings.append("__init__.py may not correctly import the agent module.")

    env_path = os.path.join(project_dir, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            env_source = f.read()
        if "GOOGLE_API_KEY" not in env_source:
            errors.append(".env is missing GOOGLE_API_KEY.")
        if "GOOGLE_GENAI_USE_VERTEXAI" not in env_source:
            warnings.append(".env is missing GOOGLE_GENAI_USE_VERTEXAI flag.")

    status = "failed" if errors else "passed"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "project_dir": project_dir,
    }


def save_test_result(
    tool_context: ToolContext,
    status: str,
    validation_report: str,
    errors: list,
    warnings: list,
) -> dict:
    """Persist the final testing verdict into session state for the
    Documentation Designer Agent to use."""
    tool_context.state[TESTING] = {
        "status": status,
        "validation_report": validation_report,
        "errors": errors,
        "warnings": warnings,
    }
    return {"status": "success", "message": "Testing results saved successfully."}
