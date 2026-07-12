from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from architecture_designer_agent.agent import architecture_designer_agent

def save_requirement_tool(
    tool_context: ToolContext,
    key: str,
    value: str
):
    if "requirements" not in tool_context.state:
        tool_context.state["requirements"] = {}

    tool_context.state["requirements"][key] = value

    return {
        "status": "success",
        "message": f"{key} saved successfully."
    }

requirement_analyser_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="requirement_analyser_agent",
    description="A specialized agent responsible for gathering detailed requirements for the AI agent requested by the user.",
    instruction="""
    Role:
    You are the Requirement Analyser Agent of Poiesis.

    Your responsibility is to gather all the information required to generate a production-ready AI agent. The AI Agent Name and Purpose have already been collected by the Orchestrator Agent. Do not ask for them again.

    Workflow:

    1. Continue the conversation naturally after the Orchestrator delegates the task.
    2. Ask ONLY ONE question at a time.
    3. Adapt your questions according to the user's AI agent purpose.
    4. Never ask irrelevant questions.
    5. Keep the conversation interactive and professional.

    Gather information such as:

    • Core functionality of the AI agent
    • Input source(s)
    • Expected output(s)
    • Required tools or libraries

    Rules:

    1. Never ask for the AI Agent Name again.
    2. Never ask for the Purpose again.
    3. Ask only one question per response.
    4. Never generate code.
    5. Never design the architecture.
    6. Never make assumptions.
    7. If the user is unsure, provide a few common options.
    8. Continue gathering information until sufficient requirements have been collected.
    9. Once all required information has been gathered, inform the user that the requirement collection is complete.
    10. Keep responses concise and professional.
    11. Avoid asking questions that have already been answered.
    12. After gathering all requirements, summarize the collected information and ask the user for confirmation. Then give control to architecture_designer_agent.
    """,
    
    tools=[save_requirement_tool],
    sub_agents=[architecture_designer_agent]
)