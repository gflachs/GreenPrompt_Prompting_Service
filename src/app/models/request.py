from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Args(BaseModel):
    prompting: Dict[str, Any]  
    deployment: Dict[str, Any]  

class LLMConfig(BaseModel):
    huggingface_url: str = Field(..., pattern="^https?://", description="Must be a valid URL")
    model: str = Field(..., min_length=1, description="Model name cannot be empty")
    args: Args  

class RequestPayload(BaseModel):
    llms: List[LLMConfig] 
    measurementId: int = Field(..., gt=0, description="Measurement ID must be positive")
    
class RequestSingleResponse(BaseModel):
    llmconfig: LLMConfig
    requestId: str = Field(..., description="Request ID must be provided")
    
class RequestResponse(BaseModel):
    requests: List[RequestSingleResponse]
    
class RequestStatus(BaseModel):
    requestId: str = Field(..., description="Request ID must be provided")
    llmconfig : LLMConfig
    status: str = Field(..., description="Status must be provided")
    measurementId: int = Field(..., gt=0, description="Measurement ID must be positive")
    address : str = Field(None, description="Address can be empty")
