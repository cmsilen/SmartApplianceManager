
from development_system.model.training_manager import TrainingManager
class TrainingController:
    def __init__(self):
        print("[INFO] Set Average Hyperparameters")
        self._training_manager = TrainingManager()


    def set_avg_hyper_params(self):
        self._training_manager.set_avg_hyperparameters()

    def update_num_iterations(self,iterations):
        self._training_manager.update_num_iterations(iterations)

    def train_model(self):
        print("[INFO] Model training started.")
        print("[INFO] Model training completed.")
        return self._training_manager.train_classifier()

    def  generate_calibration_report(self):
        self._training_manager.generate_learning_report()

