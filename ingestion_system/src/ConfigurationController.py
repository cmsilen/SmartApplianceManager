import json

from pip._internal.exceptions import ConfigurationError


class ConfigurationController:
    """
    Provides the values contained in the configuration file
    """

    file_path: str
    """
    Path to the configuration file
    """

    current_config: dict
    """
    Json object of the configuration file
    """

    def __init__(self, file_path: str):
        """
        Constructor, it will read the specified configuration file
        :param file_path: str
        """

        self.file_path = file_path
        self.current_config = None

    def load_config(self):
        """
        Loads the configuration file
        :return: None
        """
        with open(self.file_path, 'r') as f:
            self.current_config = json.load(f)
        mandatory_fields = [
            "preparation_system",
            "ingestion_system",
            "evaluation_system",
            "currentPhase",
            "minimumRecords",
            "missingSamplesThreshold",
            "recordsCollectionPeriodSeconds",
            "preparationSystemEndpoint",
            "evaluationSystemEndpoint",
            "productionSessions",
            "evaluationSessions"
        ]
        for field in mandatory_fields:
            if field not in self.current_config:
                raise ConfigurationError(f"Missing mandatory field {field} in configuration file")

        fields_types = [
            dict,
            dict,
            dict,
            str,
            int,
            int,
            float,
            str,
            str,
            int,
            int
        ]
        for i in range(len(mandatory_fields)):
            if not isinstance(self.current_config[mandatory_fields[i]], fields_types[i]):
                raise ConfigurationError(f"Wrong type for field {mandatory_fields[i]} in configuration file, expected {fields_types[i]}")
            if fields_types[i] == dict and "port" not in self.current_config[mandatory_fields[i]] and "ip" not in self.current_config[mandatory_fields[i]]:
                raise ConfigurationError(f"Missing ip or field in field {mandatory_fields[i]} in configuration file")



    def get_ingestion_system_address(self) -> dict:
        """
        Gets the ingestion system address (ip and port)
        :return: dict
        """
        return self.current_config["ingestion_system"]

    def get_preparation_system_address(self) -> dict:
        """
        Gets the preparation system address (ip and port)
        :return: dict
        """
        return self.current_config["preparation_system"]

    def get_evaluation_system_address(self) -> dict:
        """
        Gets the evaluation system address (ip and port)
        :return: dict
        """
        return self.current_config["evaluation_system"]

    def get_current_phase(self) -> str:
        """
        Gets the current phase
        :return: str
        """
        return self.current_config["currentPhase"]

    def get_minimum_records(self) -> int:
        """
        Gets the minimum number of records to constitute a raw session
        :return: int
        """
        return self.current_config["minimumRecords"]

    def get_missing_samples_threshold(self) -> int:
        """
        Gets the number of samples missing from the raw session
        :return: int
        """
        return self.current_config["missingSamplesThreshold"]

    def get_records_collection_period_seconds(self) -> int:
        """
        Cooldown for the records collection period in seconds
        :return: int
        """
        return self.current_config["recordsCollectionPeriodSeconds"]

    def get_preparation_system_endpoint(self) -> str:
        """
        Gets the preparation system endpoint
        :return: str
        """
        return self.current_config["preparationSystemEndpoint"]

    def get_evaluation_system_endpoint(self) -> str:
        """
        Gets the evaluation system endpoint
        :return: str
        """
        return self.current_config["evaluationSystemEndpoint"]

    def get_production_sessions(self) -> int:
        """
        Gets the number of production sessions to complete before switching to evaluation phase
        :return: int
        """
        return self.current_config["productionSessions"]

    def get_evaluation_sessions(self) -> list:
        """
        Gets the number of evaluation sessions to complete before switching to production phase
        :return: int
        """
        return self.current_config["evaluationSessions"]

    def is_test(self):
        return self.current_config["test"]