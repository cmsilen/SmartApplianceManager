import queue
import os
from fileinput import filename
from threading import Thread

import requests
from flask import Flask, request
from requests import post, exceptions

from dotenv import load_dotenv
from pathlib import Path

from development_system.model.communication_config import CommunicationConfig
from development_system.utility.json_read_write import JsonReadWrite

class CommunicationManager:
    _instance = None

    def __init__(self):
        # Flask instance to receive data

        self._app = Flask(__name__)
        # a thread-safe queue to buffer the received json message
        self._received_json_queue = queue.Queue()
        """"
        # ******** Needed by the Development System *******
        """
        self.communication_config = CommunicationConfig()
        self._winner_uuid = None
        """"
        # ******** Needed by the Development System *******
        """

        env_path = Path(__file__).resolve().parents[2] / "dev_sys.env"
        load_dotenv(env_path)

        # for automated
        winner_job_path_from_root = os.getenv("TEST_WINNER_AUTOMATED")
        self.winner_job_path = Path(__file__).resolve().parents[2] / winner_job_path_from_root

        # for non automated
        winner_non_automated_path_root = os.getenv("WINNER_CLASSIFIER_DIRECTORY_PATH")
        self.winner_non_automated_job_path = Path(__file__).resolve().parents[2] / winner_non_automated_path_root


    @staticmethod
    def get_instance():
        if CommunicationManager._instance is None:
            CommunicationManager._instance = CommunicationManager()
        return CommunicationManager._instance

    def listener(self, ip, port):
        # execute the listening server, for each message received, it will be handled by a thread
        self._app.run(host=ip, port=port, debug=False, threaded=True)

    def get_app(self):
        return self._app

    def send_to_main(self):
        self._received_json_queue.put(True, block=True)

    def get_queue(self):
        return self._received_json_queue

    def receive(self):
        # get json message from the queue
        # if the queue is empty the thread is blocked
        return self._received_json_queue.get(block=True)

    def put_json_into_queue(self, received_json):
        # save received message into queue
        self._received_json_queue.put(received_json)

    def send(self, ip, port, endpoint, data):
        url = f'http://{ip}:{port}/' + endpoint
        response = None
        try:
            response = post(url, json=data, timeout=10.0)
        except exceptions.RequestException:
            print("Endpoint system unreachable")
            return False
        if response.status_code != 200:
            res = response.json()
            error_message = 'unknown'
            if 'error' in res:
                error_message = res['error']
            print(f'Sending Error: {error_message}')
            return False
        return True

     # This method is to do a python test on the orchestrator in an automated mode.
    def send_classifier_joblib_automated(self, uuid):
        print("[INFO] send classifier joblib")
        ip_classification_system, port_classification_system = self.communication_config.get_ip_port("production_system")
        url = f"http://{ip_classification_system}:{port_classification_system}/deploy"

        file_path = self.winner_job_path / f"{str(uuid).upper()}.joblib"
        print("[DEBUG] Uploading:", file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"[ERROR] File not found: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                response = requests.post(url, files={'file': f}, timeout=3)

            if response.status_code == 200:
                print("[INFO] WinnerClassifier deployed successfully.")
                return True
            else:
                print(f"[ERROR] Deployment failed — status {response.status_code}: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return False


     # This method is to do a python test on the orchestrator in non-automated mode.
    def send_classifier_joblib_non_automated(self, uuid):
        print("[INFO] send classifier automated_joblib")
        ip_classification_sys, port_classification_sys = self.communication_config.get_ip_port("production_system")
        url = f"http://{ip_classification_sys}:{port_classification_sys}/deploy"

        file_path = self.winner_non_automated_job_path / f"{str(uuid).upper()}.joblib"
        print("[DEBUG] Uploading:", file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"[ERROR] File not found: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                response = requests.post(url, files={'file': f}, timeout=3)

            if response.status_code == 200:
                print("[INFO] WinnerClassifier deployed successfully.")
                return True
            else:
                print(f"[ERROR] Deployment failed — status {response.status_code}: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return False

app = CommunicationManager.get_instance().get_app()


@app.get('/start')
def start_app():
    print("[INFO] Start msg received")
    receive_thread = Thread(target=CommunicationManager.get_instance().send_to_main)
    receive_thread.start()
    return {}, 200


# The endpoint where the Calibration set arrives.
@app.post('/learning_sets')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json
    CommunicationManager.get_instance().put_json_into_queue(received_json)
    return {}, 200


@app.route("/")
def home():
    return "Development System online!"
