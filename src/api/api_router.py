from rpc_client import DatasetManager, MessageRpcClient
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from faststream.rabbit.fastapi import RabbitRouter, Logger
# from fastapi_healthz import HealthCheckRegistry, HealthCheckRabbitMQ, health_check_route
from fastapi_healthchecks.api.router import HealthcheckRouter, Probe
from fastapi_healthchecks.checks.rabbit_mq import RabbitMqCheck

router = RabbitRouter("amqp://guest:guest@localhost:5672/")
# _healthChecks = HealthCheckRegistry()
# _healthChecks.add(HealthCheckRabbitMQ(host="localhost", port=5672, vhost="", username="guest", password="guest", ssl=True))
dataset_manager = DatasetManager()

class Incoming(BaseModel):
    m: str


@router.get("/")
def test():
    return {"message": "API is running"}

# class HealthCheck(BaseModel):
#     """Response model to validate and return when performing a health check."""
#
#     status: str = "OK"

# @router.get(
#     "/health",
#     tags=["healthcheck"],
#     summary="Perform a Health Check",
#     response_description="Return HTTP Status Code 200 (OK)",
#     status_code=status.HTTP_200_OK,
#     response_model=HealthCheck,
# )
# def get_health() -> HealthCheck:
#     """
#     ## Perform a Health Check
#     Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
#     to ensure a robust container orchestration and management is in place. Other
#     services which rely on proper functioning of the API service will not deploy if this
#     endpoint returns any other HTTP status code except 200 (OK).
#     Returns:
#         HealthCheck: Returns a JSON response with the health status
#     """
#     return HealthCheck(status="OK")

@router.post('/prompt')
def get_response(inputData: Incoming):
    """
    Handles POST requests to process a prompt and retrieve its response.

    Args:
        inputData (Incoming): The input data containing the prompt.
    Returns:
        dict: A JSON response containing the prompt and corresponding response or an error message.
    """
    message_rpc = MessageRpcClient()
    prompt = inputData.m

    # First, try to retrieve the response from the dataset
    response = dataset_manager.get_response(prompt)

    # If the dataset is unavailable or no match is found, return an error
    if response == "Dataset unavailable.":
        raise HTTPException(status_code=500, detail="Dataset is unavailable.")
    elif response == "No match found.":
        raise HTTPException(status_code=404, detail="No matching prompt found.")

    # If a dataset response is found, send it through the RPC client for further processing
    try:
        print(f"Sending prompt via RPC: {prompt}")
        rpc_response = message_rpc.call(prompt)
        if rpc_response is None:
            raise HTTPException(status_code=500, detail=f"No response received for prompt '{prompt}'.")
        print(f" [.] Received RPC response for prompt '{prompt}': {rpc_response}")
        return {"prompt": prompt, "rpc_response": rpc_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

app = FastAPI()
app.include_router(router)
app.include_router(
    HealthcheckRouter(
        Probe(
            name="readiness",
            checks=[
                # PostgreSqlCheck(host="db.example.com", username=..., password=...),
                # RedisCheck(host="redis.example.com", username=..., password=...),
                RabbitMqCheck(host="localhost", port=5672, user="guest", password="guest", secure=True)
            ],
        ),
        Probe(
            name="liveness",
            checks=[
                ...,
            ],
        ),
    ),
    prefix="/health",
)
