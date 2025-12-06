""" Module for message send/receive. Implemented via Singleton """

import queue
import logging
from flask import Flask, request
from requests import post, exceptions
from evaluation_system.model.label_source import LabelSource


class MessagingJsonController:
    """ Messaging Controller class """
    _instance = None

    def __init__(self):
        """ Constructor """
        # Flask instance to receive data
        self._app = Flask(__name__)
        # a thread-safe queue to buffer the received json message
        self._msg_to_controller_queue = queue.Queue()

    @staticmethod
    def get_instance():
        """ Returns instance of MessagingController """
        if MessagingJsonController._instance is None:
            MessagingJsonController._instance = MessagingJsonController()
        return MessagingJsonController._instance

    def listener(self, ip, port):
        """ Listener """
        # Disable the default logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # execute the listening server, for each message received, it will be handled by a thread
        self._app.run(host=ip, port=port, debug=False, threaded=True)

    def get_app(self):
        return self._app

    def send_to_main(self):
        self._msg_to_controller_queue.put(True, block=True)

    def get_queue(self):
        """ Get queue """
        return self._msg_to_controller_queue

    def receive(self, block = True, timeout = None):
        """ Return message from queue """
        return self._msg_to_controller_queue.get(block=block, timeout=timeout)

    def put_object_into_queue(self, data):
        """ Put received json into queue """
        # save received message into queue
        self._msg_to_controller_queue.put(data)

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

app = MessagingJsonController.get_instance().get_app()

# TODO Delete this (or maybe not)
@app.route("/")
def home():
    """ home endpoint"""
    html = """
    <div>
      <h3>Endpoints</h3>
      <ul>
        <li>
          <strong>Classifier label structure:</strong>
          <pre><code>{
                uuid = &lt;UUID&gt;,
                type = [ none | overheating | electrical ],
            }</code></pre>
        </li>
        <li>
          <strong>Expert label structure:</strong>
          <pre><code>{
                uuid = &lt;UUID&gt;,
                type = [ none | overheating | electrical ],
            }</code></pre>
        </li>
      </ul>
    </div>
    """
    return html


@app.post("/label/classifier")
def receive_classifier_label():
    """ Receive label from classifier """

    # Extract JSON payload
    received_label = request.json

    # Add source info
    label_data = (received_label, LabelSource.CLASSIFIER)

    # Put into queue
    MessagingJsonController.get_instance().put_object_into_queue(label_data)

    # Return ok
    return {}, 200


@app.post("/label/expert")
def receive_expert_label():
    """ Receive label from expert """

    # Extract JSON payload
    received_label = request.json

    # Add source info
    label_data = (received_label, LabelSource.EXPERT)

    # Put into queue
    MessagingJsonController.get_instance().put_object_into_queue(label_data)

    # Return ok
    return {}, 200
