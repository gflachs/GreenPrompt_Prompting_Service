import streamlit as st
from app.client.llm_registry_client import get_llm_request_status
from app.controllers.db_controller import PromptingServiceDbController
import pandas as pd


def show_chat(requestId):
    chat = load_request_chat(requestId)
    for message in chat:
        with st.chat_message("user"):
            st.write(message.prompt)
        with st.chat_message("bot"):
            st.caption(f"Sci_Score: {message.sci_score} | Time: {message.answer_time_seconds} s")
            st.write(message.response)
    

@st.fragment(run_every=20)
def render_measurement_requests(measurement):
    load_measurement_requests(measurement.id)
    for request in st.session_state.current_measurement_requests:
        st.write("---")
        st.caption(f"Request ID: {request.id}")
        st.write(f"Status: {request.status}")
        st.write(f"Config:")
        st.json(request.llm_config.model_dump_json())
        st.write(f"Address: {request.address}")
        if st.button(f"Show Chat", key=f"show_chat_{request.id}"):
            show_chat(request.id)
        st.write("---")
            

def render_view_measurements():
    
    st.title("View Measurements")
    for measurement in st.session_state.all_measurements:
        st.subheader(f"Measurement ID: {measurement.id}")
        if measurement.status == "finished":            
            st.download_button(label="Download Results", data=download_measurement_results(measurement.id), file_name=f"measurement_{measurement.id}.csv", mime="text/csv")
        st.write(f"Status: {measurement.status}")
        if st.button(f"View Details", key=f"view_measurement_{measurement.id}"):
            render_measurement_requests(measurement)
            
def download_measurement_results(measurement_id):
    db_controller = PromptingServiceDbController()
    requests = db_controller.get_requests_by_measurement_id(measurement_id)
    data = []

    for request in requests:
        responses = db_controller.get_full_responses_by_request_id(request.id)
        for res in responses:
            data.append({
                "prompt": res.prompt,
                "prompttype": res.prompttype,
                "response": res.response,
                "sci_score": res.sci_score,
                "answer_time_seconds": res.answer_time_seconds,
                "request_id": res.request_id,
                "llm_config": res.llm_config,
            })

    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def load_measurement_requests(measurement_id):
    db_controller = PromptingServiceDbController()
    requests = db_controller.get_requests_by_measurement_id(measurement_id)
    st.session_state.current_measurement_requests = requests
    
def load_request_chat(requestId):
    db_controller = PromptingServiceDbController()
    chat = db_controller.get_full_responses_by_request_id(requestId)
    return chat