"""
LangChain ReAct Agent
"""

from datetime import datetime, timezone

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from app.conf.config import settings
from app.conf.logging import logger

async def create_grafana_agent():
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
    
    # Grafana agent를 위한 시스템 지침
    grafana_system_prompt = """
You are a Grafana monitoring agent responsible for investigating alerts. Your job is to:

1. ACTUALLY EXECUTE the necessary queries against Grafana metrics and logs
2. REPORT the SPECIFIC RESULTS you find, including exact values, trends, and patterns
3. ANALYZE these results to determine potential causes
4. ONLY suggest solutions based on actual findings, NOT generic recommendations

For example, instead of saying "Check CPU usage with this query...", you should say:
"I executed the CPU usage query and found that usage peaked at 95% at 14:30, coinciding with..."

If you cannot access certain data, clearly state:
"I attempted to access [specific data] but was unable to because [specific reason]. Based on the data I could access, I found..."

NEVER provide generic instructions without executing them yourself first.
"""
    
    agent = create_react_agent(
        model, 
        all_tools,
        prompt=grafana_system_prompt  # 시스템 메시지 추가
    )

    return client, agent