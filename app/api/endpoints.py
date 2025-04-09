"""
API endpoint definition
"""

from datetime import datetime, timezone

from fastapi import BackgroundTasks, FastAPI, Request

from app.api.models import AnalysisResponse, HealthCheckResponse
from app.core.logging import logger
from app.services.alert_analyzer import analyze_alert
from app.services.notification import send_email_alert

app = FastAPI(
    title="Alert Analyzer",
    description="AI-Powered Alert Analysis System Using Grafana MCP and Large Language Models",
    version="1.0.0",
)


@app.post("/alert", response_model=AnalysisResponse)
async def handle_alert(request: Request, background_tasks: BackgroundTasks):
    try:
        alert_data = await request.json()

        alert_description = (
            alert_data.get("alerts", [{}])[0]
            .get("annotations", {})
            .get("description", "No description provided")
        )
        alert_summary = (
            alert_data.get("alerts", [{}])[0]
            .get("annotations", {})
            .get("summary", "No summary provided")
        )

        logger.info(f"Received alert: {alert_summary} - {alert_description}")

        result = await analyze_alert(alert_description)

        if result["status"] == "success" and "analysis" in result:
            background_tasks.add_task(
                send_email_alert, alert_description, result["analysis"]
            )
            logger.info("Analysis completed and email notification queued")

        return result

    except Exception as e:
        logger.error(f"Error processing alert: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
