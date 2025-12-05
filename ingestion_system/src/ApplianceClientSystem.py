import datetime
import time
import random
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
        # simulate delay
        delay = random.uniform(1, 5)
        time.sleep(delay)
        return self.simulate_missing_samples({
            "uuid": uuid,
            "timestamp": datetime.datetime.now().isoformat(),
            "current": row["current"],
            "voltage": row["voltage"],
            "temperature": row["temperature"],
            "appliance_type": row["appliance_type"]
        })

    def simulate_missing_samples(self, record):
        missing_probability = 0.05
        for key in record:
            if key == "uuid" or key == "timestamp":
                continue
            if random.uniform(0, 1) <= missing_probability:
                record[key] = None
        return record