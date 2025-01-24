import requests
from app.models.request import RequestPayload, RequestResponse, RequestStatus, Prompt, PromptResponse

from app.utils.logger import console_logger

def send_prompt(wrapper_address: str, prompt: str) -> PromptResponse:
    prompt_m = Prompt(question=prompt)
    response = requests.post("http://" + wrapper_address + ":8000/process_prompt", data=prompt_m.model_dump_json())
    if response.status_code != 200:
        console_logger.error(f"Failed to send prompt: {response.content}")
        raise Exception(f"Failed to send prompt: {response.content}")
    else:
        response_json = response.json()
        response = PromptResponse(**response_json)
        return response