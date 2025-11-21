from typing import Dict, Any
from pydantic import BaseModel, Field

class PortfolioItem(BaseModel):
    """"""
    
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory = dict)