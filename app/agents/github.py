"""
LangChain ReAct Agent
"""
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from app.conf.config import settings
from app.conf.logging import logger
from datetime import datetime, timezone

async def create_github_agent():
    model = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    client = MultiServerMCPClient(
        {
            "github": {
                "command": "/app/github-mcp-server",
                "args": ["stdio"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": settings.GITHUB_TOKEN,
                },
            }
        }
    )

    all_tools = client.get_tools()
    
    # Get repository info from settings
    owner = settings.GITHUB_REPO_OWNER
    repo = settings.GITHUB_REPO_NAME
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # GitHub agent system message with repository info
    github_system_message = f"""
    An alert was triggered for the repository:

    - Repository: {owner}/{repo}
    - Current UTC Time: {current_time}

    Your mission:
    1. Investigate the repository ({owner}/{repo}) ONLY.
    2. Search for:
    - Recent **Issues** related to the alert description.
    - Recent **Pull Requests** that might have introduced related changes.
    - Recent **Commits** that could have caused or fixed something related.
    - **Code Files** that might contain problematic logic related to the alert.
    3. Focus ONLY on data **inside the repository**.
    4. If possible, find:
    - File names and paths
    - Commit hashes
    - Issue/PR numbers and their summaries

    Important Rules:
    - DO NOT perform web search.
    - DO NOT fetch external monitoring data (like Grafana).
    - ONLY use GitHub repository's Issues, PRs, Commits, and Code contents.
    - Validate your findings clearly: why you think they are related to the alert.

    Final Output Format:
    - Issues:
        - Issue Number, Title, Link, Summary
    - Pull Requests:
        - PR Number, Title, Link, Summary
    - Commits:
        - Commit Hash, Message, Link, Related File(s)
    - Code Files:
        - File Path, Extracted Code Snippet (if available)

    Stay focused inside GitHub.
    Do not hallucinate or speculate without evidence from the repository itself.
    """
    
    agent = create_react_agent(
        model, 
        all_tools,
        prompt=github_system_message
    )

    return client, agent
