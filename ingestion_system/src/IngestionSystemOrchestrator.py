import json
from pathlib import Path
import time
from threading import Thread

from ingestion_system.src.ApplianceClientSystem import ApplianceClientSystem
from ingestion_system.src.ConfigurationController import ConfigurationController
from ingestion_system.src.EnvironmentalClientSystem import EnvironmentalClientSystem
from ingestion_system.src.ExpertClientSystem import ExpertClientSystem
from ingestion_system.src.MessageController import MessageController
from ingestion_system.src.OccupancyClientSystem import OccupancyClientSystem
from ingestion_system.src.RecordsBuffer import RecordsBuffer


class IngestionSystemOrchestrator:

    def __init__(self):
        self.configuration_controller = None
        self.records_buffer = None

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
                print("[INGESTION SYSTEM] Received Appliance record")
                self.records_buffer.store_record(environmental_client.get_record(), "environmental")
                print("[INGESTION SYSTEM] Received Environmental record")
                self.records_buffer.store_record(occupancy_client.get_record(), "occupancy")
                print("[INGESTION SYSTEM] Received Occupancy record")
                if self.records_buffer.get_records_count() >= threshold:
                    break
                time.sleep(period)

            label_record = None
            if current_phase == "development" or current_phase == "evaluation":
                label_record = expert_client.get_record()
                print("[INGESTION SYSTEM] Received Label from expert")

            print("[INGESTION SYSTEM] Creating raw session...")
            # create raw session
            raw_session = self.create_raw_session()

            # remove records
            self.records_buffer.delete_records()

            # mark missing samples
            missing_samples = 0
            for key in raw_session:
                for sample in raw_session[key]:
                    if sample is None:
                        missing_samples += 1

            # raw session valid?
            if missing_samples >= threshold:
                continue

            # is evaluation phase?
            if current_phase == "evaluation":
                result = message_controller.send(evaluation_system_address["ip"], evaluation_system_address["port"], "???", label_record)
                if result:
                    print("[INGESTION SYSTEM] Sent label to evaluation system")
                else:
                    print("[INGESTION SYSTEM] Failed to send label to evaluation system")

            raw_session["label"] = label_record
            result = message_controller.send(preparation_system_address["ip"], preparation_system_address["port"], "???", raw_session)
            if result:
                print("[INGESTION SYSTEM] Sent Raw session to preparation system")
            else:
                print("[INGESTION SYSTEM] Failed to send Raw session to preparation system")





    def create_raw_session(self):
        return self.records_buffer.get_records()