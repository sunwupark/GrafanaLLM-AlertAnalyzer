"""
Alarm Analyze Service
"""

from app.core.logging import logger
from app.services.agent import create_analysis_agent, create_analysis_prompt
from app.utils.text import extract_analysis_sections


async def analyze_alert(alert_description):
    try:
        client, agent = await create_analysis_agent()

        prompt = create_analysis_prompt(alert_description)

        request_message = {"messages": [{"content": prompt, "role": "user"}]}

        logger.info("Requesting analysis from agent...")
        async with client:
            response = await agent.ainvoke(request_message)

        logger.info(f"Response structure: {type(response)}")

        if hasattr(response, "structured_response") and response.structured_response:
            analysis_result = {
                "problem": response.structured_response.problem,
                "cause": response.structured_response.cause,
                "solution": response.structured_response.solution,
            }
            logger.info(f"Successfully extracted structured response")
        else:
            logger.info(f"Response: {response}")
            if isinstance(response, dict) and "structured_response" in response:
                structured_resp = response["structured_response"]
                if isinstance(structured_resp, dict):
                    analysis_result = {
                        "problem": structured_resp.get(
                            "problem", "No problem information available"
                        ),
                        "cause": structured_resp.get(
                            "cause", "No cause information available"
                        ),
                        "solution": structured_resp.get(
                            "solution", "No solution information available"
                        ),
                    }
                else:
                    analysis_result = {
                        "problem": getattr(
                            structured_resp,
                            "problem",
                            "No problem information available",
                        ),
                        "cause": getattr(
                            structured_resp, "cause", "No cause information available"
                        ),
                        "solution": getattr(
                            structured_resp,
                            "solution",
                            "No solution information available",
                        ),
                    }
            else:
                logger.warning(
                    "Could not find structured response, falling back to text extraction"
                )
                response_content = str(response)
                analysis_result = extract_analysis_sections(response_content)

        for key in ["problem", "cause", "solution"]:
            if key not in analysis_result or not analysis_result[key]:
                analysis_result[key] = f"No {key} information available"

        return {
            "status": "success",
            "analysis": analysis_result,
            "raw_response": str(response),
        }

    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
