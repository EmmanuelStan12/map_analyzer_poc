from itertools import groupby
from operator import itemgetter


class State:
    states = []
    states_by_id = None
    states_by_code = None

    def __init__(self, sid=None, name=None, code=None):
        """
        Initialize a State object.

        Args:
            sid (int): State ID.
            name (str): State name.
            code (str): State code.
        """
        self.sid = sid
        self.name = name
        self.code = code

    @classmethod
    def from_db_row(cls, row):
        """
        Create a State object from a database row.

        Args:
            row (dict): Database row containing state data.

        Returns:
            State: Initialized State object.
        """
        return cls(
            sid=row['Id'],
            name=row['Name'],
            code=row['Code'],
        )

    @staticmethod
    def find_state_by_name(conn, name):
        """
        Find a state representing a certain name (name).

        Args:
            conn: Database connection object.
            name (str): name of the state.

        Returns:
            State: State object representing the name, or None if not found.
        """
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT *
            FROM State AS s
            WHERE s.Name = %s
            """

            cursor.execute(query, name)
            row = cursor.fetchone()
            if row:
                return State.from_db_row(row)
            else:
                print(f"No state has name ({name})")
                return None

        except Exception as e:
            print(f"Error finding state by name: {e}")
            return None

        finally:
            cursor.close()

    @staticmethod
    def find_state_by_code(conn, code):
        """
        Find a state that has the code (code).

        Args:
            conn: Database connection object.
            code (str): name of the state.

        Returns:
            State: State object representing the code, or None if not found.
        """
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT *
            FROM State AS s
            WHERE s.Code = %s
            """

            cursor.execute(query, code)
            row = cursor.fetchone()
            if row:
                return State.from_db_row(row)
            else:
                print(f"No state has code ({code})")
                return None

        except Exception as e:
            print(f"Error finding state by code: {e}")
            return None

        finally:
            cursor.close()

    @staticmethod
    def get_all_states(conn):
        """
        Get all states.

        Args:
            conn: Database connection object.

        Returns:
            list: List of all State objects.
        """
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT * FROM State
            """

            # Execute the query with the tuple of states
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                state = State.from_db_row(row)
                State.states.append(state)
            return State.states

        except Exception as e:
            print(f"Error finding states: {e}")
            return []

        finally:
            cursor.close()

    @staticmethod
    def get_states_by_code():
        if State.states_by_code is not None:
            return State.states_by_code
        _states = State.states.copy()

        # Then, use group by to group by the 'age' property
        grouped_states = {}
        for state in _states:
            grouped_states[state.code] = state
        State.states_by_code = grouped_states
        return grouped_states

    @staticmethod
    def get_states_by_id():
        if State.states_by_id is not None:
            return State.states_by_id
        _states = State.states.copy()

        grouped_states = {}
        for state in _states:
            grouped_states[state.sid] = state

        State.states_by_id = grouped_states
        return grouped_states

    def __getitem__(self, key):
        if key == 'code':
            return self.code
        elif key == 'name':
            return self.name
        elif key == 'id':
            return self.sid
        else:
            raise KeyError(f"Key {key} not found")
