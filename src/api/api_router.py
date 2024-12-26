from fastapi import FastAPI, HTTPException
from fastapi_healthz import HealthCheckRegistry, HealthCheckRabbitMQ, health_check_route
from faststream.rabbit.fastapi import RabbitRouter
from pydantic import BaseModel

from rpc_client import DatasetManager, MessageRpcClient

router = RabbitRouter("amqp://guest:guest@localhost:5672/")
_healthChecks = HealthCheckRegistry()
_healthChecks.add(HealthCheckRabbitMQ(host="localhost", port=5672, vhost="/", username="guest", password="guest", ssl=False))
dataset_manager = DatasetManager()

class Incoming(BaseModel):
    m: str


@router.get("/")
def test():
    return {"message": "API is running"}

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
app.add_api_route('/health', endpoint=health_check_route(registry=_healthChecks))
