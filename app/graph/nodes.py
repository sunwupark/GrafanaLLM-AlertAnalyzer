import functools
from langchain_core.messages import HumanMessage, SystemMessage

# app/graph/nodes.py
import json
from app.conf.logging import logger

async def agent_node(state, agent, name):
    """
    지정한 agent와 name을 사용하여 agent 노드를 생성
    """
    logger.info(f"====== {name} 시작 ======")
    logger.info(f"입력 메시지 수: {len(state['messages'])}")
    
    # 입력의 마지막 메시지 내용 로깅
    if state["messages"]:
        last_msg = state["messages"][-1]
        last_msg_content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        logger.info(f"마지막 메시지: {last_msg_content[:200]}...")
    
    # 지시사항 로깅
    if "instruction" in state and state["instruction"]:
        logger.info(f"지시사항: {state['instruction']}")
    
    try:
        # 에이전트 호출
        logger.info(f"{name} 에이전트 호출 중...")
        agent_response = await agent.ainvoke({"messages": state["messages"]})
        
        # 응답 로깅
        if "messages" in agent_response and agent_response["messages"]:
            response_msg = agent_response["messages"][-1]
            response_content = response_msg.content if hasattr(response_msg, "content") else str(response_msg)
            logger.info(f"{name} 응답: {response_content[:300]}...")
        else:
            logger.warning(f"{name} 응답에 메시지가 없음")
        
        # 에이전트 응답 메시지를 가져와서 태그 추가
        new_message = HumanMessage(content=agent_response["messages"][-1].content, name=name)
        
        # 전체 상태 복사하고 메시지 업데이트
        new_state = state.copy()  # 상태 복사
        new_state["messages"] = state["messages"] + [new_message]  # 메시지 업데이트
        
        logger.info(f"====== {name} 완료 ======")
        return new_state  # 전체 상태 반환
        
    except Exception as e:
        logger.error(f"{name} 에이전트 오류: {str(e)}", exc_info=True)
        # 오류 발생 시 오류 메시지를 포함한 상태 반환
        new_state = state.copy()
        new_state["messages"] = state["messages"] + [
            HumanMessage(content=f"Error in {name}: {str(e)}", name=name)
        ]
        return new_state

def create_agent_node(agent, name):
    """
    Agent와 name을 사용하여 노드 생성 함수
    """
    return functools.partial(agent_node, agent=agent, name=name)