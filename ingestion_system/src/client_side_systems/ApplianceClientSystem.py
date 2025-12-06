import datetime
import time
import random
import pandas as pd

from ..records.ApplianceRecord import ApplianceRecord


class ApplianceClientSystem:
    """
    Simulates the Appliance Client Side System
    """

    def __init__(self, data_path: str):
        """
        Constructor
        :param data_path: str
        """
        self.df = pd.read_csv(data_path, sep=",")
        self.index = 0
        self.uuid = 0

    def get_record(self) -> ApplianceRecord:
        """
        Get the next record
        :return: ApplianceRecord
        """
        row = self.df.iloc[self.index]

        uuid = self.uuid
        self.uuid += 1
        self.index = (self.index + 1) % len(self.df)
        # simulate delay
        delay = random.uniform(1, 5)
        time.sleep(delay)
        data = self.simulate_missing_samples({
            "uuid": uuid,
            "timestamp": datetime.datetime.now().isoformat(),
            "current": row["current"],
            "voltage": row["voltage"],
            "temperature": row["temperature"],
            "appliance_type": row["appliance_type"]
        })
        record = ApplianceRecord()
        record.uuid = data["uuid"]
        record.timestamp = data["timestamp"]
        record.current = data["current"]
        record.voltage = data["voltage"]
        record.temperature = data["temperature"]
        record.appliance_type = data["appliance_type"]
        return record

    def simulate_missing_samples(self, record: dict) -> dict:
        """
        Simulate the missing samples randomly
        :param record:
        :return:
        """
        missing_probability = 0.05
        for key in record:
            if key == "uuid" or key == "timestamp":
                continue
            if random.uniform(0, 1) <= missing_probability:
                record[key] = None
        return record