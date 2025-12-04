import datetime

import pandas as pd

class OccupancyClientSystem:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path, sep=",")
        self.index = 0
        self.uuid = 0

    def get_record(self):
        row = self.df.iloc[self.index]

        self.index = (self.index + 1) % len(self.df)
        uuid = self.uuid
        self.uuid += 1
        return {
            "uuid": uuid,
            "timestamp": datetime.datetime.now(),
            "people_number": row["occupancy"]
        }