import json
from pathlib import Path
import time
from threading import Thread

from ingestion_system.src.RawSession import RawSession
from ingestion_system.src.client_side_systems.ApplianceClientSystem import ApplianceClientSystem
from ingestion_system.src.ConfigurationController import ConfigurationController
from ingestion_system.src.client_side_systems.EnvironmentalClientSystem import EnvironmentalClientSystem
from ingestion_system.src.client_side_systems.ExpertClientSystem import ExpertClientSystem
from ingestion_system.src.MessageController import MessageController
from ingestion_system.src.client_side_systems.OccupancyClientSystem import OccupancyClientSystem
from ingestion_system.src.RecordsBuffer import RecordsBuffer
from ingestion_system.src.messages.ExpertRecordMessage import ExpertRecordMessage
from ingestion_system.src.messages.RawSessionMessage import RawSessionMessage
from ingestion_system.src.records.ExpertRecord import ExpertRecord


class IngestionSystemOrchestrator:
    configuration_controller: ConfigurationController
    records_buffer: RecordsBuffer
    next_raw_session_uuid: int

    def __init__(self):
        self.configuration_controller = None
        self.records_buffer = None
        self.next_raw_session_uuid = 0

    def import_cfg(self, file_path):
        self.configuration_controller = ConfigurationController(file_path)
        try:
            self.configuration_controller.load_config()
        except FileNotFoundError:
            print(f"Error: file {file_path} does not exist.")
            self.configuration_controller = None
        except json.JSONDecodeError:
            self.configuration_controller = None
            print(f"Error: file {file_path} is not in JSON format.")

    def run(self):
        file_path = Path(__file__).parent.parent / "ingestion_system_config.json"
        self.import_cfg(file_path)

        if self.configuration_controller is None:
            raise ValueError("Configuration not imported. Call import_cfg(file_path) first.")

        print(f"[INGESTION SYSTEM] Configuration loaded")

        message_controller = MessageController.get_instance()
        self_address = self.configuration_controller.get_ingestion_system_address()
        listener = Thread(target=message_controller.listener,
                          args=(self_address["ip"], self_address["port"]))
        listener.setDaemon(True)
        listener.start()

        appliance_client = ApplianceClientSystem("data/appliance.csv")
        environmental_client = EnvironmentalClientSystem("data/environmental.csv")
        occupancy_client = OccupancyClientSystem("data/occupancy.csv")
        expert_client = ExpertClientSystem("data/expert.csv")
        evaluation_system_address = self.configuration_controller.get_evaluation_system_address()
        preparation_system_address = self.configuration_controller.get_preparation_system_address()
        period = self.configuration_controller.get_records_collection_period_seconds()
        threshold = self.configuration_controller.get_minimum_records()
        current_phase = self.configuration_controller.get_current_phase()
        self.records_buffer = RecordsBuffer()

        while True:
            while True:
                # records collection from client side systems
                self.records_buffer.store_record(appliance_client.get_record(), "appliance")
                print("[INFO] Received Appliance record")
                self.records_buffer.store_record(environmental_client.get_record(), "environmental")
                print("[INFO] Received Environmental record")
                self.records_buffer.store_record(occupancy_client.get_record(), "occupancy")
                print("[INFO] Received Occupancy record")
                if self.records_buffer.get_records_count() >= threshold:
                    break
                time.sleep(period)

            label_record = ExpertRecord()
            if current_phase == "development" or current_phase == "evaluation":
                rec = expert_client.get_record()
                label_record.uuid = rec.uuid
                label_record.timestamp = rec.timestamp
                label_record.label = rec.label
                print("[INFO] Received Label from expert")

            print("[INFO] Creating raw session...")
            # create raw session
            raw_session = self.create_raw_session(label_record)

            # remove records
            self.records_buffer.delete_records()

            # mark missing samples
            missing_samples = self.mark_missing_samples(raw_session)

            # raw session valid?
            if missing_samples >= threshold:
                print("[ERR] Invalid raw session, discarding...")
                continue

            # is evaluation phase?
            if current_phase == "evaluation" and label_record is not None:
                label_msg = ExpertRecordMessage()
                label_msg.dst_address = evaluation_system_address["ip"]
                label_msg.dst_port = evaluation_system_address["port"]
                label_msg.expert_record = label_record
                result = message_controller.send(label_msg, "receive/expert")
                if result:
                    print("[INFO] Sent label to evaluation system")
                else:
                    print("[ERR] Failed to send label to evaluation system")

            #print(json.dumps(raw_session, indent=4))
            raw_session_msg = RawSessionMessage()
            raw_session_msg.dst_address = preparation_system_address["ip"]
            raw_session_msg.dst_port = preparation_system_address["port"]
            raw_session_msg.raw_session = raw_session
            result = message_controller.send(raw_session_msg, "???")
            if result:
                print("[INFO] Sent Raw session to preparation system")
            else:
                print("[ERR] Failed to send Raw session to preparation system")


    def create_raw_session(self, label: ExpertRecord) -> RawSession:
        records = self.records_buffer.get_records()
        uuid = self.next_raw_session_uuid
        self.next_raw_session_uuid += 1

        raw_session = RawSession()
        raw_session.uuid = uuid
        raw_session.appliance_records = records["appliance"]
        raw_session.environmental_records = records["environmental"]
        raw_session.occupancy_records = records["occupancy"]
        raw_session.expert_record = label
        return raw_session

    def mark_missing_samples(self, raw_session: RawSession) -> int:
        missing_samples = 0
        records_types = [raw_session.appliance_records, raw_session.environmental_records, raw_session.occupancy_records]
        for records in records_types:
            for sample in records:
                if sample is None:
                    missing_samples += 1

        return missing_samples