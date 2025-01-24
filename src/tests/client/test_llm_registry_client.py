import pytest
from unittest.mock import MagicMock
from app.models.request import RequestPayload, RequestResponse, RequestStatus
from app.client.llm_registry_client import request_llms, get_llm_request_status, release_llms

@pytest.fixture
def mock_requests(mocker):
    return mocker.patch("app.client.llm_registry_client.requests")

def test_request_llms_success(mock_requests):
    registry_url = "http://localhost:8000"
    request_payload = MagicMock(spec=RequestPayload)
    request_payload.model_dump_json.return_value = '{"mock": "payload"}'

    # Mock the HTTP response with valid fields for RequestResponse
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "requests": [
            {"requestId": "req123", "llmconfig": {"uses_chat_template": True, "model": "gpt2", "modeltyp": "text", "args": {"prompting" : {}, "deployment": {}}}, "status": "waiting", "measurementId": 42}
        ]
    }
    mock_requests.post.return_value = mock_response

    result = request_llms(registry_url, request_payload)

    assert isinstance(result, RequestResponse)
    assert len(result.requests) == 1
    assert result.requests[0].requestId == "req123"
    mock_requests.post.assert_called_once_with(
        registry_url + "/promptingservice/request",
        data=request_payload.model_dump_json(),
    )

def test_request_llms_failure(mock_requests):
    registry_url = "http://localhost:8000"
    request_payload = MagicMock(spec=RequestPayload)
    request_payload.model_dump_json.return_value = '{"mock": "payload"}'
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.content = b"Bad Request"
    mock_requests.post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        request_llms(registry_url, request_payload)

    assert "Failed to request llms" in str(exc_info.value)
    mock_requests.post.assert_called_once()

def test_get_llm_request_status_success(mock_requests):
    registry_url = "http://localhost:8000"
    request_id = "mock-request-id"

    # Mock the HTTP response with valid fields for RequestStatus
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "requestId": "mock-request-id",
        "llmconfig": {"uses_chat_template": True, "model": "gpt2", "modeltyp": "text", "args": {"prompting" : {}, "deployment": {}}},
        "status": "done",
        "measurementId": 42
    }
    mock_requests.get.return_value = mock_response

    result = get_llm_request_status(registry_url, request_id)

    assert isinstance(result, RequestStatus)
    assert result.requestId == "mock-request-id"
    assert result.status == "done"
    mock_requests.get.assert_called_once_with(
        registry_url + f"/promptingservice/request/{request_id}"
    )

def test_get_llm_request_status_failure(mock_requests):
    registry_url = "http://localhost:8000"
    request_id = "mock-request-id"
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b"Not Found"
    mock_requests.get.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        get_llm_request_status(registry_url, request_id)

    assert "Failed to get llm request status" in str(exc_info.value)
    mock_requests.get.assert_called_once()

def test_release_llms_success(mock_requests):
    registry_url = "http://localhost:8000"
    request_id = "mock-request-id"
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_requests.delete.return_value = mock_response

    release_llms(registry_url, request_id)

    mock_requests.delete.assert_called_once_with(
        registry_url + f"/promptingservice/request/{request_id}"
    )

def test_release_llms_failure(mock_requests):
    registry_url = "http://localhost:8000"
    request_id = "mock-request-id"
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b"Internal Server Error"
    mock_requests.delete.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        release_llms(registry_url, request_id)

    assert "Failed to release llms" in str(exc_info.value)
    mock_requests.delete.assert_called_once()
