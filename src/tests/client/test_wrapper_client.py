import pytest
from unittest.mock import MagicMock
from app.client.wrapper_client import send_prompt
from app.models.request import PromptResponse, Prompt
from app.utils.logger import console_logger

@pytest.fixture
def mock_requests(mocker):
    """Fixture for mocking requests library."""
    return mocker.patch("app.client.wrapper_client.requests")

def test_send_prompt_success(mock_requests):
    """Test send_prompt with a successful response."""
    wrapper_address = "127.0.0.1"
    prompt = "What is AI?"

    # Mocking the response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "answer": "Artificial Intelligence",
        "sci_score": 42
    }
    mock_requests.post.return_value = mock_response

    result = send_prompt(wrapper_address, prompt)

    # Assertions
    assert isinstance(result, PromptResponse)
    assert result.answer == "Artificial Intelligence"
    assert result.sci_score == 42

    mock_requests.post.assert_called_once_with(
        f"http://{wrapper_address}:8000/process_prompt",
        data=Prompt(question=prompt).model_dump_json()
    )

def test_send_prompt_failure(mock_requests):
    """Test send_prompt with a failed response."""
    wrapper_address = "127.0.0.1"
    prompt = "What is AI?"

    # Mocking the response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b"Internal Server Error"
    mock_requests.post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        send_prompt(wrapper_address, prompt)

    # Assertions
    assert "Failed to send prompt" in str(exc_info.value)
    mock_requests.post.assert_called_once_with(
        f"http://{wrapper_address}:8000/process_prompt",
        data=Prompt(question=prompt).model_dump_json()
    )

def test_send_prompt_invalid_response(mock_requests):
    """Test send_prompt with an invalid JSON response."""
    wrapper_address = "127.0.0.1"
    prompt = "What is AI?"

    # Mocking the response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "answer": "Artificial Intelligence"
        # Missing "sci_score"
    }
    mock_requests.post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        send_prompt(wrapper_address, prompt)

    # Assertions
    assert "sci_score" in str(exc_info.value)
    mock_requests.post.assert_called_once_with(
        f"http://{wrapper_address}:8000/process_prompt",
        data=Prompt(question=prompt).model_dump_json()
    )
