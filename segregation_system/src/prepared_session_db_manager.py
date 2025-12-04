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

    def get_session_number(self):
        return self.prepared_session_counter

    def increment_session_counter(self):
        self.prepared_session_counter = self.prepared_session_counter + 1

    def reset_counter(self):
        self.prepared_session_counter = 0

    # TODO validation method for prepared sessions

    def store_prepared_session(self, prepared_session):

        # TODO Validate before storing session

        query = """
                INSERT INTO prepared_sessions (
                    session_id,
                    mean_current,
                    mean_voltage,
                    mean_temperature,
                    mean_external_temperature,
                    mean_external_humidity,
                    mean_occupancy,
                    label
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

        try:
            cur = self._conn.cursor()
            cur.execute(query, prepared_session)
            self._conn.commit()
        except Exception as e:
            print(f"[SEGREGATION SYSTEM] Error: unable to add session (session_id: {prepared_session['session_id']}: {e}")
            return []

        print(f"[SEGREGATION SYSTEM] Stored new prepared session (session_id: {prepared_session['session_id']}")

        self.increment_session_counter()

        return True

    def get_all_sessions(self):
        try:
            cur = self._conn.cursor()
            cur.execute("""
                SELECT session_id, mean_current, mean_voltage, mean_temperature,
                       mean_external_temperature, mean_external_humidity, mean_occupancy, label
                FROM prepared_sessions
            """)
            sessions = cur.fetchall()
            return sessions
        except Exception as e:
            print(f"[ERROR] Unable to fetch sessions: {e}")
            return []

    def clear_dataset(self):
        try:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM prepared_sessions")
            self._conn.commit()
            print("[INFO] Dataset successfully cleared.")
        except Exception as e:
            self._conn.rollback()
            print(f"[ERROR] Unable to clear the dataset: {e}")
