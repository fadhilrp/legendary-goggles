from typing import Optional
from sqlmodel import Field, SQLModel

class Log(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt: str = Field(index=True)
    rpc_response: Optional[str] = Field(default=None, index=True)