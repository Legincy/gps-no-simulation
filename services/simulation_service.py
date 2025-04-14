import math
from typing import Dict, List, Optional

from models.station import Station


class SimulationService:
    def __init__(self, size_x: int, size_y: int, distance_scaling_factor: float):
        self._stations: List[Station] = []
        self._size_x = size_x
        self._size_y = size_y
        self._distance_scaling_factor = distance_scaling_factor

    def add_station(self, station: Station) -> None:
        self._stations.append(station)

    @property
    def anchors(self) -> List[Station]:
        return [s for s in self._stations if s.is_anchor()]

    @property
    def tags(self) -> List[Station]:
        return [s for s in self._stations if s.is_tag()]

    @property
    def stations(self) -> List[Station]:
        return self._stations

    @stations.setter
    def stations(self, stations: List[Station]) -> None:
        self._stations = stations

    def update_device_knowledge(self) -> None:
        for station in self._stations:
            others_stations = [
                s for s in self._stations if s.mac_address != station.mac_address
            ]
            station.cluster_stations = others_stations

    def calculate_distance(self, tag: Station, anchor: Station) -> Dict[str, float]:
        dx = tag.position["x"] - anchor.position["x"]
        dy = tag.position["y"] - anchor.position["y"]

        # Pythagorean theorem
        raw_distance = math.sqrt(dx**2 + dy**2)

        scaled_distance = raw_distance * self._distance_scaling_factor

        return {"raw_distance": raw_distance, "scaled_distance": scaled_distance}

    def update_tag_distances(self, tag: Station) -> None:
        if not tag.is_tag():
            return

        for anchor in self.anchors:
            distance_info = self.calculate_distance(tag, anchor)

            tag.add_distance_to_anchor(anchor, distance_info)

    def get_station_by_mac(self, mac_address: str) -> Optional[Station]:
        for station in self._stations:
            if station.mac_address == mac_address:
                return station
        return None

    def get_station_by_name(self, name: str) -> Optional[Station]:
        for station in self._stations:
            if station.name == name:
                return station
        return None
