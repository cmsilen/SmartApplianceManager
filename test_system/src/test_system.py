import json
from pathlib import Path
import time
from threading import Thread

from evaluation_system.model.label_source import LabelSource
from test_system.deployment import GET_IP
from test_system.src.json_io import JsonIO
import random
import uuid
import enum

# ----------------------------
# Enum LabelType
# ----------------------------
class LabelType(enum.Enum):
    NONE = 0
    OVERHEATING = 1
    ELECTRICAL = 2

    @staticmethod
    def from_string(s: str):
        try:
            return LabelType[s.strip().upper()]
        except KeyError:
            raise ValueError(f"Invalid LabelType: {s}")

class Label:
    LABEL_SCHEMA = {
        "type": "object",
        "properties": {
            "uuid": {"type": "string"},
            "type": {"type": "string", "enum": ["none", "classifier", "expert"]}
        },
        "required": ["uuid", "type"],
        "additionalProperties": False
    }

    def __init__(self, uuid: str, label_type: LabelType):
        self._uuid = uuid
        self._label_type = label_type

    def to_json(self):
        return {
            "uuid": self._uuid,
            "type": self._label_type.name.lower()
        }

class TestSystem:

    def __init__(self):
        self.ingestion_system_config = None

    def import_cfg(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.ingestion_system_config = json.load(f)
        except FileNotFoundError:
            print(f"Error: file {file_path} does not exist.")
        except json.JSONDecodeError:
            print(f"Error: file {file_path} is not in JSON format.")

    def start_listener(self):
        jsonIO = JsonIO.get_instance()
        listener = Thread(target=jsonIO.listener, args=(GET_IP(), 5100))

        listener.setDaemon(True)
        listener.start()



    def run(self):
        file_path = Path(__file__).parent.parent / "test_sys_config.json"
        self.import_cfg(file_path)
        self.start_listener()

        if self.ingestion_system_config is None:
            raise ValueError("Configuration not imported. Call import_cfg(file_path) first.")

        print(f"[TEST SYSTEM] Configuration loaded")

        last_cmd = "STOP"
        cmd = "x"

        types = [LabelType.NONE, LabelType.OVERHEATING, LabelType.ELECTRICAL]
        sources = [LabelSource.EXPERT, LabelSource.CLASSIFIER]

        while True:

            random_label = Label(
                uuid=str(uuid.uuid4()),
                label_type=random.choice(types)
            )
            random_source = str(random.choice(sources))
            try:
                if last_cmd == "STOP":
                    cmd = JsonIO.get_instance().receive(block=True, timeout=None)
                else:
                    cmd = JsonIO.get_instance().receive(block=True, timeout=1)

            except Exception as e:
                if e.__class__.__name__ == "Empty":
                    cmd = None
                else:
                    print(f"[TEST] Unexpected receive error: {e}")
                    cmd = None

            if cmd is not None:
                print(f"[TEST] Cmd received = {cmd}")

            if cmd in ("START", "STOP", "START_PAIRS"):
                last_cmd = cmd

            if last_cmd == "START":
                JsonIO.get_instance().send(
                    GET_IP(), 5006,
                    f"label/{random_source}",
                    random_label.to_json()
                )
                print(f"[TEST] {random_source} label sent")

            elif last_cmd == "START_PAIRS":
                # Coppia expert/classifier con stesso UUID
                shared_uuid = str(uuid.uuid4())

                expert_label = Label(uuid=shared_uuid, label_type=random.choice(types))
                classifier_label = Label(uuid=shared_uuid, label_type=random.choice(types))

                JsonIO.get_instance().send(
                    GET_IP(), 5006,
                    "label/expert",
                    expert_label.to_json()
                )
                print("[TEST] expert label sent")

                JsonIO.get_instance().send(
                    GET_IP(), 5006,
                    "label/classifier",
                    classifier_label.to_json()
                )
                print("[TEST] classifier label sent")
