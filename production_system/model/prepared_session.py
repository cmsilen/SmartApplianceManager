""" Module for defining a prepared session """
import jsonschema

class PreparedSession:
    """ Class for managing a prepared session """

    def __init__(self):
        self._uuid = None
        self._mean_current = None
        self._mean_voltage = None
        self._mean_temperature = None
        self._mean_external_temperature = None
        self._mean_external_humidity = None
        self._mean_occupancy = None

    PREPARED_SESSION_SCHEMA = {
        "type": "object",
        "properties": {
            "UUID": {"type": ["string", "number"]},
            "mean_current": {"type": "number"},
            "mean_voltage": {"type": "number"},
            "mean_temperature": {"type": "number"},
            "mean_external_temperature": {"type": "number"},
            "mean_external_humidity": {"type": "number"},
            "mean_occupancy": {"type": "number"},
            "session_id": {"type": "string"},  # optional
            "label": {"type": ["string", 'null']}  # optional
        },
        "required": [
            "UUID",
            "mean_current",
            "mean_voltage",
            "mean_temperature",
            "mean_external_temperature",
            "mean_external_humidity",
            "mean_occupancy"
        ],
        "additionalProperties": False
    }

    @staticmethod
    def from_json(data: dict)  -> "PreparedSession":
        """
        Creates a new prepared session from the given JSON data.
        Performs a validation against the preset JSON schema (PREPARED_SESSION_SCHEMA)
        """
        try:
            jsonschema.validate(instance=data, schema=PreparedSession.PREPARED_SESSION_SCHEMA)
        except jsonschema.exceptions.ValidationError as exc:
            raise jsonschema.exceptions.ValidationError(
                f"Invalid PreparedSession JSON\nSchema: \
                {PreparedSession.PREPARED_SESSION_SCHEMA};\nreceived: {data}"
            ) from exc


        prep_session = PreparedSession()
        prep_session.set_uuid(data["UUID"])
        prep_session.set_mean_current(data["mean_current"])
        prep_session.set_mean_voltage(data["mean_voltage"])
        prep_session.set_mean_temperature(data["mean_temperature"])
        prep_session.set_mean_external_temperature(data["mean_external_temperature"])
        prep_session.set_mean_external_humidity(data["mean_external_humidity"])
        prep_session.set_mean_occupancy(data["mean_occupancy"])

        return prep_session

    def to_tuple(self):
        """ Converts the prepared session to a tuple. Excludes the UUID """
        return (
            self._mean_current,
            self._mean_voltage,
            self._mean_temperature,
            self._mean_external_temperature,
            self._mean_external_humidity,
            self._mean_occupancy
        )

    def set_uuid(self, uuid):
        """ Sets the uuid """
        self._uuid = uuid

    def set_mean_current(self, mean_current):
        """ Sets the mean_current """
        self._mean_current = mean_current

    def set_mean_voltage(self, mean_voltage):
        """ Sets the mean_voltage """
        self._mean_voltage = mean_voltage

    def set_mean_temperature(self, mean_temperature):
        """ Sets the mean_temperature """
        self._mean_temperature = mean_temperature

    def set_mean_external_temperature(self, mean_external_temperature):
        """ Sets the mean_external_temperature """
        self._mean_external_temperature = mean_external_temperature

    def set_mean_external_humidity(self, mean_external_humidity):
        """ Sets the mean_external_humidity """
        self._mean_external_humidity = mean_external_humidity

    def set_mean_occupancy(self, mean_occupancy):
        """ Sets the mean_occupancy """
        self._mean_occupancy = mean_occupancy

    def get_uuid(self):
        """ Gets the UUID of the prepared session """
        return self._uuid
