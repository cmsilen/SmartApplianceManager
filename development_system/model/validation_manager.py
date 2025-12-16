import math
import os
from itertools import product
from operator import itemgetter

from dotenv import load_dotenv
from pathlib import Path

from development_system.generator.report_generator import ReportGenerator
from development_system.model.learning_set_data import LearningDataSet
from development_system.model.smart_classifier import SmartClassifier
from development_system.model.smart_classifier_config import SMARTClassifierConfig
from development_system.utility.json_read_write import JsonReadWrite


class ValidationManager:
    def __init__(self):
        self._smart_classifier = SmartClassifier()
        self._train_data = LearningDataSet.get_data("training")
        self._validation_data = LearningDataSet.get_data("validation")
        self._candidate_classifiers = []

        env_path = Path(__file__).resolve().parents[2] / "dev_sys.env"
        load_dotenv(env_path)
        config_path_from_root = os.getenv("HYPER_PARAMS_FILE_PATH")
        self.config_path = Path(__file__).resolve().parents[2] / config_path_from_root

        top5_classifiers_from_root = os.getenv("TOP5_CLASSIFIER_PATH")
        self.top5_classifiers_path = Path(__file__).resolve().parents[2] / top5_classifiers_from_root

        winner_from_root = os.getenv("WINNER_PATH")
        self.winner_path = Path(__file__).resolve().parents[2] / winner_from_root

        winner_joblib_from_root = os.getenv("WINNER_CLASSIFIER_DIRECTORY_PATH")
        self.winner_joblib_path = Path(__file__).resolve().parents[2] / winner_joblib_from_root

        candidates_path_from_root = os.getenv("CANDIDATE_CLASSIFIERS_DIRECTORY_PATH")
        self.candidate_paths = Path(__file__).resolve().parents[2] / candidates_path_from_root

    def generate_hyperparameter_options(self):
        read_result, file_content = JsonReadWrite.read_json_file(self.config_path)
        if not read_result:
            print("No HYPER_PARAMS_FILE_PATH file found")
            return [], None, None

        num_iterations = file_content["num_iterations"]
        overfitting_threshold = file_content["overfitting_tolerance"]
        hidden_layer_size_range = file_content["hidden_layer_range"]
        hidden_neuron_range = file_content["neuron_range"]

        max_exp = int(math.log2(hidden_neuron_range[1]))  # 128 -> 7
        min_exp = int(math.log2(hidden_neuron_range[0]))  # 4   -> 2
        neuron_options = [2 ** i for i in range(max_exp, min_exp - 1, -1)] # range(start, stop, step)

        hidden_layer_sizes_options = []

        for n_layers in range(hidden_layer_size_range[0], hidden_layer_size_range[1] + 1):
            hidden_layer_sizes_options.extend(
                self.generate_decreasing_layers(neuron_options, n_layers)
            )
        return hidden_layer_sizes_options, num_iterations, overfitting_threshold


    def get_candidate_classifiers(self):
        print("inside the get_candidate_classifiers ")
        grid_search_result, iterations_number, overfitting_threshold = self.generate_hyperparameter_options()
        if not grid_search_result:
            print("[WARN] No hyperparameter settings generated, skipping validation.")
            return
        # setting == architecture of the model
        for index, setting in enumerate(grid_search_result):
            new_config = SMARTClassifierConfig(iterations_number, setting)

            self._smart_classifier.update_classifier_config(new_config)

            self._smart_classifier.train_model(self._train_data["data"], self._train_data["labels"]) # train every architecture model

            train_error = self._smart_classifier.get_error(
                self._train_data["data"],
                self._train_data["labels"]
            )

            validation_error = self._smart_classifier.get_error(
                self._validation_data["data"],
                self._validation_data["labels"]
            )


            if (validation_error - train_error) > overfitting_threshold:
                print("The architecture with ",(index,setting), " is discarded.")
                continue
            print("The architecture with ", (index, setting), " is accepted.")

            self._smart_classifier.save_classifier("NN" + str(index))

            neurons = sum(setting)
            # model summary
            model = {
                "uuid": "NN" + str(index),
                "train_error": train_error,
                "validation_error": validation_error,
                "layers": len(setting),
                "neurons": neurons,
                "hidden_layers_structure": setting,
                "error_difference": abs(validation_error - train_error),
                "overfitting_threshold": overfitting_threshold
            }

            self._candidate_classifiers.append(model)
            self._candidate_classifiers = sorted(
                self._candidate_classifiers,
                key=itemgetter('validation_error')
            )

            # A check that the top classifiers selected are not more than FIVE
            if len(self._candidate_classifiers) > 5:
                self._candidate_classifiers.pop(5)

        # The top-5  candidate classifiers are saved into JSON here
        self.save_top5_classifiers_json()
        print("[DEBUG] THE BEST 5 CLASSIFIERS  : ", self._candidate_classifiers)

    def save_top5_classifiers_json(self):
        JsonReadWrite.write_json_file(self.top5_classifiers_path, self._candidate_classifiers)
        print(f"[INFO] Saved top 5 classifier metadata at {self.top5_classifiers_path}")

    def winner_classifier(self, uuid):
        # Read the top5 classifiers JSON
        read_result, file_content = JsonReadWrite.read_json_file(self.top5_classifiers_path)
        if not read_result:
            print("[ERROR] winner_classifier not found")
            return

        # Locate the selected winner
        winner = next((clf for clf in file_content if clf["uuid"] == uuid), None)
        if not winner:
            print(f"[WARN] No classifier with UUID {uuid} found in top5_classifiers.json")
            return

        JsonReadWrite.write_json_file(self.winner_path, winner)
        print(f"[INFO] Winner classifier metadata saved at {self.winner_path}")

        # Clean up the candidate directory (keep only the winner joblib)
        self.classifier_dir_archiver(uuid)

    def classifier_dir_archiver(self, uuid):
        winner_file = uuid + ".joblib"
        for filename in os.listdir(self.candidate_paths):
            if not filename.endswith(".joblib"):
                continue
            if filename == winner_file:
                continue
            file_path = os.path.join(self.candidate_paths, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def generate_validation_result(self):
        self.save_top5_classifiers_json()
        report_generator = ReportGenerator(report_type="validation",
                                           best_classifiers=self._candidate_classifiers)
        report_generator.generate_report()


    @staticmethod
    def generate_decreasing_layers(neuron_options, n_layers):
        results = []
        ValidationManager._backtrack_layers(
            neuron_options=neuron_options,
            n_layers=n_layers,
            current_layers=[],
            results=results
        )
        return results

    @staticmethod
    def _backtrack_layers(neuron_options, n_layers, current_layers, results):
        # Base case: full architecture built
        if len(current_layers) == n_layers:
            results.append(tuple(current_layers))
            return
        # Enforce non-increasing constraint
        max_allowed = current_layers[-1] if current_layers else float("inf")
        for neurons in neuron_options:
            if neurons <= max_allowed: # important!, the next layer can't have more neurons than the previous one.
                current_layers.append(neurons)
                #recursive call!
                ValidationManager._backtrack_layers(
                    neuron_options,
                    n_layers,
                    current_layers,
                    results
                )
                current_layers.pop()
