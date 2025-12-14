import os
from dotenv import load_dotenv
from pathlib import Path
from development_system.utility.json_read_write import JsonReadWrite


class CommunicationConfig:
    """
    Reads the system communication configuration file and
    returns IP and Port for the requested subsystem.
    """
    def __init__(self):
        # Path is stored in .env as COMMUNICATION_SYSTEM_CONFIG

        env_path = Path(__file__).resolve().parents[2] / "dev_sys.env"
        load_dotenv(env_path)
        config_path_from_root = os.getenv("COMMUNICATION_SYSTEM_CONFIG")
        config_path = Path(__file__).resolve().parents[2] / config_path_from_root


        read_result, file_content = JsonReadWrite.read_json_file(config_path)
        if not read_result or not file_content:
            raise FileNotFoundError(f"[ERROR] Unable to read communication config at: {file_content}")
        self._config = file_content

    def get_ip_port(self, system_name: str):
        """
        Given a subsystem name like 'evaluation_system'
        returns (ip, port) of that system
        """

        if system_name not in self._config:
            raise KeyError(f"[ERROR] System '{system_name}' not found in communication config.")

        system_info = self._config[system_name]
        ip = system_info.get("ip")
        port = system_info.get("port")

        if not ip or not port:
            raise ValueError(f"[ERROR] Invalid config for '{system_name}': missing ip or port.")
        return ip, port
