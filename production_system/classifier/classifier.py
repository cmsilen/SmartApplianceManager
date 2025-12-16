""" Module for defining the classifier """
import io
import os
import joblib
import pandas as pd

from production_system.model.label import Label
from production_system.model.label_type import LabelType
from production_system.model.prepared_session import PreparedSession


class Classifier:
    """ Class for managing the classifier """

    cols = [
        "mean_current",
        "mean_voltage",
        "mean_temperature",
        "mean_external_temperature",
        "mean_external_humidity",
        "mean_occupancy",
    ]

    def __init__(self):
        self.filename = None
        self.model = None

    def load_from_file(self, filename: str = "classifier.joblib"):
        """ Loads the classifier from a file """
        self.filename = filename

        working_dir = os.getcwd()
        full_path = os.path.join(working_dir, "classifier",filename)
        self.model = joblib.load(full_path)

    def load_from_bytes(self, raw_bytes: bytes):
        """ Loads the classifier from bytes """
        self.model = joblib.load(io.BytesIO(raw_bytes))

    def store(self, filename: str = "classifier.joblib"):
        """Store current model into a .joblib file inside the working directory."""

        if self.model is None:
            print("ERROR No model loaded, cannot store.")
            return

        working_dir = os.getcwd()
        full_path = os.path.join(working_dir, "classifier", filename)

        joblib.dump(self.model, full_path)

        self.filename = full_path


    def infer(self, prepared_session: PreparedSession):
        """Run inference."""

        if self.model is None:
            raise RuntimeError("Classifier model not loaded")

        features = prepared_session.to_tuple()
        data_frame = pd.DataFrame([features], columns=Classifier.cols)
        prediction = self.model.predict(data_frame)[0]

        return Label(
            uuid=prepared_session.get_uuid(),
            label_type=LabelType.from_string(str(prediction))
        )
