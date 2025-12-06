from .Record import Record


class ExpertRecord(Record):
    """
    Record containing the label that the expert associated to a raw session
    """

    label: str
    """
    Label that the expert associated to a raw session
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.label = None

    def to_dict(self) -> dict:
        """
        Converts the record to a dictionary for easier serialization
        :return: dict
        """
        return {
            "UUID": self.uuid,
            "timestamp": self.timestamp,
            "label": self.label
        }