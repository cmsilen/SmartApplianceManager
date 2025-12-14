import warnings
import os
import pandas as pd
import joblib

from dotenv import load_dotenv
from pathlib import Path

from development_system.utility.json_read_write import JsonReadWrite
from development_system.model.smart_classifier_config import SMARTClassifierConfig

from sklearn.exceptions import ConvergenceWarning, DataConversionWarning
from sklearn.neural_network import MLPClassifier

# Ignore the Warnings
warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=DataConversionWarning)


class SmartClassifier:
    def __init__(self):
        self._classifier = MLPClassifier()
        self._classifier_config = SMARTClassifierConfig()

        env_path = Path(__file__).resolve().parents[2] / "dev_sys.env"
        load_dotenv(env_path)
        config_path_from_root = os.getenv("HYPER_PARAMS_FILE_PATH")
        self.config_path = Path(__file__).resolve().parents[2] / config_path_from_root

        classifiers_path_from_root = os.getenv("CANDIDATE_CLASSIFIERS_DIRECTORY_PATH")
        self.classifiers_path = Path(__file__).resolve().parents[2] / classifiers_path_from_root

        winner_joblib_path_from_root = os.getenv("WINNER_CLASSIFIER_DIRECTORY_PATH")
        self.winner_joblib_path = Path(__file__).resolve().parents[2] / winner_joblib_path_from_root

    def train_model(self, training_data, training_labels):
        training_data = pd.DataFrame(training_data)
        self._classifier.fit(training_data, training_labels)

    def update_classifier_config(self, new_config: SMARTClassifierConfig):
        """
        Update internal config and, if needed, update the JSON config file and
        reconfigure the underlying classifier.
        """
        iteration_changed = self._classifier_config.num_iterations != new_config.num_iterations
        if (( self._classifier_config is not  None
                    and iteration_changed )
                or self._classifier_config is None ):
            print("[DEBUG] Update SMART classifier config file")
            JsonReadWrite.update_json_file(
                self.config_path,
                "num_iterations",
                new_config.num_iterations
            )
        self._classifier_config = new_config
        self._classifier.set_params(**new_config.to_dict())

    def get_error(self, data, labels):
        data = pd.DataFrame(data)
        return self._classifier.score(data, labels)

    def grab_training_losses(self):
        return self._classifier.loss_curve_

    def save_classifier(self, uuid):
        if uuid is None:
            raise ValueError("uuid cannot be None")

        file_path = Path(self.classifiers_path) / f"{str(uuid).upper()}.joblib"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._classifier, file_path)

    def load_classifier(self, uuid):
        if uuid is None:
            raise ValueError("uuid cannot be None")

        file_path = Path(self.classifiers_path) / f"{str(uuid).upper()}.joblib"
        if not file_path.is_file():
            raise FileNotFoundError(f"Classifier file not found: {file_path}")
        self._classifier = joblib.load(file_path)