# Documentation

## `rpc_server.py`
### Purpose
This file implements a RabbitMQ RPC server that handles message processing by matching prompts against a dataset and returning corresponding responses. It's designed to work with a prompt engineering dataset and provide response matching capabilities.

### Key Components
- Uses RabbitMQ for message queuing
- Reads from a prompt engineering dataset (CSV)
- Implements error handling and logging
- Provides response matching functionality

### Usage
The server can be started directly using Python: `python rpc_server.py`. It will:
1. Load the prompt engineering dataset
2. Establish connection to RabbitMQ
3. Listen for incoming RPC requests
4. Process messages and return matching responses

## `api_router.py`
### Purpose
This file implements a FastAPI application that serves as the main API interface, handling prompt processing, database operations, and health monitoring. It integrates with RabbitMQ for message processing and maintains a log of all operations.

### Key Components
| Component | Description |
|-----------|-------------|
| FastAPI App | Main application server |
| Database Integration | Handles storage and retrieval of logs |
| RabbitMQ Router | Manages message routing |
| Health Checks | Monitors system health |
| Dataset Manager | Handles prompt-response matching |

### Endpoints
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Root endpoint to check API status |
| `/prompt` | POST | Process new prompts and store results |
| `/logs/` | GET | Retrieve logs with pagination |
| `/logs/{log_id}` | GET | Retrieve specific log entry |
| `/logs/{log_id}` | DELETE | Delete specific log entry |
| `/health` | GET | Check system health status |

## `simu.py`
### Purpose
This file provides a simulation tool for testing the system by sending prompts from the dataset to the API endpoint. It's useful for load testing and system verification.

### Usage
Run using: `python simu.py`
- Loads the prompt engineering dataset
- Iterates through all prompts
- Sends each prompt to the API endpoint
- Handles and reports any errors

### Requirements
- Dataset must be available at the specified path
- API server must be running and accessible
- Proper network connectivity to API endpoint

## `rpc_client.py`
### Purpose
This file implements the RPC client functionality and dataset management capabilities. It provides two main classes: `DatasetManager` for handling the prompt-response dataset, and `MessageRpcClient` for RPC communication.

### Classes
#### DatasetManager
| Method | Arguments | Description |
|--------|-----------|-------------|
| `__init__` | `path` (str, optional) | Initializes with dataset path. Default: 'components/prompt_engineering_dataset.csv' |
| `get_response` | `m` (str) | Returns matching response for given prompt |

#### MessageRpcClient
| Method | Arguments | Description |
|--------|-----------|-------------|
| `__init__` | None | Initializes RabbitMQ connection and channel |
| `call` | `m` (str) | Sends RPC request and waits for response |
| `on_response` | Internal | Callback handler for RPC responses |

### Error Handling
Both classes implement comprehensive error handling for:
- Connection failures
- Channel errors
- Dataset loading issues
- Message publishing problems
- Response timeout scenarios

### Usage
```python
# Dataset Manager usage
dataset_manager = DatasetManager()
response = dataset_manager.get_response("some prompt")

# RPC Client usage
rpc_client = MessageRpcClient()
response = rpc_client.call("some message")
```