from .Record import Record


class OccupancyRecord(Record):
    """
    Record containing the amount of people in the building at a certain time
    """

    occupancy: int
    """
    Amount of people in the building at a certain time
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.occupancy = None

    def to_dict(self) -> dict:
        """
        Converts the record to a dictionary for easier serialization
        :return:
        """
        return {
            "UUID": self.uuid,
            "timestamp": self.timestamp,
            "occupancy": self.occupancy
        }