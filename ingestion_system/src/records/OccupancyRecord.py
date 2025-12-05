from .Record import Record


class OccupancyRecord(Record):
    occupancy: int

    def __init__(self):
        super().__init__()
        self.occupancy = None

    def to_dict(self):
        return {
            "UUID": self.uuid,
            "timestamp": self.timestamp,
            "occupancy": self.occupancy
        }