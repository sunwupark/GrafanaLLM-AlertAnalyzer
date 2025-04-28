from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal
from app.conf.config import settings

# Supervisor data
members = ["GithubAgent", "GrafanaAgent", "WebSearchAgent"]
options_for_next = ["FINISH", "SUMMARIZE"] + members

# Supervisor response model
class SupervisorRouteResponse(BaseModel):
    next: Literal[*options_for_next]
    instruction: str = Field(description="Instructions for the next agent")  # default 제거하고 Field로 변경

# Supervisor prompt
system_prompt = """
You are a supervisor coordinating an alert investigation using multiple specialized agents ({members}). Your role is to:

1. Direct the most appropriate agent to investigate specific aspects of the alert
2. Provide clear, actionable instructions to each agent you select
3. Require agents to EXECUTE their investigation and report ACTUAL RESULTS, not just suggestions
4. Proceed to SUMMARIZE only when sufficient concrete data has been collected

When agents return with findings, evaluate if the investigation is complete or requires additional information. Direct follow-up queries as needed.

Agents must provide concrete evidence and actual execution results. If an agent returns generic advice without execution, instruct them to complete their investigation properly.

Respond with SUMMARIZE when enough actual data has been collected to analyze the alert comprehensively.
Respond with FINISH when the full investigation and reporting process is complete.
"""

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Given the above conversation, decide who should act next (options: {options}) and provide specific instructions for that agent."),
    ]
).partial(options=str(options_for_next), members=", ".join(members))

# Create supervisor agent
def create_supervisor_agent():
    model = ChatOpenAI(model=settings.LLM_MODEL, temperature=0)
    return prompt_template | model.with_structured_output(SupervisorRouteResponse)