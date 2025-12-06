from .Record import Record


class ApplianceRecord(Record):
    """
    Record containing current, voltage, temperature relative to a certain appliance
    """

    current: float
    """
    Current of the appliance
    """

    voltage: float
    """
    Voltage of the appliance
    """

    temperature: float
    """
    Temperature of the appliance
    """

    appliance_type: str
    """
    Appliance type of the appliance
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.current = None
        self.voltage = None
        self.temperature = None
        self.appliance_type = None

    def to_dict(self) -> dict:
        """
        Converts the record to a dictionary for easier serialization
        :return: dict
        """
        return {
            "UUID": self.uuid,
            "timestamp": self.timestamp,
            "current": self.current,
            "voltage": self.voltage,
            "temperature": self.temperature,
            "appliance_type": self.appliance_type,
        }