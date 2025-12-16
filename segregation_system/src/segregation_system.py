import json
import os
import sys
import logging
from pathlib import Path
import random
from threading import Thread
from datetime import datetime
from segregation_system.src.json_io import JsonIO
from segregation_system.src.prepared_session_db_manager import PreparedSessionStorage
from segregation_system.src.balancing_report import BalancingReport
from segregation_system.src.coverage_report import CoverageReport
from segregation_system.src.learning_sets import LearningSetsGenerator
from segregation_system.src.prepared_session_schema_verifier import PreparedSessionSchemaVerifier
from segregation_system.src.segregation_system_configurator import SegregationSystemConfigurator

LOG_FILE = "segregation_system.log"
REQ_FILE = "user_requirements.log"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_user_requirement(text: str):
    with open(REQ_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {text}\n")


class SegregationSystem:

    def __init__(self):
        self.state = None
        self.segregation_system_config = None
        self.prepared_session_storage = PreparedSessionStorage()
        self.balancing_report = BalancingReport()
        self.coverage_report = CoverageReport()
        self.learning_sets = LearningSetsGenerator()
        self.prepared_session_schema_verifier = PreparedSessionSchemaVerifier()
        self.segregation_system_configurator = SegregationSystemConfigurator()

    def read_state(self):
        state_path = os.path.join(os.getcwd(), "state.txt")
        with open(state_path, "r", encoding="utf-8") as f:
            state = f.read().strip()
            return state

    def write_state(self, state):
        state_path = os.path.join(os.getcwd(), "state.txt")
        with open(state_path, "w", encoding="utf-8") as f:
            f.write(state)

    def run(self):
        self.segregation_system_config = self.segregation_system_configurator.import_cfg()

        logging.info("Configuration loaded")

        jsonIO = JsonIO.get_instance()
        listener = Thread(
            target=jsonIO.listener,
            args=(self.segregation_system_config["segregation_system"]["ip"],
                  self.segregation_system_config["segregation_system"]["port"])
        )
        listener.setDaemon(True)
        listener.start()

        self.write_state("STORE")
        current_state = self.read_state()

        self.prepared_session_storage.clear_dataset()

        while True:

            if current_state == "STORE":

                received_prepared_session = JsonIO.get_instance().receive()

                if not self.prepared_session_schema_verifier.verify(received_prepared_session):
                    logging.error("JSON session received NOT in correct format")
                    continue

                logging.info(f"JSON session received: {received_prepared_session}")

                self.prepared_session_storage.store_prepared_session(received_prepared_session)
                self.prepared_session_storage.increment_session_counter()

                if not self.prepared_session_storage.get_session_number() >= \
                       self.segregation_system_config['sessionNumber']:
                    continue

                self.prepared_session_storage.reset_counter()

                logging.info("Store state finished → Balancing state starting")
                self.write_state("BALANCING")
                current_state = "BALANCING"
                continue

            elif current_state == "BALANCING":

                logging.info("Balancing state entered")
                dataset = self.prepared_session_storage.get_all_sessions()

                self.balancing_report.generate_balancing_report(
                    dataset,
                    self.segregation_system_config['toleranceInterval']
                )
                logging.info("Balancing report generated")

                self.balancing_report.show_balancing_report()
                logging.info("Balancing report displayed to user")

                # print("[SEGREGATION SYSTEM] Does the balancing report meet your needs? (y/n): ", end="")
                # answer = sys.stdin.readline().strip().lower()
                # is_satisfactory = (answer == "y")
                # logging.info(f"Balancing report satisfactory: {is_satisfactory}")
                is_satisfactory = random.random() < 0.7

                if not is_satisfactory:
                    print("[SEGREGATION SYSTEM] Please describe what you need in order to balance:")
                    user_requirements = sys.stdin.readline().strip()
                    logging.info(f"User requirements for balancing: {user_requirements}")
                    current_state = "STORE"
                    self.write_state("STORE")
                    self.prepared_session_storage.clear_dataset()
                    logging.info("Balancing finished → Store state starting")
                    continue

                logging.info("Balancing finished → Coverage state starting")
                self.write_state("COVERAGE")
                current_state = "COVERAGE"
                continue

            elif current_state == "COVERAGE":

                logging.info("Coverage state entered")
                dataset = self.prepared_session_storage.get_all_sessions()

                self.coverage_report.generate_coverage_report(dataset)
                logging.info("Coverage report generated")

                self.coverage_report.show_coverage_report()
                logging.info("Coverage report displayed to user")

                # print("[SEGREGATION SYSTEM] Does the coverage report meet your needs? (y/n): ", end="")
                # answer = sys.stdin.readline().strip().lower()
                # is_satisfactory = (answer == "y")
                # logging.info(f"Coverage report satisfactory: {is_satisfactory}")
                is_satisfactory = random.random() < 0.7

                if not is_satisfactory:
                    print("[SEGREGATION SYSTEM] Please describe what you need in order to cover all data:")
                    user_requirements = sys.stdin.readline().strip()
                    logging.info(f"User requirements for balancing: {user_requirements}")
                    current_state = "STORE"
                    self.write_state("STORE")
                    self.prepared_session_storage.clear_dataset()
                    logging.info("Coverage finished → Store state starting")
                    continue

                logging.info("Coverage finished → Learning state starting")
                self.write_state("LEARNING")
                current_state = "LEARNING"
                continue

            elif current_state == "LEARNING":

                logging.info("Learning state entered")
                dataset = self.prepared_session_storage.get_all_sessions()

                learning_sets = self.learning_sets.generate_learning_sets(dataset)
                logging.info(f"Learning sets generated: {learning_sets}")

                JsonIO.get_instance().send(self.segregation_system_config['development_system']['ip'],
                                           self.segregation_system_config['development_system']['port'],
                                           "/learning_sets",
                                           learning_sets)

                print(
                    f"{self.segregation_system_config['development_system']['ip']}:{self.segregation_system_config['development_system']['port']}")

                logging.info(f"Learning sent to Development System")

                self.prepared_session_storage.clear_dataset()
                self.prepared_session_storage.reset_counter()
                self.write_state("STORE")
                current_state = "STORE"

                logging.info("Learning finished → Store state starting")

                continue
