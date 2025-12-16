""" Classification System main class"""

from threading import Thread
import jsonschema

from production_system.config.configuration_controller import ConfigurationController
from production_system.classifier.classifier import Classifier
from production_system.messaging.msg_json import MessagingJsonController
from production_system.model.prepared_session import PreparedSession
from production_system.errorlog.error_logger import ErrorLogger

class ClassificationSystem:
    """ Main system class """

    PHASE_PRODUCTION = "prod"
    PHASE_EVALUATION = "eval"

    def __init__(self):
        """ Constructor """
        self._conf = None
        self._msg_controller = None
        self._classifier = None
        self._session_counter = None
        self._current_session = None
        self._error_logger = None
        self._test_service_flag = True

    def setup_configuration_controller(self):
        """ Setup configuration controller """
        self._conf = ConfigurationController()
        self._conf.import_config()

    def setup_listener(self, ip_add, port):
        """ Setup listener thread """

        # Reference to msg_controller
        self._msg_controller = MessagingJsonController.get_instance()

        # Start listener on specified ip:port
        listener = Thread(target=self._msg_controller.listener, args=(ip_add, port))
        listener.daemon = True
        listener.start()

    def setup_classifier(self):
        """ Setup classifier """
        # If not in development phase, setup classifier
        if not self._conf.get_sys_params()["development_phase"]:
            self._classifier = Classifier()
            self._classifier.load_from_file()

    def setup_logger(self):
        """ Setup logger"""
        self._error_logger = ErrorLogger()
        self._error_logger.setup()

    def setup(self):
        """ Setup system """

        # Import configuration
        self.setup_configuration_controller()

        # Setup classifier
        self.setup_classifier()

        # Setup listener
        self.setup_listener(
            ip_add=self._conf.get_addresses()["classification_system"]["ip"],
            port=self._conf.get_addresses()["classification_system"]["port"],
        )

        # setup logger
        self.setup_logger()

        if not self._conf.get_sys_params()["development_phase"]:
            self._session_counter = 0
            self._current_session = self.PHASE_PRODUCTION
        else:
            self._session_counter = None

        print("[CLASSIFICATION SYSTEM] Setup completed")

    def update_phase(self):
        """ Updates the system current phase """

        # No automatic switch from dev phase
        if self._conf.get_sys_params()["development_phase"]:
            return

        if self._session_counter is None:
            return

        # Update session counter
        self._session_counter += 1

        # Switch session
        if self._current_session == self.PHASE_PRODUCTION:
            if self._session_counter >= self._conf.get_sys_params()["production_sessions"]:
                self._current_session = self.PHASE_EVALUATION
                self._session_counter = 0
                print("[CLASSIFICATION SYSTEM] Switched to evaluation phase")

        elif self._current_session == self.PHASE_EVALUATION:
            if self._session_counter >= self._conf.get_sys_params()["evaluation_sessions"]:
                self._current_session = self.PHASE_PRODUCTION
                self._session_counter = 0
                print("[CLASSIFICATION SYSTEM] Switched to production phase")

    def run(self):
        """ Main loop """

        # Setup whole system
        self.setup()

        # Start loop
        while True:

            # Depending on which phase (dev or not)
            dev_phase = self._conf.get_sys_params()["development_phase"]

            # While in development phase
            if dev_phase:

                try:
                    # Just wait for classifier
                    # in this case conversion is done by the msg module
                    classifier = self._msg_controller.receive()

                    print("[CLASSIFICATION SYSTEM] Classifier received")

                    # Save ref
                    self._classifier = classifier

                    # Save to file
                    self._classifier.store()

                    # Send message (end of development, reconfigure systems)

                    msg = {"deployment": "done"}
                    if not self._test_service_flag:
                        MessagingJsonController.send_messaging_system(msg)
                    else:
                        print("(TEST) SENDING classifier TO INGESTION")
                        ing_sys = self._conf.get_addresses()["ingestion_system"]
                        MessagingJsonController.send(
                            ing_sys["ip"],
                            ing_sys["port"],
                            "/dev_stop",
                            msg
                        )


                    print("[CLASSIFICATION SYSTEM] Deployment completed")

                except Exception as gen_exc:
                    print(f"General error: {gen_exc}")
                    self._error_logger.log(f"General error: {gen_exc}")

            # Production / Evaluation phase
            else:

                # Wait for prepared session
                prepared_session_json = self._msg_controller.receive()
                print(f"[CLASSIFICATION SYSTEM] \
                Prep. session: uuid={prepared_session_json['UUID']}")

                try:
                    # Validate schema and create object
                    prep_session = PreparedSession.from_json(prepared_session_json)

                    print("[CLASSIFICATION SYSTEM] Prepared session accepted")

                    # Infer classifier
                    label = self._classifier.infer(prep_session)
                    print(f"[CLASSIFICATION SYSTEM] \
                    Label calculated: {str(label.get_label_type())}")

                    # Differentiate between Production / Evaluation phase

                    # In evaluation phase send label to Evaluation System
                    if self._current_session == self.PHASE_EVALUATION:
                        # Send label
                        eval_sys = self._conf.get_addresses()["evaluation_system"]
                        MessagingJsonController.send(
                            eval_sys["ip"],
                            eval_sys["port"],
                            "/label/classifier",
                            label.to_dict()
                        )

                    # Always send to final client
                    if not self._test_service_flag:
                        cli_sys = self._conf.get_addresses()["client_side_system"]
                        MessagingJsonController.send(
                            cli_sys["ip"],
                            cli_sys["port"],
                            "/fault_risk",
                            label.to_dict()
                        )
                    else:
                        print(f"(TEST) SENDING TO INGESTION:\n{label.to_dict()}")
                        ing_sys = self._conf.get_addresses()["ingestion_system"]
                        msg = {'uuid': label.get_uuid()}

                        try:
                            MessagingJsonController.send(
                                ing_sys["ip"],
                                ing_sys["port"],
                                "/test_stop",
                                msg
                            )
                        except Exception as send_exc:
                            print(f"[TEST] ERROR Sending to ingestion: {send_exc}")

                    # Update session
                    self.update_phase()

                # Discard any other type of message
                except jsonschema.exceptions.ValidationError as val_exc:
                    print(f"[CLASSIFICATION SYSTEM] [PROD/EVAL] Validation error: {val_exc}")
                    self._error_logger.log(f"[PROD/EVAL] json validation error: {val_exc}")

                except Exception as gen_exc:
                    print(f"General error: {gen_exc}")
                    self._error_logger.log(f"General error: {gen_exc}")
