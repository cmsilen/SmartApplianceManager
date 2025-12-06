from .Record import Record


class EnvironmentalRecord(Record):
    """
    Record containing temperature and humidity of the environment
    """

    temperature: float
    """
    Temperature of the environment
    """

    humidity: float
    """
    Humidity of the environment
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.temperature = None
        self.humidity = None

    def to_dict(self) -> dict:
        """
        Converts the record to a dictionary for easier serialization
        :return: dict
        """
        return {
            "UUID": self.uuid,
            "timestamp": self.timestamp,
            "temperature": self.temperature,
            "humidity": self.humidity
        }