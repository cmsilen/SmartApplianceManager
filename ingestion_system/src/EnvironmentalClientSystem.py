import datetime
import random
import time
import pandas as pd

class EnvironmentalClientSystem:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path, sep=",")
        self.index = 0
        self.uuid = 0

    def get_record(self):
        row = self.df.iloc[self.index]

        self.index = (self.index + 1) % len(self.df)
        uuid = self.uuid
        self.uuid += 1
        # simulate delay
        delay = random.uniform(0, 2)
        time.sleep(delay)
        return self.simulate_missing_samples({
            "uuid": uuid,
            "timestamp": datetime.datetime.now().isoformat(),
            "temperature": row["temperature"],
            "humidity": row["humidity"]
        })

    def simulate_missing_samples(self, record):
        missing_probability = 0.05
        for key in record:
            if key == "uuid" or key == "timestamp":
                continue
            if random.uniform(0, 1) <= missing_probability:
                record[key] = None
        return record