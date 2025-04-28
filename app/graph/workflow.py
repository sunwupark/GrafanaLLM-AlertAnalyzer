from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, List, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.conf.logging import logger
from app.graph.nodes import create_agent_node
from app.agents.supervisor import create_supervisor_agent, members, options_for_next
from app.agents.grafana import create_grafana_agent
from app.agents.github import create_github_agent
from app.agents.websearch import create_websearch_agent
from app.agents.summarizer import create_summarizer_agent

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation so far"]
    next: str
    instruction: str = ""

# Global graph instance
graph_instance = None

async def create_workflow_graph():
    global graph_instance
    
    if graph_instance is not None:
        return graph_instance
    
    logger.info("Creating workflow graph...")
    
    # 슈퍼바이저 에이전트 생성
    supervisor_agent = create_supervisor_agent()
    
    # 각 전문 에이전트 생성
    _, grafana_agent = await create_grafana_agent()
    _, github_agent = await create_github_agent()
    _, websearch_agent = await create_websearch_agent()

    summarizer_agent = create_summarizer_agent()
    
    # 각 에이전트의 노드 생성
    grafana_node = create_agent_node(grafana_agent, "GrafanaAgent")
    github_node = create_agent_node(github_agent, "GithubAgent")
    websearch_node = create_agent_node(websearch_agent, "WebSearchAgent")

    # 슈퍼바이저 노드 정의
    async def supervisor_node(state: AgentState) -> AgentState:
        logger.info("====== 수퍼바이저 노드 시작 ======")
        
        # 현재 메시지 상태 로깅
        logger.info(f"메시지 수: {len(state['messages'])}")
        
        # 반복 횟수 추적 (state에 iteration_count가 없으면 0으로 초기화)
        iteration_count = state.get("iteration_count", 0) + 1
        logger.info(f"현재 반복 횟수: {iteration_count}")
        
        # 반복 횟수가 10을 초과하면 강제로 SUMMARIZE 단계로 이동
        if iteration_count >= 10:
            logger.warning(f"반복 횟수 {iteration_count}가 한도를 초과하여 강제로 요약 단계로 이동합니다")
            return {
                "messages": state["messages"],
                "next": "SUMMARIZE",
                "instruction": "반복 횟수 제한으로 인해 지금까지의 정보를 종합하여 요약해주세요. 사용 가능한 정보를 기반으로 CPU 사용률 경고에 대한 가능한 원인과 해결책을 제시하세요.",
                "iteration_count": iteration_count
            }
        
        try:
            # 수퍼바이저 에이전트 호출
            logger.info("수퍼바이저 에이전트 호출 중...")
            result = await supervisor_agent.ainvoke({"messages": state["messages"]})
            
            # 결과 로깅
            logger.info(f"수퍼바이저 결정: {result.next}")
            if hasattr(result, "instruction") and result.instruction:
                logger.info(f"다음 에이전트 지시사항: {result.instruction}")
            
            # instruction 필드가 있는 경우 사용, 없으면 빈 문자열 사용
            instruction = getattr(result, "instruction", "")
            
            logger.info("====== 수퍼바이저 노드 완료 ======")
            return {
                "messages": state["messages"],
                "next": result.next,
                "instruction": instruction,
                "iteration_count": iteration_count  # 반복 횟수 상태에 저장
            }
        except Exception as e:
            logger.error(f"수퍼바이저 노드 오류: {str(e)}", exc_info=True)
            # 오류 발생시 요약 단계로 이동
            return {
                "messages": state["messages"],
                "next": "SUMMARIZE",
                "instruction": "오류가 발생했습니다. 지금까지의 정보를 종합하여 요약해주세요.",
                "iteration_count": iteration_count
            }

    # 요약기 노드 정의
    async def summarizer_node(state: AgentState) -> AgentState:
        """
        모든 에이전트의 정보를 종합하여 최종 요약 보고서를 작성하는 노드
        """
        logger.info("Summarizer node started")
        
        # 시스템 메시지 추가하여 요약 작업 지시
        summarize_msg = SystemMessage(content="모든 정보를 종합하여 최종 보고서를 작성해주세요.")
        messages = state["messages"] + [summarize_msg]
        logger.info(f"Summarizer received {len(messages)} messages")
        
        try:
            # 요약기 에이전트 호출
            logger.info("Calling summarizer agent")
            result = await summarizer_agent.ainvoke({"messages": messages})
            logger.info("Summarizer agent returned result")
            
            # 요약 보고서 형식 구성
            summary = (
                f"### Problem\n{result.problem}\n\n"
                f"### Root Cause\n{result.cause}\n\n"
                f"### Solution\n{result.solution}"
            )
            logger.info("Summary created successfully")
            
            summary_message = HumanMessage(content=summary, name="Summarizer")
        
            # 새 상태를 딕셔너리로 직접 생성
            new_state = {
                "messages": state["messages"] + [summary_message],
                "next": "FINISH"
            }
            
            logger.info("Summary created successfully")
            logger.info("Added summary message with name 'Summarizer'")
            logger.info("Summarizer node returning FINISH")
            logger.info(f"New state has {len(new_state['messages'])} messages")
            return new_state
            
        except Exception as e:
            logger.error(f"Error in summarizer node: {e}", exc_info=True)
            # 오류가 발생해도 워크플로우를 종료하도록 함
            return {
                "messages": state["messages"] + [
                    HumanMessage(content=f"Error generating summary: {str(e)}", name="Summarizer")
                ],
                "next": "FINISH"
            }
    
    # 그래프 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("GrafanaAgent", grafana_node)
    workflow.add_node("GithubAgent", github_node)
    workflow.add_node("WebSearchAgent", websearch_node)
    workflow.add_node("Summarizer", summarizer_node)  # 요약기 노드 추가
    
    # 각 에이전트에서 슈퍼바이저로 엣지 추가
    for member in members:
        workflow.add_edge(member, "Supervisor")
    
    # 조건부 엣지 맵 생성
    conditional_map = {member: member for member in members}
    conditional_map["SUMMARIZE"] = "Summarizer"  # "SUMMARIZE"가 "Summarizer" 노드로 연결되도록 추가
    conditional_map["FINISH"] = END
    
    def get_next(state):
        return state["next"]
    
    # 슈퍼바이저에서 조건부 엣지 추가
    workflow.add_conditional_edges("Supervisor", get_next, conditional_map)
    
    # 시작 노드 설정
    workflow.add_edge(START, "Supervisor")
    
    # # 체크포인터 설정 - configurable=True로 설정
    # memory_saver = MemorySaver(configurable=True)
    
    # 그래프 컴파일
    compiled_graph = workflow.compile()
    
    # 글로벌 인스턴스 설정
    graph_instance = compiled_graph
    
    logger.info("Workflow graph created successfully")
    
    return compiled_graph