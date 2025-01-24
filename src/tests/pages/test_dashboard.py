import os
import pytest
from unittest.mock import MagicMock
from app.controllers.db_controller import PromptingServiceDbController
from app.models.internal import Measurement
from streamlit.runtime.scriptrunner import ScriptRunContext
import streamlit as st

@pytest.fixture
def mock_db_controller(mocker):
    """Mock PromptingServiceDbController."""
    mock_controller = mocker.patch("app.pages.dashboard.PromptingServiceDbController")
    mock_instance = mock_controller.return_value
    mock_instance.get_measurements.return_value = [
        Measurement(id=1, status="deployments_pending"),
        Measurement(id=2, status="prompting"),
        Measurement(id=3, status="finished"),
    ]
    return mock_instance

@pytest.fixture
def mock_db_controller1(mocker):
    """Mock PromptingServiceDbController."""
    mock_controller = mocker.patch("streamlit_app.PromptingServiceDbController")
    mock_instance = mock_controller.return_value
    mock_instance.get_measurements.return_value = [
        Measurement(id=1, status="deployments_pending"),
        Measurement(id=2, status="prompting"),
        Measurement(id=3, status="finished"),
    ]
    return mock_instance

def test_load_measurements(mock_db_controller):
    """Test the load_measurements function."""
    # Reset session state before testing
    st.session_state.clear()
    
    # Call the function
    from app.pages.dashboard import load_measurements
    load_measurements()

    # Validate session state
    assert len(st.session_state.queued_measurements) == 1
    assert len(st.session_state.prompting_measurements) == 1
    assert len(st.session_state.completed_measurements) == 1
    assert len(st.session_state.all_measurements) == 3

import streamlit as st
from app.pages.dashboard import render_dashboard
from streamlit.testing.v1 import AppTest 

def test_render_dashboard(mock_db_controller, mock_db_controller1):
    """Test the render_dashboard function using Streamlit's TestClient."""
     # Dynamischer Pfad zur dashboard.py
  # Projektroot dynamisch finden (relativ zu dieser Datei)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    app_path = os.path.join(project_root, "streamlit_app.py")

    # Überprüfen, ob die Datei existiert
    assert os.path.exists(app_path), f"Die Datei {app_path} existiert nicht."

    # Mit Streamlit AppTest laden
    client = AppTest.from_file(app_path)
    
    # Set initial session state
    client.session_state.queued_measurements = [{"id": 1, "status": "deployments_pending"}]
    client.session_state.prompting_measurements = [{"id": 2, "status": "prompting"}]
    client.session_state.completed_measurements = [{"id": 3, "status": "finished"}]
    
    
    # Run the app and capture the output
    client.run(timeout=100)
    
   
    # Validate the output
    print(client.get("title"))
    assert client.title[0].value == "Dashboard"
    assert client.button[0].label == "Create New Measurement"
    assert client.button[1].label == "View Measurements"

    assert client.text[0].value == "Queued Measurements: 1"
    assert client.text[1].value == "Prompting Measurements: 1"
    assert client.text[2].value == "Completed Measurements: 1"

