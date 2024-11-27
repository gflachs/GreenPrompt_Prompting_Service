from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from requests.exceptions import RequestException
from fastapi.responses import JSONResponse

# FastAPI-Instanz erstellen
app = FastAPI()

# Eingabeformat für die Anfrage
class PromptRequest(BaseModel):
    prompt: str
    llm_id: str  # Identifier für den LLM Service

# Beispiel-Registry für LLM-Services
llm_services = {
    "llm1": "http://machine1.example.com/process",
    "llm2": "http://machine2.example.com/process"
}

# Endpoint zur Verarbeitung des Prompts
@app.post("/send-prompt/")
async def send_prompt(request: PromptRequest):
    try:
        # URL des LLM-Services aus der Registry abrufen
        llm_service_url = llm_services.get(request.llm_id)
        
        if not llm_service_url:
            raise HTTPException(status_code=404, detail=f"LLM Service with ID '{request.llm_id}' not found.")

        # HTTP-POST-Anfrage an den entsprechenden LLM-Service senden
        response = requests.post(llm_service_url, json={"prompt": request.prompt})

        # Überprüfen, ob die Anfrage erfolgreich war
        response.raise_for_status()

        # Antwort des LLM-Service zurückgeben
        return {"llm_id": request.llm_id, "prompt": request.prompt, "response": response.json()}

    except RequestException as e:
        # Fehler beim HTTP-Request behandeln
        return JSONResponse(
            status_code=500,
            content={"detail": "Error communicating with the LLM Service.", "error": str(e)},
        )
    except Exception as e:
        # Allgemeine Fehlerbehandlung
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred.", "error": str(e)},
        )
