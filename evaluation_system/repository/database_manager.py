""" Module for defining labels """
import os
import sys
import sqlite3
from evaluation_system.model.label import Label
from evaluation_system.model.label_pair import LabelPair
from evaluation_system.model.label_source import LabelSource
from evaluation_system.model.label_type import LabelType


class DatabaseManager:
    """ Class for defining labels """

    def __init__(self):

        # Database path
        db_path = os.path.expanduser('~/evaluation_db.db')

        # Connect with SQLite
        try:
            self._conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            print(f'[EVALUATION SYSTEM] SQL Connection Error [{e}]')
            sys.exit(1)

    def _run_query(self, query: str, params: tuple = None):
        """ Runs a query and returns the result """
        cursor = self._conn.cursor()

        try:
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self._conn.commit()
            return cursor
        except sqlite3.Error as e:
            print(f'[EVALUATION SYSTEM] Sqlite Execution Error [{e}]')
            return None

    def create_tables(self):
        """ Creates the tables """
        print("[EVALUATION SYSTEM] Creating tables")
        query = "CREATE TABLE if not exists labels" \
                "(uuid TEXT PRIMARY KEY UNIQUE, label_classifier TEXT, label_expert TEXT)"
        self._run_query(query)

    def clear_tables(self):
        """ Clears the tables """
        print("[EVALUATION SYSTEM] Clearing tables")
        query = "DROP TABLE IF EXISTS labels;"
        self._run_query(query)

    def get_complete_labels(self):
        """ Returns the complete labels as LabelPair instances"""
        query = "   SELECT * \
                    FROM labels \
                    WHERE label_classifier IS NOT NULL \
                        AND label_expert IS NOT NULL;"
        cursor  = self._run_query(query)

        # print labels
        rows = cursor.fetchall()
        for row in rows:
            print(row)

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

    def get_complete_labels_count(self):
        """ Returns the number of complete labels """
        query = "   SELECT COUNT(*) \
                    FROM labels \
                    WHERE label_classifier IS NOT NULL \
                        AND label_expert IS NOT NULL;"
        cursor = self._run_query(query)
        rows = cursor.fetchall()
        print(f"[EVALUATION SYSTEM] Complete label pairs: {rows[0][0]}")
        return rows[0][0]

    def get_total_record_count(self):
        """ Returns the number of complete labels """
        query = "   SELECT COUNT(*) \
                    FROM labels"
        cursor = self._run_query(query)
        rows = cursor.fetchall()

        return rows[0][0]

    def store_label(self, label: Label, label_source: LabelSource):
        """
        Stores a label.
        Creates a new record if UUID is not found, updates only if the field is NULL.
        """

        label_type = str(label.get_label_type())

        if label_source == LabelSource.CLASSIFIER:
            query = """
                INSERT INTO labels (uuid, label_classifier)
                VALUES (?, ?)
                ON CONFLICT(uuid) DO UPDATE SET
                    label_classifier = COALESCE(labels.label_classifier, excluded.label_classifier);
            """
            label_data = (label.get_uuid(), label_type)

        elif label_source == LabelSource.EXPERT:
            query = """
                INSERT INTO labels (uuid, label_expert)
                VALUES (?, ?)
                ON CONFLICT(uuid) DO UPDATE SET
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
