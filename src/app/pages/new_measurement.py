import streamlit as st
from typing import List, Dict, Any
from pydantic import ValidationError
import random
import json
from app.models.request import RequestPayload
from app.models.internal import Args, LLMConfig, Measurement, Request, PromptInput
from app.controllers.db_controller import PromptingServiceDbController
from app.client.llm_registry_client import request_llms
import pandas as pd


def render_new_measurement():
    st.title("New Measurement")
    
    st.session_state.file = st.file_uploader("Upload CSV File", type=["csv"])
    

    if "llm_configs" not in st.session_state:
        st.session_state.llm_configs = []

    if "prompting_args" not in st.session_state:
        st.session_state.prompting_args = {}

    if "deployment_args" not in st.session_state:
        st.session_state.deployment_args = {}

    # Navigation
    mode = st.radio("Mode", ["Field-based Input", "JSON Input"], horizontal=True)

    # Field-based Input
    if mode == "Field-based Input":
        st.subheader("Add LLM Configuration")
        modeltyp = st.text_input("Model Type")
        model = st.text_input("Model Name")
        uses_chat_template = st.checkbox("Uses Chat Template", value=False)

        # Dynamische Argumente für Prompting und Deployment hinzufügen
        st.markdown("### Add Arguments")
        arg_type = st.radio("Argument Type", ["prompting", "deployment"], horizontal=True)
        arg_name = st.text_input("Argument Name")
        arg_datatype = st.selectbox("Argument Datatype", ["string", "int", "float", "bool"])
        arg_value = st.text_input("Argument Value")

        def add_argument(arg_type: str, name: str, datatype: str, value: str):
            """Add an argument to prompting or deployment based on the type."""
            parsed_value = None
            if datatype == "int":
                parsed_value = int(value)
            elif datatype == "float":
                parsed_value = float(value)
            elif datatype == "bool":
                parsed_value = value.lower() in ["true", "1", "yes"]
            else:
                parsed_value = value  # String

            if arg_type == "prompting":
                st.session_state.prompting_args[name] = parsed_value
            elif arg_type == "deployment":
                st.session_state.deployment_args[name] = parsed_value

        if st.button("Add Argument"):
            try:
                add_argument(arg_type, arg_name, arg_datatype, arg_value)
                st.success(f"Added {arg_type} argument: {arg_name} = {arg_value} ({arg_datatype})")
            except Exception as e:
                st.error(f"Failed to add argument: {e}")

        # Aktuelle Argumente anzeigen
        st.subheader("Current Arguments")
        st.write("**Prompting Arguments**")
        st.json(st.session_state.prompting_args)
        st.write("**Deployment Arguments**")
        st.json(st.session_state.deployment_args)

        if st.button("Add Configuration"):
            try:
                config = LLMConfig(
                    modeltyp=modeltyp,
                    model=model,
                    uses_chat_template=uses_chat_template,
                    args=Args(
                        prompting=st.session_state.prompting_args,
                        deployment=st.session_state.deployment_args,
                    ),
                )
                st.session_state.llm_configs.append(config)
                st.session_state.prompting_args = {}
                st.session_state.deployment_args = {}
                st.success("Configuration added successfully!")
            except ValidationError as e:
                st.error(f"Invalid input: {e}")

    # JSON Input
    elif mode == "JSON Input":
        st.subheader("Add Configuration from JSON")
        json_input = st.text_area("Paste JSON here", height=300)

        if st.button("Add Configuration from JSON"):
            try:
                parsed_json = json.loads(json_input)
                config = LLMConfig(**parsed_json)
                st.session_state.llm_configs.append(config)
                st.success("Configuration added successfully from JSON!")
            except ValidationError as e:
                st.error(f"Invalid JSON: {e}")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {e}")

    # Submit Measurement
    st.subheader("Submit Measurement")
    if st.button("Submit Measurement"):
        if st.session_state.llm_configs and len(st.session_state.llm_configs) > 0 and st.session_state.file:
            promptingserviceDbController = PromptingServiceDbController.get_instance()
            try:
                # CSV-Datei einlesen
                df = pd.read_csv(st.session_state.file)
                #prüfe ob die csv datei die richtigen Spalten hat
                if not all(col in df.columns for col in ["prompt", "prompttype"]):
                    st.error("CSV file must have columns 'prompt' and 'prompttype'.")
                    return
                measurement = promptingserviceDbController.create_measurement()
                #für jede Zeile in der CSV-Datei
                for index, row in df.iterrows():
                    # PromptInput-Objekt erstellen
                    prompt_input = PromptInput(
                        prompt=row["prompt"],
                        prompttype=row["prompttype"],
                        measurementId=measurement.id,
                    )
                    promptingserviceDbController.insert_prompt_input(prompt_input)
                payload = RequestPayload(
                    llms=st.session_state.llm_configs,
                    measurementId=measurement.id,
                )
                registry_url = "http://localhost:8000"
                response = request_llms(registry_url, payload)
                st.success("Measurement submitted successfully!")
                st.session_state.llm_configs = []
                for request in response.requests:
                    new_request = Request(
                        id=request.requestId,
                        llm_config=request.llmconfig.model_dump(),
                        status="queued",
                        measurementId=measurement.id,
                    )
                    promptingserviceDbController.insert_llm_request(new_request)
            except Exception as e:
                st.error(f"Failed to submit measurement: {e}")
        elif not st.session_state.file:
            st.error("Please upload a CSV file before submitting.")
        else:
            st.error("Add at least one configuration before submitting.")

    # Alle gespeicherten Konfigurationen anzeigen
    st.subheader("Current Configurations")
    for i, config in enumerate(st.session_state.llm_configs):
        st.json(config.dict())
        if st.button(f"Remove Configuration {i+1}", key=f"remove_config_{i}"):
            del st.session_state.llm_configs[i]
            st.rerun()()