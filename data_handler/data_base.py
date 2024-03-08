import sqlite3
from pathlib import Path
from typing import List
from abc import ABC


class AbstractDBHandler(ABC):
    """
    Generalized data base handler.

    Attributes
    ----------
    conn : :obj:`sqlite3.dbapi2.Connection`
        A 'Connection' object pointing to the data base.
    cur : :obj:`sqlite3.dbapi2.Cursor`
        A 'Cursor' object based on the previous connection.
    """

    def __init__(self, db_path: Path):
        """Set instance attributes."""
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

        # Check if db exists, if not set template.
        if not db_path.exists():
            self.cur.execute(self.db_template)

    def insert(self, table: str, values: str):
        """Insert values to table.

        Parameters
        ----------
        table : str
            The name of the table.
        values : str
            The values to be added.
        """        
        sql = f"INSERT INTO {table} VALUES {values}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def update(self, table: str, changes: str, condition: str):
        """Update the values of specific rows based on condition.

        Parameters
        ----------
        table : str
            The table name.
        changes : str
            The changes to make.
        condition : str
            The condition to filter rows.
        """
        sql = f"UPDATE {table} SET {changes} WHERE {condition}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def delete(self, table: str, conditions: str):
        """Delete rows based on a condition.

        Parameters
        ----------
        table : str
            The table name.
        conditions : str
            The conditions to filter out rows.
        """        
        sql = f"DELETE FROM {table} WHERE {conditions}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def select(self, what: str, table: str, additionals: str) -> List:
        """Select certain values to show.

        Parameters
        ----------
        what : str
            The columns to show.
        table : str
            The table name.
        additionals : str
            Conditions for filtering.

        Returns
        -------
        List
            The results from the filtering.
        """
        sql = f"SELECT {what} FROM {table} {additionals}"
        print(sql)
        result = self.cur.execute(sql).fetchall()
        return result


class DataLakeHandler(AbstractDBHandler):
    """Handler of database for raw data."""

    db_template = """
        CREATE TABLE MOTOR_READINGS (
            unix_time FLOAT NOT NULL PRIMARY KEY,
            date_time VARCHAR(30) NOT NULL,
            voltage FLOAT NOT NULL
        );
    """
