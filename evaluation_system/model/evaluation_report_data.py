""" Module for defining the evaluation report data """
from typing import List
from evaluation_system.model.label_pair import LabelPair

class EvaluationReportData:
    """Class for handling the evaluation report data"""

    def __init__(self):
        self._label_pairs = None
        self._errors = None
        self._errors_max = None
        self._consecutive_errors = None
        self._consecutive_errors_max = None
        self._errors_threshold_satisfied = None
        self._consecutive_errors_threshold_satisfied = None

    def to_dict(self):
        """ Convert the evaluation report data to a dictionary """
        return {
            "label_pairs": [
                {
                    "UUID": p.get_uuid(),
                    "label_expert": str(p.get_label_expert()),
                    "label_classifier": str(p.get_label_classifier())
                }
                for p in (self.get_label_pairs() or [])
            ],
            "errors": self.get_errors(),
            "errors_max": self.get_errors_max(),
            "consecutive_errors": self.get_consecutive_errors(),
            "consecutive_errors_max": self.get_consecutive_errors_max(),
            "errors_threshold_satisfied": self.get_errors_threshold_satisfied(),
            "consecutive_errors_threshold_satisfied":
                self.get_consecutive_errors_threshold_satisfied()
        }

    def get_label_pairs(self) -> List[LabelPair]:
        """Gets label pairs"""
        return self._label_pairs

    def set_label_pairs(self, value: List[LabelPair]):
        """Sets label pairs"""
        self._label_pairs = value

    def get_errors(self) -> int:
        """Gets errors"""
        return self._errors

    def set_errors(self, value: int):
        """Sets errors"""
        self._errors = value

    def get_errors_max(self) -> int:
        """Gets maximum errors"""
        return self._errors_max

    def set_errors_max(self, value: int):
        """Sets maximum errors"""
        self._errors_max = value

    def get_consecutive_errors(self) -> int:
        """Gets consecutive errors"""
        return self._consecutive_errors

    def set_consecutive_errors(self, value: int):
        """Sets consecutive errors"""
        self._consecutive_errors = value

    def get_consecutive_errors_max(self) -> int:
        """Gets maximum consecutive errors"""
        return self._consecutive_errors_max

    def set_consecutive_errors_max(self, value: int):
        """Sets maximum consecutive errors"""
        self._consecutive_errors_max = value

    def get_errors_threshold_satisfied(self) -> bool:
        """Gets errors threshold satisfied"""
        return self._errors_threshold_satisfied

    def set_errors_threshold_satisfied(self, value: bool):
        """Sets errors threshold satisfied"""
        self._errors_threshold_satisfied = value

    def get_consecutive_errors_threshold_satisfied(self) -> bool:
        """Gets consecutive errors threshold satisfied"""
        return self._consecutive_errors_threshold_satisfied

    def set_consecutive_errors_threshold_satisfied(self, value: bool):
        """Sets consecutive errors threshold satisfied"""
        self._consecutive_errors_threshold_satisfied = value
