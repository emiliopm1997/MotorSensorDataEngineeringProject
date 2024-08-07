import sqlite3
from abc import ABC
from pathlib import Path
from typing import List, Optional

import pandas as pd
from logger import LOGGER


class AbstractDBHandler(ABC):
    """
    Generalized data base handler.

    Attributes
    ----------
    db_type : str
        The of database one is dealing with.
    db_template : Union[List[str], str]
        The templates used to create the tables of the db.
    conn : :obj:`sqlite3.dbapi2.Connection`
        A 'Connection' object pointing to the data base.
    cur : :obj:`sqlite3.dbapi2.Cursor`
        A 'Cursor' object based on the previous connection.
    """

    db_type = ""
    db_template = []

    def __init__(self, db_path: Path, set_structure: Optional[bool] = False):
        """Set instance attributes."""
        db_exists = db_path.exists()

        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

        # Set templates if db doesn't exist.
        if (not db_exists) or set_structure:
            LOGGER.info(f"{self.db_type} doesn't exist. Setting tables...")
            if isinstance(self.db_template, str):
                self.db_template = [self.db_template]
            for table in self.db_template:
                self.cur.execute(table)
                self.conn.commit()
        else:
            LOGGER.info(f"{self.db_type} exists. Continuing...")

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

    def select(
        self, what: str, table: str, additionals: Optional[str] = ""
    ) -> List:
        """Select certain values to show.

        Parameters
        ----------
        what : str
            The columns to show.
        table : str
            The table name.
        additionals : Optional[str]
            Conditions for filtering. Empty if not passed.

        Returns
        -------
        List
            The results from the filtering.
        """
        sql = f"SELECT {what} FROM {table} {additionals}"
        print(sql)
        result = pd.read_sql_query(sql, self.conn)
        return result


class DataLakeHandler(AbstractDBHandler):
    """Handler of database for raw data."""

    db_type = "Data Lake"
    db_template = """
        CREATE TABLE MOTOR_VOLTAGE (
            unix_time FLOAT NOT NULL PRIMARY KEY,
            date_time VARCHAR(30) NOT NULL,
            voltage FLOAT NOT NULL
        );
    """


class DataWarehouseHandler(AbstractDBHandler):
    """Handler of database for processed data.

    Attributes
    ----------
    latest_cycle_time : float
        The latest time that has been used to cut a cycle.
    latest_cycle_id : int
        The latest id that has been used for a cut cycle.
    """

    db_type = "Data Warehouse"
    db_template = [
        """
            CREATE TABLE CYCLES (
                unix_time FLOAT NOT NULL PRIMARY KEY,
                date_time VARCHAR(30) NOT NULL,
                cycle_id INTEGER NOT NULL,
                voltage FLOAT NOT NULL
            );
        """,
        """
            CREATE TABLE METRICS (
                metric_id INTEGER NOT NULL PRIMARY KEY,
                cycle_id INTEGER NOT NULL,
                ref_unix_time FLOAT NOT NULL,
                ref_date_time VARCHAR(30) NOT NULL,
                metric_name VARCHAR(30) NOT NULL,
                metric_value FLOAT NOT NULL
            );

        """,
    ]

    @property
    def latest_cycle_time(self) -> float:
        """Get the last time value considered for the cycles."""
        additionals = "ORDER BY unix_time DESC LIMIT 1"
        data = self.select("unix_time", "CYCLES", additionals)
        if len(data) == 0:
            return None

        # The last method is so that it is stored in a native
        # Python type.
        return data.loc[0].values[0].item()

    @property
    def latest_cycle_id(self) -> int:
        """Get the last id value considered for the cycles."""
        additionals = "ORDER BY cycle_id DESC LIMIT 1"
        data = self.select("cycle_id", "CYCLES", additionals)
        if len(data) == 0:
            return None

        # The last method is so that it is stored in a native
        # Python type.
        return data.loc[0].values[0].item()
