import datetime

import pandas as pd

class ApplianceClientSystem:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path, sep=",")
        self.index = 0
        self.uuid = 0

    def get_record(self):
        row = self.df.iloc[self.index]

        uuid = self.uuid
        self.uuid += 1
        self.index = (self.index + 1) % len(self.df)
        return {
            "uuid": uuid,
            "timestamp": datetime.datetime.now(),
            "current": row["current"],
            "voltage": row["voltage"],
            "temperature": row["temperature"],
            "appliance_type": row["appliance_type"]
        }