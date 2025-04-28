from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langchain_tavily import TavilySearch
import os
from app.conf.config import settings

async def create_websearch_agent():
    model = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    
    # 도구를 리스트로 만들기'
    os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
    tavily_tool = TavilySearch(max_results=10)
    tools = [tavily_tool]
    
    # 웹 검색 에이전트를 위한 시스템 프롬프트
    websearch_system_prompt = """
You are a WebSearch agent responsible for finding relevant information about the alert. Your job is to:

1. ACTUALLY SEARCH for specific information related to the alert
2. REPORT actual search results with specific sources and quotes
3. ANALYZE how these findings relate to the current alert
4. ONLY suggest solutions backed by reputable sources

For example, instead of saying "Search for common causes...", you should say:
"I found several reports of similar CPU spikes in the Red Hat Knowledge Base (KB123456) which indicates that..."

If you cannot find specific information, clearly state:
"I searched for [specific terms] but could not find relevant information about [specific aspect]. The most relevant information I found was..."

NEVER provide generic search suggestions without executing the search yourself.
"""
    
    agent = create_react_agent(
        model,
        tools=tools,  # 리스트로 전달
        prompt=websearch_system_prompt
    )
    
    # 다른 에이전트들과 일관성을 유지하기 위해 더미 클라이언트 객체 생성
    dummy_client = None
    
    return dummy_client, agent