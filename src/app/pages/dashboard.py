import streamlit as st
from app.controllers.db_controller import PromptingServiceDbController
from app.models.internal import Measurement, Request, LLMConfig, Args, LLM_Response

def load_measurements():
    queued_measurements = []
    prompting_measurements = []
    completed_measurements = []
    db_controller = PromptingServiceDbController()
    all_measurements = db_controller.get_measurements()
    for measurement in all_measurements:
        if measurement.status == "deployments_pending":
            queued_measurements.append(measurement)
        elif measurement.status == "prompting":
            prompting_measurements.append(measurement)
        elif measurement.status == "finished":
            completed_measurements.append(measurement)
            
    st.session_state.queued_measurements = queued_measurements
    st.session_state.prompting_measurements = prompting_measurements
    st.session_state.completed_measurements = completed_measurements
    st.session_state.all_measurements = all_measurements

@st.fragment(run_every=20)
def render_dashboard():
    
    load_measurements()
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
        

    
    st.title("Dashboard")
    
    

    st.subheader("Overview")
    st.write(f"Queued Measurements: {len(st.session_state.queued_measurements)}")
    st.write(f"Prompting Measurements: {len(st.session_state.prompting_measurements)}")
    st.write(f"Completed Measurements: {len(st.session_state.completed_measurements)}")

    # Navigation zu anderen Seiten
    st.write("---")
    if st.button("Create New Measurement", key="create_new_measurement"):
        st.session_state.current_page = "New Measurement"
        st.rerun()
    if st.button("View Measurements", key="view_measurements_from_dashboard"):
        st.session_state.current_page = "View Measurements"
        st.rerun()

