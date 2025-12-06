""" Module for defining label type """
import enum

class LabelType(enum.Enum):
    """ Class for defining label type """
    NONE        = 1
    OVERHEATING = 2
    ELECTRICAL  = 3

    def __str__(self):
        """ Returns the string representation """
        return self.name.lower()

    @staticmethod
    def from_string(s: str):
        """ Converts a string into a LabelSource """
        s = s.strip().upper()
        try:
            return LabelType[s]
        except KeyError:
            raise ValueError(f"Invalid label type: {s}")
