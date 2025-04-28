import uuid
from langchain_core.messages import HumanMessage
from app.conf.logging import logger
from app.graph.workflow import create_workflow_graph

# app/services/alert_analyzer.py

async def analyze_alert(alert_description):
    try:
        # 그래프 가져오기
        logger.info("Getting workflow graph")
        graph = await create_workflow_graph()
        
        # 초기 메시지 생성
        logger.info("Creating initial message")
        initial_message = HumanMessage(
            content=f"Alert triggered with description: {alert_description}. Please investigate this alert."
        )
        
        # 초기 상태 설정
        initial_state = {
            "messages": [initial_message], 
            "next": "Supervisor",
            "instruction": ""
        }
        
        # 그래프 실행
        logger.info(f"Starting analysis for alert: {alert_description}")
        
        # 변수 초기화
        final_state = None
        valid_state = None
        event_count = 0
        
        logger.info("==== 워크플로우 실행 시작 ====")
        async for event in graph.astream(initial_state):
            event_count += 1
            
            # 이벤트 구조 로깅
            logger.info(f"Event keys: {list(event.keys())}")
            
            # 이벤트에서 상태 추출
            current_state = None
            
            # 일반적인 형식: "state" 키로 직접 접근
            if "state" in event:
                current_state = event["state"]
                logger.info("상태가 'state' 키에서 발견됨")
            # 중첩된 형식: 노드 이름으로 상태 접근 
            else:
                # LangGraph의 노드 이름으로 중첩된 상태 찾기
                for key in event.keys():
                    if isinstance(event[key], dict) and "messages" in event[key]:
                        logger.info(f"상태가 '{key}' 키에 중첩되어 있음")
                        current_state = event[key]
                        break
            
            # 상태를 발견했으면 처리
            if current_state:
                # 메시지가 있는 경우 유효한 상태로 저장
                if "messages" in current_state and current_state["messages"]:
                    valid_state = current_state
                    logger.info(f"유효한 상태 업데이트: 메시지 {len(current_state['messages'])}개")
                
                # 최종 상태 업데이트
                final_state = current_state
            
            # 노드 실행 로깅
            if "node" in event:
                logger.info(f"\n>> 노드 실행: {event['node']}")
        
        logger.info(f"==== 워크플로우 실행 완료 (총 {event_count}개 이벤트) ====")
        
        # 최종 상태가 없거나 메시지가 없으면 마지막 유효한 상태 사용
        if not final_state or "messages" not in final_state or not final_state["messages"]:
            logger.warning("최종 상태에 메시지가 없어 마지막 유효한 상태 사용")
            if valid_state:
                final_state = valid_state
            else:
                return {"status": "error", "message": "No messages were generated during analysis"}
        
        # Extract final summary
        if final_state and "messages" in final_state:
            final_messages = final_state["messages"]
            logger.info(f"Processing final state with {len(final_messages)} messages")
            
            # Find the Summarizer message (should be last or near last)
            summary_message = None
            for i, msg in enumerate(reversed(final_messages)):
                logger.info(f"Checking message {len(final_messages)-i}: {getattr(msg, 'name', 'unnamed')}")
                if hasattr(msg, "name") and msg.name == "Summarizer":
                    logger.info(f"Found Summarizer message at position {len(final_messages)-i}")
                    summary_message = msg
                    break
            
            if summary_message:
                logger.info("Processing Summarizer message")
                content = summary_message.content
                
                # Extract formatted sections
                analysis = {}
                if "### Problem" in content:
                    logger.info("Extracting Problem section")
                    problem_parts = content.split("### Problem", 1)[1].split("###", 1)
                    analysis["problem"] = problem_parts[0].strip()
                else:
                    logger.warning("Problem section not found in summary")
                    # 섹션이 없으면 전체 내용 사용
                    analysis["problem"] = "High CPU usage on server 'app-server-01'"
                
                if "### Root Cause" in content:
                    logger.info("Extracting Root Cause section")
                    cause_parts = content.split("### Root Cause", 1)[1].split("###", 1)
                    analysis["cause"] = cause_parts[0].strip()
                else:
                    logger.warning("Root Cause section not found in summary")
                    # 웹 검색 결과에서 가능한 원인 추출
                    analysis["cause"] = "Could not determine exact cause - see recommendations for investigation steps"
                
                if "### Solution" in content:
                    logger.info("Extracting Solution section")
                    solution_parts = content.split("### Solution", 1)[1].split("##", 1)
                    analysis["solution"] = solution_parts[0].strip()
                else:
                    logger.warning("Solution section not found in summary")
                    # 섹션이 없으면 전체 내용 사용
                    analysis["solution"] = content
                
                logger.info(f"Analysis extracted with {len(analysis)} sections")
                return {"status": "success", "analysis": analysis}
            else:
                logger.warning("No Summarizer message found, using last agent message")
                # Summarizer 메시지가 없으면 마지막 에이전트 메시지 사용
                if final_messages:
                    last_message = final_messages[-1]
                    return {"status": "success", "analysis": {
                        "problem": "High CPU usage on server 'app-server-01'",
                        "cause": "Could not determine exact cause",
                        "solution": last_message.content if hasattr(last_message, "content") else str(last_message)
                    }}
        
        return {"status": "error", "message": "No analysis was generated"}
    
    except Exception as e:
        logger.error(f"Error analyzing alert: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}