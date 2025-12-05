from .Record import Record


class EnvironmentalRecord(Record):
    temperature: float
    humidity: float

    def __init__(self):
        super().__init__()
        self.temperature = None
        self.humidity = None

    def to_dict(self):
        return {
            "UUID": self.uuid,
            "timestamp": self.timestamp,
            "temperature": self.temperature,
            "humidity": self.humidity
        }