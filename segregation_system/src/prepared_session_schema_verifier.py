class PreparedSessionSchemaVerifier:
    REQUIRED_SCHEMA = {
        "UUID": int,
        "label": str,
        "mean_current": (int, float),
        "mean_voltage": (int, float),
        "mean_temperature": (int, float),
        "mean_external_temperature": (int, float),
        "mean_external_humidity": (int, float),
        "mean_occupancy": (int, float)
    }

    @classmethod
    def verify(cls, data: dict) -> bool:
        for field, expected_type in cls.REQUIRED_SCHEMA.items():
            if field not in data:
                raise ValueError(f"Missing field: '{field}'")

            if not isinstance(data[field], expected_type):
                raise ValueError(
                    f"Incorrect type for '{field}': "
                    f"Expected {expected_type}, found {type(data[field])}"
                )

        return True
