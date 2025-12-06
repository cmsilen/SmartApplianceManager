""" Module for Evaluation report controller """
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List

from evaluation_system.model.label_pair import LabelPair
from evaluation_system.repository.database_manager import DatabaseManager
from evaluation_system.model.evaluation_report_data import EvaluationReportData


def calculate_errors(label_pairs: List[LabelPair]) -> int:
    """ Calculate the number of errors """
    error_count = 0

    for label_pair in label_pairs:
        if label_pair.are_label_different():
            error_count += 1

    return error_count

def calculate_consecutive_errors(label_pairs: List[LabelPair]) -> int:
    """ Calculate the number of consecutive errors """

    max_streak = 0
    current_streak = 0

    for label_pair in label_pairs:
        if label_pair.are_label_different():
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return max_streak


class EvaluationReportController:
    """ Evaluation report controller """

    def __init__(self):
        """ Initialise the controller """
        self._database_manager = None
        self._config_filepath = None
        self._reports_directory = None
        self._evaluation_config_json = None
        self._current_report = None

    def setup(self, config_filename = "system_config.json"):
        """ Set up the controller """
        self._database_manager = DatabaseManager()

        self._config_filepath = Path(__file__).parent.parent / "config" / config_filename
        self._reports_directory = Path(__file__).parent.parent / "evaluation_reports"

        self.load_config()

    def load_config(self):
        """ Load configuration file """
        try:
            with open(self._config_filepath, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
                self._evaluation_config_json = full_config["evaluation_parameters"]

        except FileNotFoundError:
            print(f"Error: file {self._config_filepath} does not exist.")
        except json.JSONDecodeError:
            print(f"Error: file {self._config_filepath} is not in JSON format.")

    def is_evaluation_possible(self):
        """
        Check if the evaluation report is possible.
        It checks if there are enough complete label pairs in the database
        """

        # In case of modified configuration file
        self.load_config()

        # Get number of complete pairs
        current_pairs = self._database_manager.get_count_pairs()

        # Possible if more than the request amount are present
        return current_pairs >= self._evaluation_config_json["label_pairs"]

    def generate_report(self):
        """
        Generate evaluation report
        1) Fetches configuration file
        2) Fetches label pairs from the database
        3) Calculates error counts (total and consecutive)
        4) Deletes used labels from database
        """

        # Load configuration
        self.load_config()

        # Number of pairs
        pairs_count = self._evaluation_config_json["label_pairs"]

        # Get number of complete pairs
        current_pairs = self._database_manager.get_label_pairs(limit=pairs_count)

        # Create data object
        evaluation_report_data = EvaluationReportData()

        ### Set fields

        # Label pairs
        evaluation_report_data.set_label_pairs(current_pairs)

        # Errors
        err_max = self._evaluation_config_json["max_errors"]
        err = calculate_errors(current_pairs)
        evaluation_report_data.set_errors_max(err_max)
        evaluation_report_data.set_errors(err)
        evaluation_report_data.set_errors_threshold_satisfied(err <= err_max)

        # Consecutive errors
        ce_max = self._evaluation_config_json["max_consecutive_errors"]
        ce = calculate_consecutive_errors(current_pairs)
        evaluation_report_data.set_consecutive_errors_max(ce_max)
        evaluation_report_data.set_consecutive_errors(ce)
        evaluation_report_data.set_consecutive_errors_threshold_satisfied(err <= ce_max)

        self._current_report = evaluation_report_data

        # Delete used labels
        self._database_manager.delete_label_pairs(current_pairs)

    def save_report(self):
        """Save the evaluation report"""
        if self._current_report is None:
            return

        os.makedirs(self._reports_directory, exist_ok=True)

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"report_{timestamp}.json"
        path = os.path.join(self._reports_directory, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._current_report.to_dict(), f, indent=4)

    def visualize_report(self):
        """ Visualize the evaluation report """
        if self._current_report is None:
            return

        data = self._current_report.to_dict()

        print("\n ====== Evaluation Report ======")

        print(" === Label Pairs: (expert / classifier )")
        for p in data['label_pairs']:
            print(f" - {p['label_expert']} / {p['label_classifier']}")

        print(" === Total errors:")
        print(f" Actual:  {data['errors']}")
        print(f" Maximum: {data['errors_max']}")
        print(f" Threshold satisfied: {data['errors_threshold_satisfied']}")

        print(" === Consecutive errors:")
        print(f" Actual:  {data['consecutive_errors']}")
        print(f" Maximum: {data['consecutive_errors_max']}")
        print(f" Threshold satisfied: {data['consecutive_errors_threshold_satisfied']}")

        print(" ====== Evaluation Report end ======")

    @staticmethod
    def get_report_evaluation() -> bool:
        """ Asks human the final evaluation """

        while True:
            user_input = input("Final evaluation (type OK or NOTOK): ").strip().upper()
            if user_input == "OK":
                print("Input received correctly.\n")
                return True
            if user_input == "NOTOK":
                print("Input received correctly.\n")
                return False

            print("Input not recognized. Please type 'OK' or 'NOTOK'.")

    def close_report(self):
        """Close the evaluation report"""
        self._current_report = None
