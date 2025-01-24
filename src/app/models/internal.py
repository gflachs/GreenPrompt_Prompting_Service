from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Args(BaseModel):
    prompting: Dict[str, Any]  
    deployment: Dict[str, Any]  

class LLMConfig(BaseModel):
    modeltyp: str = Field(..., min_length=1, description="Model type cannot be empty")
    model: str = Field(..., min_length=1, description="Model name cannot be empty")
    uses_chat_template: bool = Field(..., description="Uses chat template must be provided")
    args: Args  

class Measurement(BaseModel):
    id: int = Field(..., gt=0, description="ID must be positive")
    status: str = Field(..., description="Status must be provided")
    
class Request(BaseModel):
    #uuid
    id: str = Field(..., description="ID must be provided")
    llm_config : LLMConfig
    status: str = Field(..., description="Status must be provided")
    measurementId: int = Field(..., gt=0, description="Measurement ID must be positive")
    address : str |  None = Field(None, description="Address must be provided")
    
class LLM_Response(BaseModel):
    id: int | None = Field(None, gt=0, description="ID must be positive")
    llm_config : LLMConfig
    idPromptInput : int = Field(..., gt=0, description="ID Prompt Input must be positive")
    response : str | None = Field(None, description="Response must be provided")
    sci_score : float | None = Field(None, description="Sci score must be provided")
    answer_time_seconds : float | None = Field(None, description="Answer time seconds must be provided")
    request_id : str = Field(..., description="Request ID must be provided")
    
class LLM_Response_Full(LLM_Response):
    prompt : str = Field(..., description="Prompt must be provided")
    prompttype : str = Field(..., description="Prompt type must be provided")

class PromptInput(BaseModel):
    id : int | None = Field(None, gt=0, description="ID must be positive")
    prompt : str = Field(..., description="Prompt must be provided")
    prompttype : str = Field(..., description="Prompt type must be provided")
    measurementId : int = Field(..., gt=0, description="ID must be positive")