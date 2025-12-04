import json
import os
from pathlib import Path
from threading import Thread
from segregation_system.src.json_io import JsonIO
from segregation_system.src.prepared_session_db_manager import PreparedSessionStorage
from segregation_system.src.balancing_report import BalancingReport
from segregation_system.src.coverage_report import CoverageReport
from segregation_system.src.learning_sets import LearningSetsGenerator


class SegregationSystem:

    def __init__(self):
        self.state = None
        self.segregation_system_config = None
        self.prepared_session_storage = PreparedSessionStorage()
        self.balancing_report = BalancingReport()
        self.coverage_report = CoverageReport()
        self.learning_sets = LearningSetsGenerator()

    def import_cfg(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.segregation_system_config = json.load(f)
        except FileNotFoundError:
            print(f"Error: file {file_path} does not exist.")
        except json.JSONDecodeError:
            print(f"Error: file {file_path} is not in JSON format.")

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
        file_path = Path(__file__).parent.parent / "segregation_system_config.json"
        self.import_cfg(file_path)

        if self.segregation_system_config is None:
            raise ValueError("Configuration not imported. Call import_cfg(file_path) first.")

        print(f"[SEGREGATION SYSTEM] Configuration loaded")

        current_state = self.read_state()

        jsonIO = JsonIO.get_instance()
        listener = Thread(target=jsonIO.listener,
                          args=(self.segregation_system_config["segregation_system"]["ip"],
                                self.segregation_system_config["segregation_system"]["port"]))
        listener.setDaemon(True)
        listener.start()

        while True:

            if current_state == "STORE":

                received_prepared_session = JsonIO.get_instance().receive()

                print(f"[SEGREGATION SYSTEM] JSON session received: {received_prepared_session}")

                self.prepared_session_storage.store_prepared_session(received_prepared_session)
                self.prepared_session_storage.increment_session_counter()

                if (not self.prepared_session_storage.get_session_number()
                        >= self.segregation_system_config['sessionNumber']):
                    continue

                self.prepared_session_storage.reset_counter()

                print(f"[SEGREGATION SYSTEM] Store state terminated. Balancing state starting")
                self.write_state("BALANCING")
                current_state = "BALANCING"

                continue

            elif current_state == "BALANCING":

                print(f"[SEGREGATION SYSTEM] dbg")
                dataset = self.prepared_session_storage.get_all_sessions()

                print(f"[SEGREGATION SYSTEM] Balancing report generated.")
                self.balancing_report.generate_balancing_report(dataset,
                                                                self.segregation_system_config['toleranceInterval'])

                print(f"[SEGREGATION SYSTEM] Balancing report exported in balancing_report.png.")
                self.balancing_report.show_balancing_report()

                print(f"[SEGREGATION SYSTEM] Balancing state terminated. Coverage state starting")
                self.write_state("COVERAGE")
                current_state = "COVERAGE"

                continue

            elif current_state == "COVERAGE":

                dataset = self.prepared_session_storage.get_all_sessions()

                print(f"[SEGREGATION SYSTEM] Coverage report generated.")
                self.coverage_report.generate_coverage_report(dataset)

                print(f"[SEGREGATION SYSTEM] Coverage report exported in coverage_report.png.")
                self.coverage_report.show_coverage_report()

                print(f"[SEGREGATION SYSTEM] Coverage state terminated. Learning state starting")
                self.write_state("LEARNING")
                current_state = "LEARNING"

                continue

            elif current_state == "LEARNING":
                dataset = self.prepared_session_storage.get_all_sessions()

                print(f"[SEGREGATION SYSTEM] Learning sets generated.")
                learning_sets = self.learning_sets.generate_learning_sets(dataset)

                print(learning_sets)

                print(f"[SEGREGATION SYSTEM] Learning state terminated. Store state is starting")

                exit(0)
