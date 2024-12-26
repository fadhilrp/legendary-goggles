from typing import Annotated, List
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, select
from fastapi_healthz import HealthCheckRegistry, HealthCheckRabbitMQ, health_check_route
from faststream.rabbit.fastapi import RabbitRouter
from pydantic import BaseModel
from src.api.database.models.models import Log
from src.api.database.database import Database
from src.api.rpc_client import DatasetManager, MessageRpcClient
from contextlib import contextmanager

# Initialize components
app = FastAPI()
database = Database()
router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")
dataset_manager = DatasetManager()

# Health checks
_healthChecks = HealthCheckRegistry()
_healthChecks.add(
    HealthCheckRabbitMQ(
        host="rabbitmq",
        port=5672,
        vhost="/",
        username="guest",
        password="guest",
        ssl=False
    )
)


class Incoming(BaseModel):
    m: str


# Session dependency
@contextmanager
def get_session():
    session = database.get_session()
    try:
        yield session
    finally:
        session.close()


def get_db():
    with get_session() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


# Event handlers
@app.on_event("startup")
def on_startup():
    database.create_tables()


# Routes
@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/prompt")
async def create_prompt(inputData: Incoming, session: SessionDep):
    """
    Handle incoming prompts, process them through RPC, and store in database.
    """
    message_rpc = MessageRpcClient()
    prompt = inputData.m

    # Check dataset first
    response = dataset_manager.get_response(prompt)
    if response == "Dataset unavailable.":
        raise HTTPException(status_code=500, detail="Dataset is unavailable.")
    # elif response == "No match found.":
    #     raise HTTPException(status_code=404, detail="No matching prompt found.")

    try:
        # Process through RPC
        print(f"Sending prompt via RPC: {prompt}")
        if response == "No match found.":
            rpc_response = "I don't know how to answer that"
        else:
            rpc_response = message_rpc.call(prompt)
        if rpc_response is None:
            raise HTTPException(
                status_code=500,
                detail=f"No response received for prompt '{prompt}'."
            )
        else:
            print(f"Received response via RPC: {rpc_response}")

        # Store in database
        log = Log(prompt=prompt, rpc_response=rpc_response)
        session.add(log)
        session.commit()
        session.refresh(log)

        return {
            "prompt": prompt,
            "rpc_response": rpc_response,
            "log_id": log.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/logs/")
def read_logs(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
) -> List[Log]:
    logs = session.exec(select(Log).offset(offset).limit(limit)).all()
    return logs


@app.get("/logs/{log_id}")
def read_log(log_id: int, session: SessionDep) -> Log:
    log = session.get(Log, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@app.delete("/logs/{log_id}")
def delete_log(log_id: int, session: SessionDep):
    log = session.get(Log, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    session.delete(log)
    session.commit()
    return {"ok": True}


# Include RabbitMQ router and health check
app.include_router(router)
app.add_api_route('/health', endpoint=health_check_route(registry=_healthChecks))

# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)