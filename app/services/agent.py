"""
LangChain ReAct Agent
"""

from datetime import datetime, timezone

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger


class ResponseFormat(BaseModel):
    problem: str = Field(description="Current Problem of the Alert")
    cause: str = Field(description="Cause of the Problem")
    solution: str = Field(description="Solution to the Problem")


async def create_analysis_agent():
    model = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    client = MultiServerMCPClient(
        {
            "grafana": {
                "command": "/app/mcp-grafana",
                "args": [],
                "env": {
                    "GRAFANA_URL": settings.GRAFANA_URL,
                    "GRAFANA_API_KEY": settings.GRAFANA_API_KEY,
                },
            }
        }
    )

    all_tools = client.get_tools()
    # except list_datasources, cause currently it does not work
    fixed_tools = [tool for tool in all_tools if tool.name != "list_datasources"]

    agent = create_react_agent(model, fixed_tools, response_format=ResponseFormat)

    return client, agent


def create_analysis_prompt(alert_description):
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    prompt = f"""
        An alert was triggered with the following description: {alert_description}.

        The current time is: {current_time}.

        Your task is to:
        1. Retrieve all available data sources and identify their UIDs.
        2. For each data source, ensure you have gathered the necessary `name`, `label`, `metadata`, or other required information before using a tool. Avoid using non-existent or incorrect inputs by thoroughly checking the `properties.description` and `properties` of each tool.
        3. Query the last 1 hour of data from each data source, using the current time as the endpoint and calculating the start time accordingly.
        4. IMPORTANT: When working with Prometheus metrics that involve division (calculating rates, percentages, etc.), always check if the denominator could be zero. If it might be zero, use a conditional approach or the 'or' operator to provide a safe default value. This prevents NaN results and false alerts.
        5. If issues are detected, use the appropriate tools to gather more information.
        6. Ensure that all tools are used effectively and accurately. Before making any request, verify the available inputs and only use valid data.
        7. Provide a structured report using the following format:

        Problem:
        Cause of Problem:
        Solution:
        
        8. MOST IMPORTANT!! : Always validate the inputs using the `properties.description` of the tools before making any requests.
        """

    return prompt
