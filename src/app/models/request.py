from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.models.internal import Args, LLMConfig

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
    address : str |  None = Field(None, description="Address must be provided")

class PromptResponse(BaseModel):
    answer: str = Field(..., description="The llm's answer to a previously asked question.")
    sci_score: int = Field(..., description="A numerical value as a representation of the sci score as a representation of the energy consumption and the associated CO2 emissions generated during the processing of the prompt and the creation of the answer.")

class Prompt(BaseModel):
    question: str = Field(..., description="A string formatted question which is to be answered by the llm while measuring the energy consumption needed to generate the answer")