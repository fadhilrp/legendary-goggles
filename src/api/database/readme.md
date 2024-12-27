# Documentation

## `database.py`
### Purpose
This file implements a SQLModel-based database connection manager that handles SQLite database operations. It provides a simple interface for creating database sessions and managing database tables.

### Class: Database
| Method | Arguments | Description |
|--------|-----------|-------------|
| `__init__` | `sqlite_url` (str, optional) | Initializes database engine. Default URL: "sqlite:///database.db". Sets up connection with thread-safe settings. |
| `create_tables` | None | Creates all tables defined by SQLModel metadata |
| `get_session` | None | Returns a new database session |

### Usage
```python
# Initialize database
db = Database()

# Create tables
db.create_tables()

# Get a session for database operations
with db.get_session() as session:
    # Perform database operations
    pass
```

### Key Features
- SQLite database support with thread-safe configuration
- Session management
- Automatic table creation
- Connection pooling through SQLModel/SQLAlchemy

## `models.py`
### Purpose
This file defines the database models using SQLModel, specifically the Log model for storing prompt-response pairs. It provides the structure for the database tables and defines the schema for storing interaction logs.

### Class: Log
| Field | Type | Description |
|-------|------|-------------|
| `id` | Optional[int] | Primary key, auto-incrementing identifier |
| `prompt` | str | The input prompt, indexed for faster queries |
| `rpc_response` | Optional[str] | The response from RPC server, nullable and indexed |

### Schema Details
- All fields are indexed for optimized query performance
- `id` is automatically managed by the database
- `rpc_response` is optional to handle cases where RPC calls fail
- Both `prompt` and `rpc_response` fields are searchable through database indices

### Usage
```python
# Create a new log entry
log = Log(
    prompt="example prompt",
    rpc_response="example response"
)

# Using with database session
with db.get_session() as session:
    session.add(log)
    session.commit()
    session.refresh(log)
```

### Integration
The Log model is used primarily by the API router (`api_router.py`) to:
1. Store new prompt-response pairs
2. Query existing logs
3. Delete log entries
4. Retrieve specific log entries by ID

### Database Schema
```sql
CREATE TABLE log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    rpc_response TEXT,
    INDEX idx_prompt (prompt),
    INDEX idx_rpc_response (rpc_response)
);
```