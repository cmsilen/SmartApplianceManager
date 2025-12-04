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


class IngestionSystemOrchestrator:

    def __init__(self):
        self.configuration_controller = None

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



        while True:
            time.sleep(1)
