from pydantic import BaseModel
from typing import List
# Define Pydantic model for queries and their types
class QueryItem(BaseModel):
    query: str
    query_type: str  # Either "query" or "prediction"

class DispatcherResponse(BaseModel):
    Questions: List[QueryItem]
    