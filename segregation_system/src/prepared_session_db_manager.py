import os
import sys
import sqlite3


class PreparedSessionStorage:

    def __init__(self):
        self.prepared_session_counter = 0
        db_path = os.path.expanduser('~/segregation_db.db')
        try:
            self._conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            print(f'[SEGREGATION SYSTEM] SQL Connection Error [{e}]')
            sys.exit(1)

        # init database
        cursor = self._conn.cursor()

        # prepared session table
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS prepared_session (
                    uuid INTEGER,
                    mean_current FLOAT,
                    mean_voltage FLOAT,
                    mean_temperature FLOAT,
                    mean_external_temperature FLOAT,
                    mean_external_humidity FLOAT,
                    mean_occupancy FLOAT,
                    label TEXT
                )
        """)
        self._conn.commit()

    def get_session_number(self):
        return self.prepared_session_counter

    def increment_session_counter(self):
        self.prepared_session_counter = self.prepared_session_counter + 1

    def reset_counter(self):
        self.prepared_session_counter = 0

    def store_prepared_session(self, prepared_session):

        query = """
                INSERT INTO prepared_session (
                    uuid,
                    mean_current,
                    mean_voltage,
                    mean_temperature,
                    mean_external_temperature,
                    mean_external_humidity,
                    mean_occupancy,
                    label
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """


        values = (
            prepared_session["UUID"],
            prepared_session["mean_current"],
            prepared_session["mean_voltage"],
            prepared_session["mean_temperature"],
            prepared_session["mean_external_temperature"],
            prepared_session["mean_external_humidity"],
            prepared_session["mean_occupancy"],
            prepared_session["label"]
        )

        try:
            cur = self._conn.cursor()
            cur.execute(query, values)
            self._conn.commit()
        except Exception as e:
            print(f"[SEGREGATION SYSTEM] Error: unable to add session "
                  f"(uuid: {prepared_session.get('UUID', 'UNKNOWN')}): {e}")
            return False

        print(f"[SEGREGATION SYSTEM] Stored new prepared session "
              f"(uuid: {prepared_session.get('UUID')})")

        self.increment_session_counter()

        return True

    def get_all_sessions(self):
        try:
            cur = self._conn.cursor()
            cur.execute("""
                SELECT uuid, mean_current, mean_voltage, mean_temperature,
                       mean_external_temperature, mean_external_humidity, mean_occupancy, label
                FROM prepared_session
            """)
            sessions = cur.fetchall()
            return sessions
        except Exception as e:
            print(f"[ERROR] Unable to fetch sessions: {e}")
            return []

    def clear_dataset(self):
        try:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM prepared_session")
            self._conn.commit()
            print("[INFO] Dataset successfully cleared.")
        except Exception as e:
            self._conn.rollback()
            print(f"[ERROR] Unable to clear the dataset: {e}")
