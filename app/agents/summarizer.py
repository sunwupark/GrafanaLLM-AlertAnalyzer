from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from app.conf.config import settings

# app/agents/summarizer.py
class SummaryFormat(BaseModel):
    problem: str = Field(description="Clear description of the alert problem based on the information provided")
    cause: str = Field(description="Root cause analysis based on the investigation findings")
    solution: str = Field(description="Numbered list of specific actionable steps to resolve the issue")

summarizer_system_prompt = """
You are a summary agent tasked with compiling a final alert analysis report.

Create a detailed report based ONLY on the ACTUAL FINDINGS reported by the investigation agents. Your report must include:

1. Problem: Describe the specific alert conditions based on the actual metrics reported by agents
2. Cause: Analyze the root cause based ONLY on evidence found during the investigation
3. Solution: Provide a NUMBERED list of specific actions directly addressing the identified cause

For each solution step, cite the specific finding that justifies the recommendation.

If the investigation did not yield sufficient information in some areas, acknowledge this limitation and recommend specific additional investigation steps as part of the solution.

Format your solution as a numbered list with each item on a new line for better readability.
"""

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", summarizer_system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Create a structured summary of the alert investigation."),
    ]
)

# Create summarizer agent
def create_summarizer_agent():
    model = ChatOpenAI(model=settings.LLM_MODEL, temperature=0)
    return prompt_template | model.with_structured_output(SummaryFormat)