import math
import os

from development_system.generator.report_generator import ReportGenerator
from development_system.model.learning_set_data import LearningDataSet
from development_system.model.smart_classifier import SmartClassifier
from development_system.model.smart_classifier_config import SMARTClassifierConfig
from development_system.utility.json_read_write import JsonReadWrite
from dotenv import load_dotenv
from pathlib import Path


class TrainingManager:

    def __init__(self):
        print("INITIALIZING TRAINING MANAGER")
        self._smart_classifier = SmartClassifier()
        self._smart_classifier_config = None
        self._train_data = None
        self._num_iterations = 0
        self._hidden_layer_sizes = []

        env_path = Path(__file__).resolve().parents[2] / "dev_sys.env"
        load_dotenv(env_path)
        config_path_from_root = os.getenv("HYPER_PARAMS_FILE_PATH")
        self.config_path = Path(__file__).resolve().parents[2] / config_path_from_root

    def update_num_iterations(self, iterations):
        self._num_iterations = iterations
        new_config = SMARTClassifierConfig(
            iterations=self._num_iterations,
            hidden_layer_sizes=self._hidden_layer_sizes)
        self._smart_classifier_config = new_config
        self._smart_classifier.update_classifier_config(new_config)

    def set_avg_hyperparameters(self):
        read_result , file_content = JsonReadWrite.read_json_file(self.config_path)
        if not read_result:
            return
        hidden_layer_size_range = file_content["hidden_layer_range"]
        hidden_neuron_range = file_content["neuron_range"]

        # grab the average hyper params
        average_layers = int((hidden_layer_size_range[1] + hidden_layer_size_range[0]) / 2)
        average_neurons = int((hidden_neuron_range[1] + hidden_neuron_range[0]) / 2)
        average_neurons = int((hidden_neuron_range[1] + hidden_neuron_range[0]) / 2)

        self._hidden_layer_sizes = tuple([math.ceil(average_neurons / (2 ** i)) for i in range(average_layers)])
        print(f'Initially the Training Network has this hidden layer sizes: { self._hidden_layer_sizes }')
        #Update the Configuration
        new_config = SMARTClassifierConfig(hidden_layer_sizes=self._hidden_layer_sizes)
        self._smart_classifier.update_classifier_config(new_config)

    def train_classifier(self):
        self._train_data = LearningDataSet().get_data("training")
        self._smart_classifier.train_model(self._train_data["data"], self._train_data["labels"])
        return self._train_data

    def get_classifier_losses(self):
        return self._smart_classifier.grab_training_losses()

    def generate_learning_report(self):
        losses = self.get_classifier_losses()
        generator = ReportGenerator(report_type="training", learning_losses=losses)
        generator.generate_report()
