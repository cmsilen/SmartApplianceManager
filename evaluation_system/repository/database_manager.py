""" Module for defining labels """
import os
import sys
import sqlite3
import threading
from typing import List

from evaluation_system.model.label import Label
from evaluation_system.model.label_pair import LabelPair
from evaluation_system.model.label_source import LabelSource
from evaluation_system.model.label_type import LabelType


class DatabaseManager:
    """ Class for defining labels """

    def __init__(self):

        # Database path
        db_path = os.path.expanduser('~/evaluation_db.db')
        self._lock = threading.Lock()

        # Connect with SQLite
        try:
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
        except sqlite3.Error as sql_exc:
            print(f'[EVALUATION SYSTEM] SQL Connection Error [{sql_exc}]')
            sys.exit(1)

    def _run_query(self, query: str, params: tuple = None):
        """ Runs a query and returns the result """
        with self._lock:
            cursor = self._conn.cursor()
            try:
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                self._conn.commit()
                return cursor
            except sqlite3.Error as sql_exc:
                print(f'[EVALUATION SYSTEM] Sqlite Execution Error [{sql_exc}]')
                return None

    # Table management

    def create_tables(self, clear_if_exists=True):
        """ Creates the tables """
        if clear_if_exists:
            self.clear_tables()

        query = "CREATE TABLE if not exists labels" \
                "(UUID TEXT PRIMARY KEY UNIQUE, label_classifier TEXT, label_expert TEXT)"
        self._run_query(query)

    def clear_tables(self):
        """ Clears the tables """
        query = "DROP TABLE IF EXISTS labels;"
        self._run_query(query)

    # Read operation

    def get_label_pairs(self, limit: int):
        """ Returns the complete labels as LabelPair instances"""
        query = "  SELECT * \
                    FROM labels \
                    WHERE label_classifier IS NOT NULL \
                        AND label_expert IS NOT NULL \
                    LIMIT ?"
        cursor  = self._run_query(query, (limit,))

        rows = cursor.fetchall()

        label_pairs = []
        for uuid, label_expert, label_classifier in rows:
            expert_label = Label(
                uuid=uuid,
                label_type=LabelType.from_string(label_expert)
            )
            classifier_label = Label(
                uuid=uuid,
                label_type=LabelType.from_string(label_classifier)
            )
            pair = LabelPair(uuid, expert_label, classifier_label)
            label_pairs.append(pair)

        return label_pairs

    def get_count_pairs(self):
        """ Returns the number of complete labels """
        query = "   SELECT COUNT(*) \
                    FROM labels \
                    WHERE label_classifier IS NOT NULL \
                        AND label_expert IS NOT NULL;"
        cursor = self._run_query(query)
        rows = cursor.fetchall()
        return rows[0][0]

    def get_count_all(self):
        """ Returns the number of complete labels """
        query = "   SELECT COUNT(*) \
                    FROM labels"
        cursor = self._run_query(query)
        rows = cursor.fetchall()

        return rows[0][0]

    # Create / Update records

    def store_label(self, label: Label, label_source: LabelSource):
        """
        Stores a label.
        Creates a new record if UUID is not found, updates only if the field is NULL.
        """

        label_type = str(label.get_label_type())

        if label_source == LabelSource.CLASSIFIER:
            query = """
                INSERT INTO labels (UUID, label_classifier)
                VALUES (?, ?)
                ON CONFLICT(UUID) DO UPDATE SET
                    label_classifier = COALESCE(labels.label_classifier, excluded.label_classifier);
            """
            label_data = (label.get_uuid(), label_type)

        elif label_source == LabelSource.EXPERT:
            query = """
                INSERT INTO labels (UUID, label_expert)
                VALUES (?, ?)
                ON CONFLICT(UUID) DO UPDATE SET
                    label_expert = COALESCE(labels.label_expert, excluded.label_expert);
            """
            label_data = (label.get_uuid(), label_type)

        else:
            raise ValueError("Invalid LabelSource")

        self._run_query(query, label_data)

    def store_label_json(self, label_json, label_source: LabelSource):
        """ Stores a label passed as json """

        # Create Label object
        # JSON schema check is included
        label = Label.from_json(label_json)

        # Stores label object
        self.store_label(label, label_source)

    # Delete operation

    def delete_label_pairs(self, label_pairs: List[LabelPair]):
        """ Delete label pairs"""

        if not label_pairs:
            return

        # List of uuids
        uuids = [pair.get_uuid() for pair in label_pairs]

        # values array
        placeholders = ",".join(["?"] * len(uuids))
        query = f"DELETE FROM labels WHERE UUID IN ({placeholders});"

        self._run_query(query, tuple(uuids))
