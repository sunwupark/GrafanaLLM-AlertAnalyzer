import asyncio
from fastapi import FastAPI, BackgroundTasks, Request
from app.api.models import AnalysisResponse, HealthCheckResponse
from app.api.endpoints import handle_alert, health_check
from app.graph.workflow import create_workflow_graph
from app.conf.logging import logger

app = FastAPI(
    title="Alert Analyzer",
    description="AI-Powered Alert Analysis System Using Grafana MCP and Large Language Models",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    # 서버 시작 시 워크플로우 그래프 생성
    try:
        logger.info("Initializing workflow graph...")
        await create_workflow_graph()
        logger.info("Workflow graph initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize workflow graph: {e}", exc_info=True)
        # 그래프 초기화 실패는 치명적이므로 서버를 종료
        asyncio.get_event_loop().stop()

# API 라우트 등록
app.post("/alert", response_model=AnalysisResponse)(handle_alert)
app.get("/health", response_model=HealthCheckResponse)(health_check)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)