from .Record import Record


class ApplianceRecord(Record):
    current: float
    voltage: float
    temperature: float
    appliance_type: str

    def __init__(self):
        super().__init__()
        self.current = None
        self.voltage = None
        self.temperature = None
        self.appliance_type = None

    def to_dict(self):
        return {
            "UUID": self.uuid,
            "timestamp": self.timestamp,
            "current": self.current,
            "voltage": self.voltage,
            "temperature": self.temperature,
            "appliance_type": self.appliance_type,
        }