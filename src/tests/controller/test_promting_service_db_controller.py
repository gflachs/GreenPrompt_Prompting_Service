import pytest
from app.controllers.db_controller import PromptingServiceDbController
from app.models.internal import Measurement, Request, LLM_Response, PromptInput, LLMConfig, Args

@pytest.fixture
def prompting_db_controller(tmp_path, mocker):
    """Fixture for creating a PromptingServiceDbController with a temporary database."""
    db_path = tmp_path / "test_prompting.db"
    mocker.patch("app.utils.configreader.ConfigReader.get_instance", return_value={"database": {"db_name": str(db_path)}})
    controller = PromptingServiceDbController()
    controller.__create_tables__()  # Sicherstellen, dass Tabellen erstellt werden
    yield controller
    controller.db_controller.reset_database()


def test_create_measurement(prompting_db_controller):
    """Test creating a measurement."""
    measurement = prompting_db_controller.create_measurement()
    assert measurement.status == "deployments_pending"
    assert measurement.id > 0

def test_insert_prompt_input(prompting_db_controller):
    """Test inserting a prompt input."""
    measurement = prompting_db_controller.create_measurement()
    prompt_input = PromptInput(prompt="What is AI?", prompttype="general", measurementId=measurement.id)
    prompting_db_controller.insert_prompt_input(prompt_input)
    inputs = prompting_db_controller.get_prompt_inputs_by_measurement_id(measurement.id)
    assert len(inputs) == 1
    assert inputs[0].prompt == "What is AI?"

def test_insert_llm_request(prompting_db_controller):
    """Test inserting an LLM request."""
    measurement = prompting_db_controller.create_measurement()
    llm_config = LLMConfig(
        modeltyp="text-generation",
        model="gpt-3",
        uses_chat_template=False,
        args=Args(prompting={"temperature": 0.7}, deployment={"gpu_enabled": True})
    )
    request = Request(id="test-request", llm_config=llm_config, status="waiting", measurementId=measurement.id, address=None)
    prompting_db_controller.insert_llm_request(request)
    requests = prompting_db_controller.get_requests_by_measurement_id(measurement.id)
    assert len(requests) == 1
    assert requests[0].id == "test-request"

def test_insert_llm_response(prompting_db_controller):
    """Test inserting an LLM response."""
    measurement = prompting_db_controller.create_measurement()
    prompt_input = PromptInput(prompt="What is AI?", prompttype="general", measurementId=measurement.id)
    prompting_db_controller.insert_prompt_input(prompt_input)
    inputs = prompting_db_controller.get_prompt_inputs_by_measurement_id(measurement.id)
    llm_config = LLMConfig(
        modeltyp="text-generation",
        model="gpt-3",
        uses_chat_template=False,
        args=Args(prompting={"temperature": 0.7}, deployment={"gpu_enabled": True})
    )
    llm_response = LLM_Response(
        idPromptInput=inputs[0].id,
        llm_config=llm_config,
        response="Artificial Intelligence is the simulation of human intelligence by machines.",
        sci_score=42.0,
        answer_time_seconds=2.5,
        request_id="test-request"
    )
    prompting_db_controller.insert_llm_response(llm_response)
    responses = prompting_db_controller.get_llm_responses("test-request")
    assert len(responses) == 1
    assert responses[0].response == "Artificial Intelligence is the simulation of human intelligence by machines."

def test_update_llm_request(prompting_db_controller):
    """Test updating an LLM request."""
    measurement = prompting_db_controller.create_measurement()
    llm_config = LLMConfig(
        modeltyp="text-generation",
        model="gpt-3",
        uses_chat_template=False,
        args=Args(prompting={"temperature": 0.7}, deployment={"gpu_enabled": True})
    )
    request = Request(id="test-request", llm_config=llm_config, status="waiting", measurementId=measurement.id, address=None)
    prompting_db_controller.insert_llm_request(request)
    request.status = "prompting"
    request.address = "http://127.0.0.1:8000"
    prompting_db_controller.update_llm_request(request)
    updated_request = prompting_db_controller.get_requests_by_measurement_id(measurement.id)[0]
    assert updated_request.status == "prompting"
    assert updated_request.address == "http://127.0.0.1:8000"

def test_get_measurements_by_status(prompting_db_controller):
    """Test getting measurements by status."""
    prompting_db_controller.create_measurement()  # Default status: deployments_pending
    measurements = prompting_db_controller.get_measurements_by_status("deployments_pending")
    assert len(measurements) == 1
    assert measurements[0].status == "deployments_pending"

def test_clear_all(prompting_db_controller):
    """Test clearing all database entries."""
    prompting_db_controller.create_measurement()
    prompting_db_controller.clear_all()
    measurements = prompting_db_controller.get_measurements()
    assert len(measurements) == 0
