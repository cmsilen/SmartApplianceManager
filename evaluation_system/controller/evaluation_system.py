""" Evaluation System main class"""

import random
from threading import Thread
import jsonschema

from evaluation_system.model.label import Label
from evaluation_system.messaging.msg_json import MessagingJsonController
from evaluation_system.repository.database_manager import DatabaseManager
from evaluation_system.reporting.evaluation_report_controller import EvaluationReportController
from evaluation_system.errorlog.error_logger import ErrorLogger
from evaluation_system.config.configuration_controller import ConfigurationController


class EvaluationSystem:
    """ Main system class """

    def __init__(self):
        """ Constructor """
        self._conf = None
        self._database_manager = None
        self._msg_controller = None
        self._eval_report_controller = None
        self._error_logger = None
        self._test_service_flag = True

    def setup_configuration_controller(self):
        """ Setup configuration controller """
        self._conf = ConfigurationController()
        self._conf.import_config()

    def setup_database(self):
        """ Setup database """
        self._database_manager = DatabaseManager()

        # Create the tables (clearing previous database)
        self._database_manager.create_tables(clear_if_exists = True)
        print("Tables created")

    def setup_listener(self, ip_add, port):
        """ Setup listener thread """

        # Reference to msg_controller
        self._msg_controller = MessagingJsonController.get_instance()

        # Start listener on specified ip:port
        listener = Thread(target=self._msg_controller.listener, args=(ip_add, port))
        listener.daemon = True
        listener.start()

    def setup_evaluation_report_controller(self, file_name = "evaluation_system_config.json"):
        """ Setup evaluation report controller """

        self._eval_report_controller = EvaluationReportController()

        self._eval_report_controller.setup(file_name)

    def setup_logger(self):
        """ Setup logger"""
        self._error_logger = ErrorLogger()
        self._error_logger.setup()

    def setup(self):
        """ Setup system """

        # Import configuration
        self.setup_configuration_controller()

        # Setup database
        self.setup_database()

        # Setup evaluation report controller
        self.setup_evaluation_report_controller(self._conf.get_eval_params())

        # Setup listener
        self.setup_listener(
            ip_add=self._conf.get_addresses()["evaluation_system"]["ip"],
            port=self._conf.get_addresses()["evaluation_system"]["port"],
        )

        # Setup logger
        self.setup_logger()

        print("Setup completed")

    def run(self):
        """ Main loop """

        # Setup whole system
        self.setup()

        # Start loop
        while True:

            # Receive JSON
            received_label_json, label_source = self._msg_controller.receive()

            try:
                # Convert to Label Object
                label = Label.from_json(received_label_json)
                print("[EVALUATION SYSTEM]: " +
                      f"LABEL [{str(label.get_label_type()):<12}" +
                      f" | {str(label_source):<12} " +
                      f"| {label.get_uuid()}]")

                # Add to database
                self._database_manager.store_label(label, label_source)

                # If there are enough label pairs
                if self._eval_report_controller.is_evaluation_possible():
                    print("==========================")
                    print("Starting evaluation report")

                    # Log eventual unpaired labels
                    tot = self._database_manager.get_count_all()
                    full = self._database_manager.get_count_pairs()
                    if full < tot:
                        self._error_logger.log(f"Unpaired labels present: {tot-full}")

                    # Generate evaluation report
                    self._eval_report_controller.generate_report()
                    # this also deletes used labels

                    # Save report
                    self._eval_report_controller.save_report()

                    # View evaluation report
                    self._eval_report_controller.visualize_report()

                    # Ask for OK / NOT OK
                    evaluation_positive = False

                    if not self._test_service_flag:
                        evaluation_positive = EvaluationReportController.get_report_evaluation()
                    else:
                        # 1/0 (OK/NOT OK) percentage: 80/20
                        evaluation_positive = random.choices(
                            [True, False],
                            weights=[50, 50],
                            k=1)[0]
                        print("Simulated result:" + str(evaluation_positive))

                    if not evaluation_positive:
                        msg = {"evaluation" : "not passed"}
                        MessagingJsonController.send_messaging_system(msg)

                    self._eval_report_controller.close_report()

            except jsonschema.exceptions.ValidationError as val_exc:
                print(f"Validation error: {val_exc}")
                self._error_logger.log(f"json validation error: {val_exc}")

            except Exception as exc:
                print(f"General error: {exc}")
                self._error_logger.log(f"General error: {exc}")
