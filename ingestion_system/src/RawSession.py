from ingestion_system.src.records.ApplianceRecord import ApplianceRecord
from ingestion_system.src.records.EnvironmentalRecord import EnvironmentalRecord
from ingestion_system.src.records.ExpertRecord import ExpertRecord
from ingestion_system.src.records.OccupancyRecord import OccupancyRecord


class RawSession:
    uuid: int
    appliance_records: list[ApplianceRecord]
    environmental_records: list[EnvironmentalRecord]
    occupancy_records: list[OccupancyRecord]
    expert_record: ExpertRecord

    def __init__(self):
        self.uuid = None
        self.appliance_records = None
        self.environmental_records = None
        self.occupancy_records = None
        self.expert_record = None

    def to_dict(self):
        ret = {
            "UUID": self.uuid,
            "applianceRecords": [],
            "environmentalRecords": [],
            "occupancyRecords": [],
            "expertRecord": self.expert_record.to_dict()
        }

        for record in self.appliance_records:
            ret["applianceRecords"].append(record.to_dict())
        for record in self.environmental_records:
            ret["environmentalRecords"].append(record.to_dict())
        for record in self.occupancy_records:
            ret["occupancyRecords"].append(record.to_dict())

        return ret