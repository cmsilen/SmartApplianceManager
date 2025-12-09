import datetime
import queue
from threading import Thread
from flask import Flask, request
from requests import post, exceptions

from ingestion_system.src.messages import Message
from ingestion_system.src.messages.RawSessionMessage import RawSessionMessage


class MessageController:
    """
    Provides primitives for messaging between systems
    """

    _instance = None

    def __init__(self):
        # Flask instance to receive data
        self._app = Flask(__name__)
        # a thread-safe queue to buffer the received json message
        self._received_json_queue = queue.Queue()
        self.test_data = {}

    @staticmethod
    def get_instance():
        if MessageController._instance is None:
            MessageController._instance = MessageController()
        return MessageController._instance

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

    def send(self, message: Message, endpoint):
        """
        Sends a message to an endpoint using the address in the message.
        Returns if the message was successfully sent
        :param message: Message
        :param endpoint: str
        :return: boolean
        """
        url = f'http://{message.dst_address}:{message.dst_port}/' + endpoint
        response = None
        try:
            response = post(url, json=message.to_dict(), timeout=10.0)
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

        if isinstance(message, RawSessionMessage):
            self.test_data[message.raw_session.uuid] = datetime.datetime.now()
        return True


app = MessageController.get_instance().get_app()


@app.get('/start')
def start_app():
    print("[INFO] Start msg received")
    receive_thread = Thread(target=MessageController.get_instance().send_to_main)
    receive_thread.start()
    return {}, 200


@app.route("/")
def home():
    return "Ingestion System online!"

@app.post("/test_stop")
def test_stop():
    msg = request.get_json()
    test_data = MessageController.get_instance().test_data
    end = datetime.datetime.now()
    if msg["uuid"] not in test_data:
        print("[ERR] invalid uuid received")
        return {"error": "invalid uuid"}, 400

    start = test_data[msg["uuid"]]
    del test_data[msg["uuid"]]
    difference = end - start
    with open("test.csv", "a") as f:
        f.write(f"{start.isoformat()};{end.isoformat()};{difference.total_seconds()}\n")
    return {}, 200
