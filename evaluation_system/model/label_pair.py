""" Module for defining label pairs """

from evaluation_system.model.label import Label
from evaluation_system.model.label_source import LabelSource

class LabelPair:
    """ Class for managing label pairs """

    def __init__(self, uuid, label_expert: Label, label_classifier: Label):
        self._uuid = uuid
        self._label_expert = label_expert.get_label_type()
        self._label_classifier = label_classifier.get_label_type()
