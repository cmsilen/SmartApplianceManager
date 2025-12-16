""" Module for message send/receive. Implemented via Singleton """
import os
import json
import queue
from datetime import datetime
from flask import Flask, request
from requests import post, exceptions

from production_system.classifier.classifier import Classifier


class MessagingJsonController:
    """ Messaging Controller class """
    _instance = None

    def __init__(self):
        """ Constructor """
        # Flask instance to receive data
        self._app = Flask(__name__)

        self._queue = queue.Queue()

    @staticmethod
    def get_instance():
        """ Returns instance of MessagingController """
        if MessagingJsonController._instance is None:
            MessagingJsonController._instance = MessagingJsonController()
        return MessagingJsonController._instance

    def listener(self, ip_add, port):
        """ Listener """
        # Disable the default logging
        # log = logging.getLogger('werkzeug')
        # log.setLevel(logging.ERROR)

        # execute the listening server, for each message received, it will be handled by a thread
        self._app.run(host=ip_add, port=port, debug=False, threaded=True)

    def get_app(self):
        """ Get app reference """
        return self._app

    def get_queue(self):
        """ Get queue """
        return self._queue

    def receive(self, block = True, timeout = None):
        """ Return message from queue """
        return self._queue.get(block=block, timeout=timeout)

    def enqueue(self, data):
        """ Put received data into queue """
        # save received message into queue
        self._queue.put(data)

    @staticmethod
    def send(ip, port, endpoint, data):
        """ Send JSON data to given endpoint """
        url = f'http://{ip}:{port}/' + endpoint
        response = None
        try:
            response = post(url, json=data, timeout=10.0)
        except exceptions.RequestException:
            print("Endpoint system unreachable")
            return False

        if response.status_code != 200:
            try:
                res = response.json()
                error_message = 'unknown'
                if 'error' in res:
                    error_message = res['error']
                print(f'Sending Error: {error_message}')
            except ValueError:
                print(f'Non-JSON response: {response.text.strip()}')

            return False
        return True

    @staticmethod
    def send_messaging_system(data):
        """ Send message to msg system (saves to file) """

        current_dir = os.path.dirname(os.path.abspath(__file__))
        messages_dir = os.path.join(current_dir, "..", "messaging", "messages")
        os.makedirs(messages_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"msg_sys_{timestamp}.json"

        filepath = os.path.join(messages_dir, filename)

        with open(filepath, "w", encoding="utf-8") as msg_sys_msg:
            json.dump(data, msg_sys_msg, indent=4)

app = MessagingJsonController.get_instance().get_app()

@app.post("/deploy")
def receive_classifier():
    """Receive developed classifier via uploaded joblib file"""

    if "file" not in request.files:
        return {"error": "No file part"}, 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return {"error": "No selected file"}, 400

    # Read bytes
    file_bytes = uploaded_file.read()

    # Create classifier, load via passed bytes
    clf = Classifier()
    clf.load_from_bytes(file_bytes)

    # Enqueue to main controller
    MessagingJsonController.get_instance().enqueue(clf)

    return {}, 200

@app.post("/prepared_session")
def receive_prepared_session():
    """ Receive prepared session """

    # Extract JSON payload
    received_prepared_session = request.json

    # Put into queue
    MessagingJsonController.get_instance().enqueue(received_prepared_session)

    # Return ok
    return {}, 200
