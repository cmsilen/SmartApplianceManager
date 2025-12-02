import json
from pathlib import Path
import time
from threading import Thread
from preparation_system.src.json_io import JsonIO


class PreparationSystem:

    def __init__(self):
        self.preparation_system_config = None

    def import_cfg(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.preparation_system_config = json.load(f)
        except FileNotFoundError:
            print(f"Error: file {file_path} does not exist.")
        except json.JSONDecodeError:
            print(f"Error: file {file_path} is not in JSON format.")

    def run(self):
        file_path = Path(__file__).parent.parent / "preparation_system_config.json"
        self.import_cfg(file_path)

        if self.preparation_system_config is None:
            raise ValueError("Configuration not imported. Call import_cfg(file_path) first.")

        print(f"[PREPARATION SYSTEM] Configuration loaded")

        jsonIO = JsonIO.get_instance()
        listener = Thread(target=jsonIO.listener,
                          args=(self.preparation_system_config["preparation_system"]["ip"],
                                self.preparation_system_config["preparation_system"]["port"]))
        listener.setDaemon(True)
        listener.start()

        while True:
            time.sleep(1)
