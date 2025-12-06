import datetime
import random
import time
import pandas as pd

from ..records.ExpertRecord import ExpertRecord


class ExpertClientSystem:
    """
    Simulates the Expert Client Side System
    """

    def __init__(self, data_path: str):
        """
        Constructor
        :param data_path: str
        """
        self.df = pd.read_csv(data_path, sep=",")
        self.index = 0
        self.uuid = 0

    def get_record(self) -> ExpertRecord:
        """
        Get the next expert record
        :return: ExpertRecord
        """
        row = self.df.iloc[self.index]

        self.index = (self.index + 1) % len(self.df)
        uuid = self.uuid
        self.uuid += 1
        # simulate delay
        delay = random.uniform(1, 5)
        time.sleep(delay)
        data = {
            "uuid": uuid,
            "timestamp": datetime.datetime.now().isoformat(),
            "label": row["label"]
        }
        record = ExpertRecord()
        record.uuid = data["uuid"]
        record.timestamp = data["timestamp"]
        record.label = data["label"]
        return record