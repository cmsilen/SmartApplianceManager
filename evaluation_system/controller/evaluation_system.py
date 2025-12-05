""" Evaluation System main class"""

import json
import jsonschema
from pathlib import Path
from threading import Thread

from evaluation_system.messaging.msg_json import MessagingJsonController
from evaluation_system.repository.database_manager import DatabaseManager
from evaluation_system.model.label import Label
from evaluation_system.model.label_source import LabelSource


class EvaluationSystem:
    """ Main system class """

    def __init__(self):
        """ Constructor """
        self.database_manager = None
        self.evaluation_system_config = None
        self.msg_controller = None

    def import_cfg(self, file_name = "system_config.json"):
        """ Import configuration file"""

        current_dir = Path(__file__).parent  # A/Y
        config_dir = current_dir.parent / "config"
        config_filepath = current_dir.parent / "config" / file_name

        try:
            with open(config_filepath, 'r', encoding='utf-8') as f:
                self.evaluation_system_config = json.load(f)
        except FileNotFoundError:
            print(f"Error: file {config_filepath} does not exist.")
        except json.JSONDecodeError:
            print(f"Error: file {config_filepath} is not in JSON format.")

    def setup_database(self):
        """ Setup database """
        self.database_manager = DatabaseManager()

        # Create the tables
        self.database_manager.create_tables()

    def setup_listener(self, ip, port):
        """ Setup listener thread """

        # Reference to msg_controller
        self.msg_controller = MessagingJsonController.get_instance()

        # Start listener on specified ip:port
        listener = Thread(target=self.msg_controller.listener, args=(ip, port))
        listener.setDaemon(True)
        listener.start()

    def setup(self):
        """ Setup system """

        # Import configuration
        self.import_cfg()

        # Setup database
        self.setup_database()

        # Setup listener
        self.setup_listener(
            ip=self.evaluation_system_config["evaluation_system"]["ip"],
            port=self.evaluation_system_config["evaluation_system"]["port"],
        )

        print("[EVALUATION SYSTEM] Setup completed")

    def run(self):
        """ Main loop """

        # Setup whole system
        self.setup()

        # Start loop
        while True:

            # Receive JSON
            received_label_json, label_source = self.msg_controller.receive()

            try:
                # Convert to Label Object
                label = Label.from_json(received_label_json)

                # Add to database
                self.database_manager.store_label(label, label_source)

                tot_rec = self.database_manager.get_total_record_count()
                tot_pairs = self.database_manager.get_complete_labels_count()
                print(f"[EVALUATION SYSTEM] Total records: {tot_rec}")
                print(f"[EVALUATION SYSTEM] Total pairs: {tot_pairs}")

                # TODO check number of completed pairs AGAINST the configuration

                # TODO generate evaluation report

                # TODO view evaluation report

                # TODO ask for ok/not ok

                # TODO module to simulate ok/not ok

            except jsonschema.exceptions.ValidationError:
                print(f"Validation error: {received_label_json}")
