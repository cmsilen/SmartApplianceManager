""" Module for defining label source """
import enum

class LabelSource(enum.Enum):
    """ Class for defining label source """
    CLASSIFIER  = 1
    EXPERT      = 2

    def __str__(self):
        """ Returns the string representation """
        return self.name.lower()

    @staticmethod
    def from_string(s: str):
        """ Converts a string into a LabelSource """
        s = s.strip().upper()
        try:
            return LabelSource[s]
        except KeyError:
            raise ValueError(f"Invalid label source: {s}")
