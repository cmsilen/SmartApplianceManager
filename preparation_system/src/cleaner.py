import numpy as np


def _interpolate_list_of_values(values):
    ts = np.array(values, dtype=float)
    valid = ~np.isnan(ts)
    invalid = np.isnan(ts)

    if valid.sum() == 0:
        return ts.tolist()

    ts[invalid] = np.interp(
        x=np.flatnonzero(invalid),
        xp=np.flatnonzero(valid),
        fp=ts[valid]
    )
    return ts.tolist()


class Cleaner:
    def __init__(self, limits: dict):
        self.limits = limits

    def correct_missing_samples(self, session: dict):
        corrected = session.copy()

        if "applianceRecords" in corrected:
            for field in ["current", "voltage", "temperature"]:
                values = []
                for rec in corrected["applianceRecords"]:
                    v = rec.get(field)
                    values.append(np.nan if v is None else float(v))

                interpolated = _interpolate_list_of_values(values)

                for rec, new_val in zip(corrected["applianceRecords"], interpolated):
                    rec[field] = new_val

        if "environmentalRecords" in corrected:
            for field in ["temperature", "humidity"]:
                values = []
                for rec in corrected["environmentalRecords"]:
                    v = rec.get(field)
                    values.append(np.nan if v is None else float(v))

                interpolated = _interpolate_list_of_values(values)

                for rec, new_val in zip(corrected["environmentalRecords"], interpolated):
                    rec[field] = new_val

        if "occupancyRecords" in corrected:
            values = []
            for rec in corrected["occupancyRecords"]:
                v = rec.get("occupancy")
                values.append(np.nan if v is None else float(v))

            interpolated = _interpolate_list_of_values(values)

            for rec, new_val in zip(corrected["occupancyRecords"], interpolated):
                rec["occupancy"] = new_val

        return corrected

    def correct_outliers(self, session: dict):
        corrected = session.copy()

        def process_records(records, fields_mapping):
            for field_json_name, limit_key in fields_mapping.items():
                min_val = self.limits[limit_key]["min"]
                max_val = self.limits[limit_key]["max"]

                values = []
                for rec in records:
                    v = rec.get(field_json_name)
                    v = np.nan if v is None else float(v)
                    if np.isnan(v) or v < min_val or v > max_val:
                        v = np.nan
                    values.append(v)

                interpolated = _interpolate_list_of_values(values)

                for rec, new_val in zip(records, interpolated):
                    rec[field_json_name] = new_val

        if "applianceRecords" in corrected:
            process_records(
                corrected["applianceRecords"],
                {
                    "current": "current",
                    "voltage": "voltage",
                    "temperature": "temperature"
                }
            )

        if "environmentalRecords" in corrected:
            process_records(
                corrected["environmentalRecords"],
                {
                    "temperature": "ex_temperature",
                    "humidity": "humidity"
                }
            )

        if "occupancyRecords" in corrected:
            process_records(
                corrected["occupancyRecords"],
                {
                    "occupancy": "occupancy"
                }
            )

        return corrected
