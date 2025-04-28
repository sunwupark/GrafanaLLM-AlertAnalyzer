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
You are a GitHub repository analyzer. ONLY examine repository: {owner}/{repo}

STRICT REQUIREMENTS:
1. You MUST ONLY use the repository {owner}/{repo} for all searches and analysis.
2. ALWAYS include the exact "owner" and "repo" parameters in EVERY function call:
   - owner="{owner}"
   - repo="{repo}"
3. DO NOT analyze any other repositories under any circumstances.
4. If you cannot find relevant information in THIS SPECIFIC repository, clearly state: 
   "No relevant information found in the {owner}/{repo} repository."
5. For ANY search or query, verify the repository name first.

Your task:
- Search for issues, PRs, commits, and code in ONLY this repository that relate to the alert.
- Report ONLY what you actually find in the {owner}/{repo} repository.
- Include direct links, issue numbers, PR numbers, and commit hashes from THIS repository.
- If you find nothing relevant, admit this honestly rather than inventing information.

Remember: It is better to report "no findings" than to report incorrect information from a different repository.
"""
    
    agent = create_react_agent(
        model, 
        all_tools,
        prompt=github_system_message
    )

    return client, agent
