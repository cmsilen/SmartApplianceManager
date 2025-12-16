from development_system.model.validation_manager import ValidationManager


class ValidationController:
    def __init__(self):
        self._validation_manager = ValidationManager()

    def get_classifiers(self):
        return self._validation_manager.get_candidate_classifiers()

    def get_the_winner_classifier(self, uuid):
        self._validation_manager.winner_classifier(uuid)

    def get_validation_report(self):
        self._validation_manager.generate_validation_result()