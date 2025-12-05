""" Module for defining the evaluation report data """
from typing import List
from evaluation_system.model.label_pair import LabelPair

class EvaluationReportData:
    """Class for handling the evaluation report data"""

    def __init__(
        self,
        label_pairs: List[LabelPair] = None,
        errors: int = None,
        errors_max: int = None,
        consecutive_errors: int = None,
        consecutive_errors_max: int = None,
    ):
        self._label_pairs = label_pairs if label_pairs is not None else []
        self._errors = errors
        self._errors_max = errors_max
        self._consecutive_errors = consecutive_errors
        self._consecutive_errors_max = consecutive_errors_max

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
