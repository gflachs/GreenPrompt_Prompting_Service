import requests
from app.models.request import RequestPayload, RequestResponse, RequestStatus

from app.utils.logger import console_logger

def request_llms(registry_url: str, request_payload: RequestPayload) -> RequestResponse:
    response = requests.post(registry_url + "/request", json=request_payload.model_dump_json())
    if response.status_code != 200:
        console_logger.error(f"Failed to request llms: {response.text}")
        raise Exception(f"Failed to request llms: {response.text}")
    
    response_json = response.json()
    response = RequestResponse(**response_json)
    return response

def get_llm_request_status(registry_url: str, request_id: str) -> RequestStatus:
    response = requests.get(registry_url + f"/request/{request_id}")
    if response.status_code != 200:
        console_logger.error(f"Failed to get llm request status: {response.text}")
        raise Exception(f"Failed to get llm request status: {response.text}")
    
    response_json = response.json()
    response = RequestStatus(**response_json)
    return response

def release_llms(registry_url: str, request_id: str):
    response = requests.delete(registry_url + f"/request/{request_id}")
    if response.status_code != 204:
        console_logger.error(f"Failed to release llms: {response.text}")
        raise Exception(f"Failed to release llms: {response.text}")