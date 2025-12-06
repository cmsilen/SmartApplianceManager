import datetime
import random
import time
import pandas as pd

from ..records.OccupancyRecord import OccupancyRecord


class OccupancyClientSystem:
    """
    Simulates the Occupancy Client Side System
    """

    def __init__(self, data_path: str):
        """
        Constructor
        :param data_path: str
        """
        self.df = pd.read_csv(data_path, sep=",")
        self.index = 0
        self.uuid = 0

    def get_record(self) -> OccupancyRecord:
        """
        Get the next OccupancyRecord
        :return:
        """
        row = self.df.iloc[self.index]

        self.index = (self.index + 1) % len(self.df)
        uuid = self.uuid
        self.uuid += 1
        # simulate delay
        delay = random.uniform(1, 5)
        time.sleep(delay)
        data = self.simulate_missing_samples({
            "uuid": uuid,
            "timestamp": datetime.datetime.now().isoformat(),
            "occupancy": int(row["occupancy"])
        })
        record = OccupancyRecord()
        record.uuid = data["uuid"]
        record.timestamp = data["timestamp"]
        record.occupancy = data["occupancy"]
        return record

    def simulate_missing_samples(self, record: dict) -> dict:
        """
        Simulate missing samples randomly
        :param record: dict
        :return: dict
        """
        missing_probability = 0.01
        for key in record:
            if key == "uuid" or key == "timestamp":
                continue
            if random.uniform(0, 1) <= missing_probability:
                record[key] = None
        return record