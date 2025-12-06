""" Evaluation System main class"""

import json
from pathlib import Path
from threading import Thread
import jsonschema

from evaluation_system.model.label import Label
from evaluation_system.messaging.msg_json import MessagingJsonController
from evaluation_system.repository.database_manager import DatabaseManager
from evaluation_system.reporting.evaluation_report_controller import EvaluationReportController
from test_system.deployment import GET_IP


PRINT_ENABLED = True

_builtin_print = print
def print(s):
    """ Redefinition of print """
    if PRINT_ENABLED:
        _builtin_print(f"[EVALUATION SYSTEM] {s}")


class EvaluationSystem:
    """ Main system class """

    def __init__(self):
        """ Constructor """
        self.database_manager = None
        self.evaluation_system_config = None
        self.msg_controller = None
        self.eval_report_controller = None

    def import_cfg(self, file_name = "system_config.json"):
        """ Import configuration file"""

        config_filepath = Path(__file__).parent.parent / "config" / file_name

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

        # Create the tables (clearing previous database)
        self.database_manager.create_tables(clear_if_exists = True)
        print("Tables created")

    def setup_listener(self, ip, port):
        """ Setup listener thread """

        # Reference to msg_controller
        self.msg_controller = MessagingJsonController.get_instance()

        # Start listener on specified ip:port
        listener = Thread(target=self.msg_controller.listener, args=(ip, port))
        listener.setDaemon(True)
        listener.start()

    def setup_evaluation_report_controller(self, file_name = "system_config.json"):
        """ Setup evaluation report controller """

        self.eval_report_controller = EvaluationReportController()

        self.eval_report_controller.setup(file_name)

    def setup(self):
        """ Setup system """

        # Import configuration
        self.import_cfg()

        # Setup database
        self.setup_database()

        # Setup evaluation report controller
        self.setup_evaluation_report_controller()

        # TODO togli, metti solo prendere da file (quello tra "")
        self.setup_listener(
            ip=GET_IP(),
            port=self.evaluation_system_config["addresses"]["evaluation_system"]["port"],
        )

        # Setup listener
        """
        self.setup_listener(
            ip=self.evaluation_system_config["addresses"]["evaluation_system"]["ip"],
            port=self.evaluation_system_config["addresses"]["evaluation_system"]["port"],
        )
        """


        print("Setup completed")

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
                print("[EVALUATION SYSTEM]: " +
                      "LABEL [{str(label.get_label_type()):<12}" +
                      " | {str(label_source):<12} " +
                      "| {label.get_uuid()}]")

                # Add to database
                self.database_manager.store_label(label, label_source)

                print(f" Current labels: {self.database_manager.get_count_pairs()} \
                (complete pairs) / {self.database_manager.get_count_all()} (total)")

                # TODO decide what to do with not complete labels

                # TODO include timestamp, order label pairs by timestamp
                #  (NEEDED FOR CONSECUTIVE ERRORS)
                #  Decide how to handle different timestamps (Expert/Classifier)

                # If there are enough label pairs
                if self.eval_report_controller.is_evaluation_possible():
                    print("==========================")
                    print("Starting evaluation report")

                    # Generate evaluation report
                    self.eval_report_controller.generate_report()
                    # this also deletes used labels

                    # Save report
                    self.eval_report_controller.save_report()

                    # View evaluation report
                    self.eval_report_controller.visualize_report()

                    # Ask for OK / NOT OK
                    evaluation_result = EvaluationReportController.get_report_evaluation()

                    # TODO fai qualcosa con il risultato

                    self.eval_report_controller.close_report()



            except jsonschema.exceptions.ValidationError:
                print(f"Validation error: {received_label_json}")
