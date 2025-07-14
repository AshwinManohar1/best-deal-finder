# main.py

from fastapi import FastAPI, HTTPException
from agent.orchestrator import AgentOrchestrator
from common.requests import StartRequest, StartResponse
from common.logger import get_logger
# --- App Initialization ---
app = FastAPI(
    title="Best Deal Finder API",
    description="An API to find the best price for a product.",
    version="0.1.0",
)

logger = get_logger(__name__)

# --- API Endpoints ---
@app.post("/agent/best-deal/start", response_model=StartResponse)
async def start_best_deal_agent(
    request: StartRequest
):
    """
    Starts a new shopping agent job in the background.
    """
    try:
        logger.info(f"Received request for product: {request.product_name}")
        orchestrator = AgentOrchestrator(request.product_name)
        result = orchestrator.run()
        logger.info(f"Agent result: {result}")

        response = StartResponse(result=result["final_answer"])
        logger.info(f"Returning response: {response}")
        return response
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
