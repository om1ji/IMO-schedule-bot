import sqlite3
from aiogram.types import User
from settings import db_name


class DB:
    def __init__(self, db_name: str):
        self._conn = sqlite3.connect(db_name)
        self._cursor = self._conn.cursor()

        users_table_query = """CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER,
                            gruppa TEXT,
                            UNIQUE(user_id)
                            )"""

        feedback_table_query = """CREATE TABLE IF NOT EXISTS feedback(
                            user_id INTEGER,
                            gruppa TEXT,
                            feedback TEXT,
                            user_data TEXT,
                            UNIQUE (user_id)
                            )"""

        self._cursor.execute(users_table_query)
        self._cursor.execute(feedback_table_query)
        self._conn.commit()

    def __del__(self):
        self._conn.commit()
        self._conn.close()

    def get_all_users(self) -> list:
        self._cursor.execute("SELECT user_id FROM users")
        return [item[0] for item in self._cursor.fetchall()]

    def insert_group(
        self, user_id: int, group: str
    ) -> None:
        query = "UPDATE users SET gruppa = ? WHERE user_id = ?"
        self._cursor.execute(query, (group, user_id))
        self._conn.commit()

    def get_group(self, user_id: int) -> str:
        query = "SELECT gruppa FROM users WHERE user_id = ?"
        self._cursor.execute(query, (user_id,))
        return self._cursor.fetchone()[0]

    def select_group(self, group: str) -> str:
        query = "SELECT gruppa FROM users WHERE group = ?"
        self._cursor.execute(query, (group,))
        result = self._cursor.fetchall()
        return result[0]

    def add_user(self, user: User):
        if user.id not in self.get_all_users():
            query = "INSERT INTO users VALUES (?, ?)"
            self._cursor.execute(query, (user.id, None))
            self._conn.commit()
            
    def get_users(self):
        query = "SELECT user_id FROM users"
        self._cursor.execute(query)
        result = self._cursor.fetchall()
        return [user_id[0] for user_id in result]

    def insert_feedback(self, user_id: int, group: str, feedback: str = None, user_data: str = None):
        if feedback is None:
            query = "INSERT INTO feedback VALUES (?, ?, ?, ?)"
            self._cursor.execute(query, (user_id, group, None, None))
        else:
            query = "UPDATE feedback SET feedback = ?, user_data = ? WHERE user_id = ?"
            self._cursor.execute(query, (feedback, user_data, user_id))

        self._conn.commit()


db = DB(db_name)
