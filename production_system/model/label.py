""" Module for defining labels """
import jsonschema
from production_system.model.label_type import LabelType


class Label:
    """ Class for managing labels """

    RECEIVED_LABEL_SCHEMA = {
        "type": "object",
        "properties": {
            "UUID": {"type": ["string", "number"]},
            "type": {"type": "string", "enum": ["none", "electrical", "overheating"]},
            "timestamp": {"type": "string"}  # optional
        },
        "required": ["UUID", "type"],
        "additionalProperties": False
    }

    def __init__(self, uuid, label_type):
        self._uuid = uuid
        self._label_type = label_type

    @staticmethod
    def from_json(data: dict)  -> "Label":
        """
        Creates a new label from the given JSON data.
        Performs a validation against the preset JSON schema (RECEIVED_LABEL_SCHEMA)
        """

        # Schema validation
        jsonschema.validate(instance=data, schema=Label.RECEIVED_LABEL_SCHEMA)

        # Mapping case-insensitive
        label_type_enum = LabelType.from_string(data["type"])

        return Label(
            uuid=data["UUID"],
            label_type=label_type_enum
        )

    def to_dict(self):
        """ Returns a dictionary representation of the label """
        return {
            "UUID": self._uuid,
            "label": str(self._label_type)
        }

    def get_label_type(self):
        """ Returns the label type """
        return self._label_type

    def get_uuid(self):
        """ Returns the UUID """
        return self._uuid
