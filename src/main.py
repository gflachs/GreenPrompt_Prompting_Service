import os
import threading
from streamlit.web.bootstrap import run
import threading
import time

from app.controllers.db_controller import PromptingServiceDbController
from app.client.llm_registry_client import get_llm_request_status, release_llms
from app.client.wrapper_client import send_prompt
from app.utils.logger import console_logger
from apscheduler.schedulers.background import BackgroundScheduler
from app.models.internal import Request, LLM_Response

def background_status_checker():
    """Background thread to periodically check the status of queued measurements."""

    #load all measurements
    dbController = PromptingServiceDbController.get_instance()
    all_measurements = dbController.get_measurements_by_status("deployments_pending")
    for measurement in all_measurements:
        requests = load_measurement_requests(measurement.id)
        requests_finished = 0
        for request in requests:
            if request.status == "prompting" or request.status == "deployed" and request.address != "" and request.address is not None:
               continue
            if request.status == "finished":
                requests_finished += 1
                continue
            status = get_llm_request_status("http://localhost:8000", request.id)
            if request.status != status.status:
                request.status = status.status
                request.address = status.address
                dbController.update_llm_request(request)
            if request.status == "deployed" and request.address != "" and request.address is not None:
                request.status = "prompting"
                dbController.update_llm_request(request)
                measurement.status = "prompting"
                dbController.update_measurement(measurement)
                threading.Thread(target=start_prompting, args=(request,), daemon=True).start()
        if requests_finished == len(requests):
            measurement.status = "finished"
            dbController.update_measurement(measurement)
    console_logger.info("Checked status of all requests")
    
def start_prompting(request: Request):
    """Startet den Prompting-Prozess für eine Messung."""
    console_logger.info(f"Starting prompting for request {request.id}")
    db_controller = PromptingServiceDbController.get_instance()
    promptInputs = db_controller.get_prompt_inputs_by_measurement_id(request.measurementId)
    for promptInput in promptInputs:
        time_start = time.time()
        prompt = promptInput.prompt
        response = send_prompt(request.address, prompt)
        time_end = time.time()
        llmResponse = LLM_Response(llm_config=request.llm_config, idPromptInput=promptInput.id, response=response.answer, sci_score=response.sci_score, answer_time_seconds=time_end-time_start, request_id=request.id)
        db_controller.insert_llm_response(llmResponse)
    request.status = "finished"
    db_controller.update_llm_request(request)
    release_llms("http://localhost:8000", request.id)
    
    

def load_measurement_requests(measurement_id):
    db_controller = PromptingServiceDbController.get_instance()
    requests = db_controller.get_requests_by_measurement_id(measurement_id)
    return requests


def start_streamlit():
    """Startet die Streamlit-App."""
    script_path = os.path.join(os.getcwd(), "streamlit_app.py")
    flag_options = {}
    run(script_path, False, "", flag_options)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(background_status_checker, 'interval', seconds=20)
    scheduler.start()
    # Streamlit im Hauptprozess starten
    start_streamlit()
