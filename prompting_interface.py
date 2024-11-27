from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from requests.exceptions import RequestException
from fastapi.responses import JSONResponse

# Create Fast-API instance
app = FastAPI()

# Input format for the request
class PromptRequest(BaseModel):
    prompt: str
    llm_id: str  # Identifier für den LLM Service

# Expamle registry for LLMs
llm_services = {
    "llm1": "http://machine1.example.com/process",
    "llm2": "http://machine2.example.com/process"
}

# endpoint for prompts
@app.post("/send-prompt/")
async def send_prompt(request: PromptRequest):
    try:
        llm_service_url = llm_services.get(request.llm_id)
        
        if not llm_service_url:
            raise HTTPException(status_code=404, detail=f"LLM Service with ID '{request.llm_id}' not found.")

        response = requests.post(llm_service_url, json={"prompt": request.prompt})

        response.raise_for_status()

        return {"llm_id": request.llm_id, "prompt": request.prompt, "response": response.json()}

    except RequestException as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Error communicating with the LLM Service.", "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred.", "error": str(e)},
        )
