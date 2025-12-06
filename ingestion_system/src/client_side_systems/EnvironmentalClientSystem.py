import datetime
import random
import time
import pandas as pd

from ..records.EnvironmentalRecord import EnvironmentalRecord


class EnvironmentalClientSystem:
    """
    Simulates the Environmental Client Side System
    """

    def __init__(self, data_path: str):
        """
        Constructor
        :param data_path: str
        """
        self.df = pd.read_csv(data_path, sep=",")
        self.index = 0
        self.uuid = 0

    def get_record(self) -> EnvironmentalRecord:
        """
        Get the next record
        :return: EnvironmentalRecord
        """
        row = self.df.iloc[self.index]

        self.index = (self.index + 1) % len(self.df)
        uuid = self.uuid
        self.uuid += 1
        # simulate delay
        delay = random.uniform(0, 2)
        time.sleep(delay)
        data = self.simulate_missing_samples({
            "uuid": uuid,
            "timestamp": datetime.datetime.now().isoformat(),
            "temperature": row["temperature"],
            "humidity": row["humidity"]
        })
        record = EnvironmentalRecord()
        record.uuid = data["uuid"]
        record.timestamp = data["timestamp"]
        record.temperature = data["temperature"]
        record.humidity = data["humidity"]
        return record


    def simulate_missing_samples(self, record: dict) -> dict:
        """
        Simulate missing samples randomly
        :param record: dict
        :return: dict
        """
        missing_probability = 0.05
        for key in record:
            if key == "uuid" or key == "timestamp":
                continue
            if random.uniform(0, 1) <= missing_probability:
                record[key] = None
        return record