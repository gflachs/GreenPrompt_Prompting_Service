import streamlit as st
from app.controllers.db_controller import PromptingServiceDbController
from app.pages.dashboard import render_dashboard
from app.pages.new_measurement import render_new_measurement
from app.pages.view_measurements import render_view_measurements
from functools import partial

if "queued_measurements" not in st.session_state:
    st.session_state.queued_measurements = []
if "prompting_measurements" not in st.session_state:
    st.session_state.prompting_measurements = []
if "completed_measurements" not in st.session_state:
    st.session_state.completed_measurements = []


# Initialisiere den Zustand für die aktuelle Seite
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

def set_page(page):
    """Set the current page in the session state and rerun the app."""
    st.session_state.current_page = page

# Navigation
st.sidebar.title("Navigation")
st.sidebar.button("Dashboard", key="dashboard", on_click=partial(set_page, "Dashboard"))
st.sidebar.button("New Measurement", key="new_measurement", on_click=partial(set_page, "New Measurement"))
st.sidebar.button("View Measurements", key="view_measurements", on_click=partial(set_page, "View Measurements"))

# Render die entsprechende Seite basierend auf der aktuellen Auswah

if st.session_state.current_page == "Dashboard":
    render_dashboard()
elif st.session_state.current_page == "New Measurement":
    render_new_measurement()
elif st.session_state.current_page == "View Measurements":
    render_view_measurements()

