class LearningDataSet:
    _instance = {}

    @staticmethod
    def set_data(data):
        """
        Converts external JSON data (flat features + string labels)
        into the internal numerical format expected by the MLP classifier.
        """

        # Mapping: string labels → numeric
        label_map = {"none": 0, "overheating": 1, "electrical": 2}

        LearningDataSet._instance = {
            "training": {
                "data": {
                    "mean_current": [],
                    "mean_voltage": [],
                    "mean_temperature": [],
                    "mean_external_temperature": [],
                    "mean_external_humidity": [],
                    "mean_occupancy": []
                },
                "labels": [],
            },
            "validation": {
                "data": {
                    "mean_current": [],
                    "mean_voltage": [],
                    "mean_temperature": [],
                    "mean_external_temperature": [],
                    "mean_external_humidity": [],
                    "mean_occupancy": []
                },
                "labels": [],
            },
            "test": {
                "data": {
                    "mean_current": [],
                    "mean_voltage": [],
                    "mean_temperature": [],
                    "mean_external_temperature": [],
                    "mean_external_humidity": [],
                    "mean_occupancy": []
                },
                "labels": [],
            }
        }

        for phase in ["training", "validation", "test"]:
            if phase not in data:
                continue
            for record in data[phase]:
                f = record["features"]
                lbl = label_map.get(record["label"].lower(), -1)
                if lbl == -1:
                    print(f"[WARN] Unknown label '{record['label']}' — skipping entry.")
                    continue
                LearningDataSet._instance[phase]["data"]["mean_current"].append(f[0])
                LearningDataSet._instance[phase]["data"]["mean_voltage"].append(f[1])
                LearningDataSet._instance[phase]["data"]["mean_temperature"].append(f[2])
                LearningDataSet._instance[phase]["data"]["mean_external_temperature"].append(f[3])
                LearningDataSet._instance[phase]["data"]["mean_external_humidity"].append(f[4])
                LearningDataSet._instance[phase]["data"]["mean_occupancy"].append(f[5])
                LearningDataSet._instance[phase]["labels"].append(lbl)

        print("[INFO] External dataset successfully set.")

    @staticmethod
    def get_data(category):
        if category not in LearningDataSet._instance:
            raise KeyError(f"[ERROR] '{category}' data not found. Did you call set_data()?")

        return LearningDataSet._instance[category]
