import logging
import os
import sqlite3
from typing import List, Optional

from models.station import DeviceType, Station


class StorageService:

    def load_stations(self) -> List[Station]:
        raise NotImplementedError("This method must be implemented by a derived class")

    def save_stations(self, stations: List[Station]) -> None:
        raise NotImplementedError("This method must be implemented by a derived class")

    def update_station(self, station: Station) -> None:
        raise NotImplementedError("This method must be implemented by a derived class")


class SqliteStorage(StorageService):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_tables_if_not_exist()
        logging.info(f"Connected to database at {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        if not os.path.exists(os.path.dirname(os.path.abspath(self.db_path))):
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

        return sqlite3.connect(self.db_path)

    def _create_tables_if_not_exist(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS stations (
            mac_address TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            cluster_name TEXT,
            randomizer REAL NOT NULL,
            updated_at TEXT,
            created_at TEXT NOT NULL,
            position_x REAL,
            position_y REAL,
            target_x REAL,
            target_y REAL
        )
        """
        )

        conn.commit()
        conn.close()

    def _station_to_db_format(self, station: Station) -> tuple:
        position = station.position
        target_point = station.target_point

        return (
            station.mac_address,
            station.name,
            station.device_type_str,
            station.cluster_name,
            station.randomizer,
            station.updated_at,
            station.created_at,
            position["x"],
            position["y"],
            target_point["x"],
            target_point["y"],
        )

    def _db_to_station(self, row: tuple) -> Station:
        (
            mac_address,
            name,
            device_type_str,
            cluster_name,
            randomizer,
            updated_at,
            created_at,
            pos_x,
            pos_y,
            target_x,
            target_y,
        ) = row

        station = Station(
            mac_address=mac_address,
            name=name,
            device_type=device_type_str,
            position={"x": pos_x, "y": pos_y},
            target_point={"x": target_x, "y": target_y},
            randomizer=randomizer,
            cluster_name=cluster_name,
        )

        station.updated_at = updated_at
        station.created_at = created_at

        return station

    def load_stations_by_device_type(
        self, device_type: DeviceType, amount: Optional[int] = None
    ) -> List[Station]:
        conn = self._get_connection()
        cursor = conn.cursor()
        device_type_str = device_type.value

        try:
            query = "SELECT * FROM stations WHERE type = ? ORDER BY mac_address"
            params = [device_type_str]

            if amount is not None:
                query += " LIMIT ?"
                params.append(amount)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            devices = [self._db_to_station(row) for row in rows]

            if devices:
                logging.info(
                    f"Successfully loaded {len(devices)} {device_type}s from database"
                )

            return devices
        except Exception as e:
            logging.error(f"Error while loading {device_type_str}s from database: {e}")
            return []
        finally:
            conn.close()

    def load_stations(self) -> List[Station]:
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM stations")
            rows = cursor.fetchall()

            stations = []
            for row in rows:
                station = self._db_to_station(row)
                stations.append(station)

            if len(stations) > 0:
                logging.info(
                    f"Successfully loaded {len(stations)} stations from database"
                )

            return stations
        except Exception as e:
            logging.error(f"Error while loading stations from database: {e}")
            return []
        finally:
            conn.close()

    def save_stations(self, stations: List[Station]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            for station in stations:
                cursor.execute(
                    """
                INSERT OR REPLACE INTO stations 
                (mac_address, name, type, cluster_name, randomizer, updated_at, created_at, position_x, position_y, target_x, target_y)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    self._station_to_db_format(station),
                )

            conn.commit()
            logging.debug(f"Updated {len(stations)} stations in database")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error while saving stations to database: {e}")
        finally:
            conn.close()

    def update_station(self, station: Station) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
            INSERT OR REPLACE INTO stations 
            (mac_address, name, type, cluster_name, randomizer, updated_at, created_at, position_x, position_y, target_x, target_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                self._station_to_db_format(station),
            )

            conn.commit()
            logging.debug(f"Updated station {station.name} in database")
        except Exception as e:
            conn.rollback()
            logging.error(
                f"Error while updating station {station.name} in database: {e}"
            )
        finally:
            conn.close()


def get_storage_instance(storage_type: str, db_path: str, json_path: str) -> StorageService:
    if storage_type.lower() == "sqlite":
        return SqliteStorage(db_path)
    # elif storage_type.lower() == "json":
    #    return JsonStorage(json_path)
    else:
        raise ValueError(
            f"Unknown storage type: {storage_type}. Supported types are 'sqlite' and 'json'."
        )
