# main.py

import time
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from agent.orchestrator import AgentOrchestrator
from llm_client import get_llm_response


# --- App Initialization ---
app = FastAPI(
    title="Shopping Agent API",
    description="An API to find the best price for a product.",
    version="0.1.0",
)

# --- In-Memory Job Store (for simplicity, replace with Redis later) ---
# This dictionary will act as our database for now.
jobs = {}

# --- Pydantic Models for Data Validation ---
class StartRequest(BaseModel):
    product_name: str = Field(
        ...,
        description="The name of the product to search for.",
        examples=["Sony WH-1000XM5 headphones"],
    )

class StartResponse(BaseModel):
    job_id: str = Field(..., description="The unique ID for this search job.")

class StatusResponse(BaseModel):
    job_id: str
    status: str
    request: StartRequest
    result: dict | None = None
    intermediate_steps: list[str] = []


# --- Placeholder Agent Logic ---
# This function simulates the work of the agent.
# Later, we will replace this with our actual agent orchestrator loop.
def run_agent_task(job_id: str, product_name: str):
    """
    This is the actual agent task that runs the orchestrator.
    """
    print(f"Starting agent for job_id: {job_id} to find '{product_name}'")
    jobs[job_id]["status"] = "RUNNING"


    def job_updater(key, value):
        if key == "intermediate_steps":
            jobs[job_id][key].append(value)
        else:
            jobs[job_id][key] = value

    try:
        orchestrator = AgentOrchestrator(product_name, job_updater)
        result = orchestrator.run()

        # Update the job with the final result
        job_updater("result", result)
        job_updater("status", "COMPLETED")
        print(f"Finished agent for job_id: {job_id}")

    except Exception as e:
        print(f"🔴 Agent task failed for job_id: {job_id} with error: {e}")
        job_updater("result", {"error": str(e)})
        job_updater("status", "FAILED")



# --- API Endpoints ---
@app.post("/agent/shopping/start", response_model=StartResponse)
async def start_shopping_agent(
    request: StartRequest, background_tasks: BackgroundTasks
):
    """
    Starts a new shopping agent job in the background.
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "PENDING",
        "request": request,
        "result": None,
        "intermediate_steps": [],
    }

    # Add the long-running agent task to the background
    background_tasks.add_task(run_agent_task, job_id, request.product_name)

    return {"job_id": job_id}


@app.get("/agent/shopping/status/{job_id}", response_model=StatusResponse)
async def get_shopping_agent_status(job_id: str):
    """
    Retrieves the status and result of a shopping agent job.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job